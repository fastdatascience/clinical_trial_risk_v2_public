import pathlib
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import numpy as np
from celery.signals import worker_process_init

from app.helpers import create_analysis_report_data_and_upload_to_storage, extract_logs_for_analysis_report
from app.models.document.document import Document
from app.models.document.repo import get_a_document_by_id
from app.models.user.base import User
from app.models.weight_profile.base import WeightProfileBase
from app.models.weight_profile.repo import get_a_weight_profile_for_user_or_default
from app.services.storage_provider import StorageProvider
from app.services.transform import transform_data_for_rac
from app.utils import get_file_extension, remove_file_extension

try:
    # * Try importing the package normally
    from clinicaltrials.core import ClassifierConfig, ClinicalTrial
    from clinicaltrials.core import Document as CTDocument
    from clinicaltrials.core import Page as CTPage
    from clinicaltrials.model_store import initialize_models
except ImportError:
    # * If it fails, append the local source directory to sys.path
    # * Use packaged core lib or installed through package manager
    import sys

    this_folder = pathlib.Path(__file__).parent.resolve()
    sys.path.append(f"{this_folder}/../clinical_trials_core/src")

    from clinicaltrials.core import ClassifierConfig, ClinicalTrial
    from clinicaltrials.core import Document as CTDocument
    from clinicaltrials.core import Page as CTPage
    from clinicaltrials.model_store import initialize_models

from redis import Redis
from sqlmodel import Session as SQLModelSession
from sqlmodel import or_, select

from app import config
from app.celery_config import celery
from app.database import engine
from app.grpc_client.document_parser import process_document
from app.grpc_client.document_parser.DocumentParser_pb2 import DocumentParserResponse
from app.log_config import logger
from app.models.user.user_resource_usage import UserResourceUsage, UserResourceUsageStatus
from app.models.vm import DocumentQueueItem

redis = Redis.from_url(config.REDIS_ENDPOINT)


@contextmanager
def session_scope():
    session = SQLModelSession(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def map_document_parser_response_to_ct_document(data: DocumentParserResponse) -> CTDocument:
    pages_list = [CTPage(page_number=key, content=value) for key, value in data.pages.items()]

    metadata = data.metadata if isinstance(data.metadata, dict) else None

    return CTDocument(pages=pages_list, metadata=metadata)


def transform_keys(data: dict):
    transformed_dict = {}
    for key, value in data.items():
        new_key = key.replace(" ", "_").lower()
        if isinstance(value, dict):
            value = transform_keys(value)  # noqa: PLW2901

        transformed_dict[new_key] = convert_set_to_list(value)

    return transformed_dict


def convert_int64_to_float(data: dict | list | int | float | np.integer) -> Any:
    """
    Recursively walk through the data (dict or list),
    and convert all numpy int64 values to float.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = convert_int64_to_float(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = convert_int64_to_float(item)
    elif isinstance(data, int | np.integer):
        return float(data)
    return data


def convert_set_to_list(object: dict | list | set | Any) -> dict[Any, Any] | list[Any]:
    if isinstance(object, dict):
        return {key: convert_set_to_list(value) for key, value in object.items()}
    if isinstance(object, list):
        return [convert_set_to_list(item) for item in object]
    if isinstance(object, set):
        return list(object)

    return object


@worker_process_init.connect
def at_start(sender=None, **kwargs):
    logger.info("Loading models...")
    initialize_models(path_to_classifier=ClassifierConfig().classifier_storage_path)


@celery.task
def reconcile_document_processing():
    """
    Runs every 10 minutes (check top level celery config object) and reconcile document run processes that are older than 10 minutes,
    assume the runs have failed if status is not COMPLETE
    """
    logger.info("Running document processing reconcile...")
    time_threshold = datetime.now(UTC) - timedelta(minutes=10)

    with session_scope() as session:
        results = session.exec(
            select(UserResourceUsage).where(
                UserResourceUsage.start_time < time_threshold,
                or_(UserResourceUsage.end_time == None),
            )
        ).all()

        logger.info(f"Found {len(results)} failed document run process")

        for result in results:
            result.status = UserResourceUsageStatus.FAILED
            result.end_time = datetime.now(UTC)
            result.result = None

            session.add(result)

        session.commit()


@celery.task
def init_document_process(document_dict: dict):
    document = DocumentQueueItem(**document_dict)
    logger.info(f"Starting document process {document.document_id}::{document.user_id}")

    with session_scope() as session:
        # * Update user resource usage record
        user_resource_usage = cast(
            UserResourceUsage,
            session.exec(select(UserResourceUsage).where(UserResourceUsage.resource_id == document.document_id)).first(),
        )

        user_resource_usage.status = UserResourceUsageStatus.IN_PROGRESS
        session.add(user_resource_usage)
        session.commit()
        session.refresh(user_resource_usage)

        storage_client = StorageProvider()

        file_contents: bytes = storage_client.get_file(file_name=document.resource_url)

        # * Parse the pdf, call tika and get the parsed document back
        parsed_document = process_document(file_contents=file_contents)

        ct = ClinicalTrial()

        # * Add event listener
        redis_list_key = f"run_log:{document.document_id}"
        redis_progress_key = f"run_log:{document.document_id}_completion"

        ct.event.subscribe(
            lambda event_data: (
                redis.lpush(redis_list_key, event_data.data) if event_data.type == "message" else redis.set(redis_progress_key, event_data.data),
                None,
            )[1]
        )

        # * Expire in 10 minutes
        redis.expire(name=f"run_log:{document.document_id}", time=600)

        ct_document = map_document_parser_response_to_ct_document(data=parsed_document)
        ct_document.extract_tables(file_buffer=file_contents)

        # todo get allowed modules, conditionally run modules, get modules from user_module and subscription_module
        user_resource_usage_result = ct.run_all(document=ct_document, parallel=True, file_buffer=file_contents)

        # * Transform the result just in case
        user_resource_usage_result = transform_keys(data=user_resource_usage_result)

        user_resource_usage.status = UserResourceUsageStatus.COMPLETED
        user_resource_usage.end_time = datetime.now(UTC)

        # * Convert any int64 to float
        user_resource_usage_result = cast(dict, convert_int64_to_float(user_resource_usage_result))

        user_resource_usage.result = user_resource_usage_result
        session.add(user_resource_usage)
        session.commit()
        session.refresh(user_resource_usage)

        logger.info(f"Annotating document {document.document_id}::{document.user_id}")

        # * Annotate pdf and save it to storage
        annotated_pdf = None
        if hasattr(CTDocument, "add_document_highlights") and callable(CTDocument.add_document_highlights):
            annotated_pdf = CTDocument.add_document_highlights(pdf_buffer=file_contents, document=ct_document)

        if annotated_pdf is not None:
            modified_resource_url = f"{remove_file_extension(document.resource_url)}_annotated.{get_file_extension(document.resource_url)}"

            storage_client.put_file(file_name=modified_resource_url, data=annotated_pdf)
        else:
            logger.error(f"Error annotating document {document.document_id}::{document.user_id}")

        process_time = (user_resource_usage.end_time - user_resource_usage.start_time).total_seconds()

        # Get db user
        db_user = cast(
            User,
            session.exec(select(User).where(User.id == document.user_id)).first(),
        )

        # Get db document
        db_document = get_a_document_by_id(session=session, user=db_user, document_id=document.document_id)

        if db_user and db_document:
            # Get weight profile
            weight_profile = get_a_weight_profile_for_user_or_default(session=session, user=db_user)

            # Get CT nodes
            ct_cost_nodes, ct_risk_nodes = transform_data_for_rac(
                metadata=ct.metadata,
                result=user_resource_usage.result,
                module_weight=weight_profile,
                selected_param={},
            )

            logger.info(f"The NLP analysis ran in {process_time} seconds.")

            # Analysis report Logs
            analysis_report_logs = extract_logs_for_analysis_report(
                parsed_document_metadata=dict(parsed_document.metadata),
                user_resource_usage_result=user_resource_usage_result,
            )

            # Create analysis report data and upload it to storage
            try:
                create_analysis_report_data_and_upload_to_storage(
                    db_user=db_user,
                    db_document=db_document,
                    ct_cost_nodes=ct_cost_nodes,
                    ct_risk_nodes=ct_risk_nodes,
                    user_resource_usage_result=user_resource_usage.result,
                    tokenised_pages=ct_document.tokenised_pages,
                    weight_profile=weight_profile,
                    storage_client=storage_client,
                    weights=WeightProfileBase(**weight_profile.weights),
                    session=session,
                    logs=analysis_report_logs,
                    analysis_run_time=process_time,
                )
            except Exception:
                logger.exception(f"Could not create analysis report data for document {db_document.id}.")
