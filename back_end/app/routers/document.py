import asyncio
import io
import json
import mimetypes
from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime
from typing import cast
from uuid import uuid4

import orjson
from clinicaltrials.core import Metadata as ClinicalTrialMetadata
from fastapi import APIRouter, Depends, File, Header, Query, UploadFile
from fastapi.responses import Response, StreamingResponse
from redis.asyncio import Redis as RedisAsync
from sqlmodel import Session, col, func, select

from app.config import BUCKET_OR_CONTAINER_NAME, CDN_BUCKET_OR_CONTAINER_BASE_PATH, MAX_DEMO_ACCOUNT_FILE_PROCESSING_COUNT
from app.ct_core import init_document_process, map_document_parser_response_to_ct_document
from app.database import paginate
from app.grpc_client.document_parser import process_document
from app.helpers import (
    create_analysis_report_data_and_upload_to_storage,
    extract_logs_for_analysis_report,
    get_user_analysis_report_data_storage_keys,
    get_user_documents_storage_keys,
)
from app.log_config import logger
from app.models.analysis_report.analysis_report import AnalysisReport
from app.models.document.document import Document
from app.models.document.repo import get_all_template_documents
from app.models.server_response import ServerResponse
from app.models.subscription.subscription_attribute import SubscriptionAttribute
from app.models.subscription.subscription_type import SubscriptionType
from app.models.user.base import User, UserWithRoles
from app.models.user.repo import get_user_resource_usage_in_resource_ids
from app.models.user.role import RoleEnum
from app.models.user.user_resource_usage import ResourceType, ResourceTypeName, UserResourceUsage, UserResourceUsageStatus
from app.models.user.user_subscription import UserSubscription
from app.models.vm import DocumentQueueItem
from app.models.weight_profile.base import DocumentRunWeightProfile, WeightProfileBase
from app.models.weight_profile.repo import get_a_weight_profile_for_user_by_id_or_default, get_a_weight_profile_for_user_or_default, get_default_weight_profiles
from app.resources import (
    create_or_update_tag_counter,
    dep_get_user_document_by_id,
    dep_get_user_resource_usage_by_document_id,
    get_ct_core_metadata_list,
    get_db,
    get_redis_async,
    get_storage_provider,
    get_user_with_roles,
    is_demo_account,
)
from app.schemas import AnalysisReportData as AnalysisReportDataSchema
from app.security import decode_sha256
from app.services import PdfGenerator
from app.services.pdf_generator.pdf_generator import PDF_GENERATOR_AVAILABLE, WKHTMLTOPDF_IO_ERROR_MESSAGE
from app.services.storage_provider import StorageProvider
from app.services.transform import get_total_trial_cost, get_trial_risk_score, transform_data_for_rac
from app.utils import create_analysis_report_file_storage_key, remove_file_extension

router = APIRouter()


ALLOWED_MIME_TYPES = ["application/pdf"]


@router.get(path="")
async def get_documents(
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
    metadata=Depends(get_ct_core_metadata_list),
    storage_client: StorageProvider = Depends(get_storage_provider),
    page: int = 1,
    page_size: int = 20,
    weight_profile_id: int | None = Query(default=None, alias="wp"),
):
    paginated_documents = paginate(
        session=session, query=select(Document).where(Document.user_id == user.user.id).order_by(col(Document.id).desc()), page=page, page_size=page_size
    )

    document_ids = [document.id for document in paginated_documents.contents]
    user_resource_usages = get_user_resource_usage_in_resource_ids(session=session, user=user.user, resource_ids=document_ids)
    usage_dict: dict[int, UserResourceUsage] = {usage.resource_id: usage for usage in user_resource_usages if usage.resource_id is not None}

    weight_profile = get_a_weight_profile_for_user_by_id_or_default(session=session, user=user.user, weight_profile_id=weight_profile_id)

    document_buffer = []
    for document in paginated_documents.contents:
        user_resource_usage = usage_dict.get(document.id)
        if user_resource_usage is None or user_resource_usage.result is None:
            document_buffer.append(
                {
                    **document.dict(),
                    "cdn_path": storage_client.get_internal_cdn_url(user_id=user.user.id, object_id=document.id),
                    "cost": {"total_cost": None, "total_cost_per_participant": None},
                    "trial_risk_score": None,
                }
            )
            continue

        cost_nodes, risk_nodes = transform_data_for_rac(metadata=metadata, result=user_resource_usage.result, module_weight=weight_profile, selected_param={})
        total_cost, total_cost_per_participant = get_total_trial_cost(ct_nodes=cost_nodes, module_weight=weight_profile)
        trial_risk_score_numeric, trial_risk_level = get_trial_risk_score(ct_node=risk_nodes, module_weight=weight_profile)

        document_buffer.append(
            {
                **document.dict(),
                "cdn_path": storage_client.get_internal_cdn_url(user_id=user.user.id, object_id=document.id),
                "cost": {"total_cost": total_cost, "total_cost_per_participant": total_cost_per_participant},
                "trial_risk_score": trial_risk_level,
                "trial_risk_score_numeric": trial_risk_score_numeric,
                "weight_profile": weight_profile.model_dump(exclude={"weights"}),
            }
        )

    paginated_documents.contents = document_buffer

    return ServerResponse(data=paginated_documents.to_dict())


@router.get(path="/{document_id}")
async def get_a_document(
    document_id: int,
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
    storage_client: StorageProvider = Depends(get_storage_provider),
):
    logger.info(f"Delete document request from {user.user.id}::{user.user.email} document id {document_id}")
    document = session.exec(select(Document).where(Document.id == document_id, Document.user_id == user.user.id)).first()

    if document is None:
        return ServerResponse(error="Document not found", status_code=404)

    return ServerResponse(
        data={
            **document.model_dump(),
            "cdn_path": storage_client.get_internal_cdn_url(user_id=user.user.id, object_id=document.id),
        }
    )


@router.post(path="")
async def upload_document(
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER, RoleEnum.GUEST])),
    session: Session = Depends(get_db),
    storage_client: StorageProvider = Depends(get_storage_provider),
    redis: RedisAsync = Depends(get_redis_async),
    document: UploadFile = File(),
    demo_account: bool = Depends(is_demo_account),
    x_tag: str | None = Header(alias="X-Tag", default=None),
):
    logger.info(f"Upload request from {user.user.id}::{user.user.email}")

    # * Ensure it's an image file with a valid MIME type
    if document.content_type not in ALLOWED_MIME_TYPES:
        allowed_file_type = ", ".join([file_type_ext.split("/").pop() for file_type_ext in ALLOWED_MIME_TYPES])
        return ServerResponse(status_code=400, error="Invalid file type. Please upload a valid document", errors=[f"Allowed documents are {allowed_file_type}"])

    # * Get subscription attributes for this user
    user_subscription_result: tuple[UserSubscription, SubscriptionType, SubscriptionAttribute] | None = session.exec(
        select(UserSubscription, SubscriptionType, SubscriptionAttribute)
        .join(SubscriptionType, col(UserSubscription.subscription_type_id) == SubscriptionType.id)
        .join(SubscriptionAttribute, col(SubscriptionAttribute.subscription_type_id) == SubscriptionType.id)
        .filter(col(UserSubscription.user_id) == user.user.id)
        .order_by(col(UserSubscription.id).desc())
    ).first()

    if user_subscription_result is None:
        return ServerResponse(error="No subscription found", status_code=403)

    _, subscription_type, subscription_attribute = user_subscription_result
    user_resource_identifier = cast(User, session.query(User).where(col(User.id) == user.user.id).first()).user_resource_identifier

    if not demo_account:
        # * Check if daily processing cap is hit only for non guest accounts
        user_resource_usage_count = session.exec(
            select(func.count()).where(UserResourceUsage.user_id == user.user.id).where(func.date(UserResourceUsage.start_time) == date.today())
        ).first()
        resource_usage_count_today = user_resource_usage_count if user_resource_usage_count else 0

        if resource_usage_count_today >= subscription_attribute.file_processing_limit:
            return ServerResponse(error="File processing limit reached", status_code=429)
    else:
        # * Check resource usage using the tag for demo account
        _, tag_count = await create_or_update_tag_counter(redis=redis, x_tag=x_tag)
        if tag_count >= MAX_DEMO_ACCOUNT_FILE_PROCESSING_COUNT:
            return ServerResponse(error="File processing limit reached", errors=["Upgrade plan for higher processing limit"], status_code=429)

    # * Check the file size
    file_contents = await document.read()

    file_size_limit_in_bytes = subscription_attribute.file_size * 1024 * 1024

    logger.info(f"Processing file with size {file_size_limit_in_bytes} bytes")

    if len(file_contents) > file_size_limit_in_bytes:
        return ServerResponse(
            status_code=413,
            error=f"Document size cannot exceed {subscription_attribute.file_size}MBs",
            errors=[f"{subscription_type.name} maximum upload size is {subscription_attribute.file_size}MBs"],
        )

    # * Upload file to storage
    file_uuid = uuid4()
    document_name = f"{file_uuid}_{document.filename.replace(' ', '_')}" if document.filename else str(file_uuid)
    logger.info(f"Uploading document for {user.user.id}::{user.user.email}. Document name {document_name}::{file_uuid}")

    upload_path = f"{CDN_BUCKET_OR_CONTAINER_BASE_PATH}/documents/{user_resource_identifier}/{document_name}"

    storage_client.put_file(file_name=upload_path, data=file_contents, content_type=document.content_type)

    logger.info(f"Uploaded document for {user.user.id}::{user.user.email}. Document name {document_name}::{file_uuid}")

    document_record = Document(
        original_document_name=document.filename if document.filename is not None else document_name,
        system_assigned_name=document_name,
        document_size=len(file_contents),
        document_type=document.content_type,
        user_id=user.user.id,  # type: ignore
    )

    resource_type = cast(ResourceType, session.exec(select(ResourceType).where(ResourceType.name == ResourceTypeName.FILE_PROCESS.value)).first())

    session.add(document_record)
    session.commit()
    session.refresh(document_record)

    session.add(
        UserResourceUsage(
            user_id=cast(int, user.user.id),
            status=UserResourceUsageStatus.QUEUED,
            resource_type_id=cast(int, resource_type.id),
            resource_id=document_record.id,
            start_time=datetime.now(UTC),
        )
    )

    # * Add default document weight profile
    # * Get default weight profile, Should always be present as a part of startup sequence
    default_weight_profile = get_default_weight_profiles(session=session)
    session.add(DocumentRunWeightProfile(document_id=cast(int, document_record.id), weights=default_weight_profile.weights))

    session.commit()

    if user.user.id is not None and document_record.id is not None:
        init_document_process.delay(  # type: ignore
            DocumentQueueItem(
                s3_bucket_name=BUCKET_OR_CONTAINER_NAME,
                resource_url=upload_path,
                user_id=user.user.id,
                document_id=document_record.id,
                user_resource_identifier=user_resource_identifier,
            ).model_dump()
        )

    return ServerResponse(data={**document_record.model_dump()})


@router.delete(path="/{document_id}")
async def delete_a_document(
    document_id: int,
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
    storage_client: StorageProvider = Depends(get_storage_provider),
):
    logger.info(f"Delete document request from {user.user.id}::{user.user.email} document id {document_id}")
    document = session.exec(select(Document).where(Document.id == document_id, Document.user_id == user.user.id)).first()

    if document is None:
        return ServerResponse(error="Document not found", status_code=404)

    db_user = cast(User, session.exec(select(User).where(User.id == user.user.id)).first())

    db_analysis_report = cast(AnalysisReport | None, session.exec(select(AnalysisReport).where(AnalysisReport.document_id == document_id)).first())

    # * Delete analysis report and document from storage
    all_files_to_delete: list[str] = []
    if db_analysis_report:
        analysis_report_files_to_delete = get_user_analysis_report_data_storage_keys(
            session=session,
            user=db_user,
            document_ids=[document.id],
        )
        if analysis_report_files_to_delete:
            all_files_to_delete.extend(analysis_report_files_to_delete)
    document_files_to_delete = get_user_documents_storage_keys(
        session=session,
        user=db_user,
        document_ids=[document.id],
        included_annotated_documents=True,
    )
    if document_files_to_delete:
        all_files_to_delete.extend(document_files_to_delete)
    if all_files_to_delete:
        storage_client.delete_files(file_names=all_files_to_delete)

    # * Delete document from db
    # * All data associated to this document via a foreign key will be deleted
    session.delete(document)

    # * Commit
    session.commit()

    return ServerResponse(status_code=204)


@router.get(path="/{document_id}/run-status")
async def get_document_process_run_status(
    document_id: int,
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER, RoleEnum.GUEST])),
    session: Session = Depends(get_db),
    redis: RedisAsync = Depends(get_redis_async),
    metadata=Depends(get_ct_core_metadata_list),
    weight_profile_id: int | None = Query(default=None, alias="wp"),
    storage_client: StorageProvider = Depends(get_storage_provider),
):
    async def get_status() -> AsyncGenerator[str, None]:
        run_completed = False
        user_resource_usage = cast(
            UserResourceUsage, session.exec(select(UserResourceUsage).where(UserResourceUsage.resource_id == document_id, UserResourceUsage.user_id == user.user.id)).first()
        )

        while not run_completed:
            session.refresh(user_resource_usage)

            run_log: list[bytes] = await redis.lrange(f"run_log:{document_id}", 0, -1)  # type: ignore
            run_completion = float(await redis.get(f"run_log:{document_id}_completion") or 0.0)

            data = {"user_resource_usage": user_resource_usage.model_dump_json(), "run_log": [item.decode("utf-8") for item in run_log], "completion": run_completion}

            # * Check if the run has completed
            run_completed = user_resource_usage.status is UserResourceUsageStatus.COMPLETED

            if run_completed and user_resource_usage.result is not None:
                # * Get weight profile
                weight_profile = get_a_weight_profile_for_user_or_default(session=session, user=user.user)

                cost_nodes, risk_nodes = transform_data_for_rac(metadata=metadata, result=user_resource_usage.result, module_weight=weight_profile, selected_param={})
                total_cost, total_cost_per_participant = get_total_trial_cost(ct_nodes=cost_nodes, module_weight=weight_profile)
                trial_risk_score_numeric, trial_risk_level = get_trial_risk_score(ct_node=risk_nodes, module_weight=weight_profile)

                completed_data = {
                    **data,
                    "trial_cost_table": [node.model_dump() for node in cost_nodes],
                    "trial_risk_table": [node.model_dump() for node in risk_nodes],
                    "cost": {"total_cost": total_cost, "total_cost_per_participant": total_cost_per_participant},
                    "trial_risk_score": trial_risk_level,
                    "trial_risk_score_numeric": trial_risk_score_numeric,
                }

                data_json = orjson.dumps(completed_data).decode("utf-8")
                yield f"data: {data_json}\n\n"
                break

            data_json = orjson.dumps(data).decode("utf-8")
            yield f"data: {data_json}\n\n"

            await asyncio.sleep(delay=1)

    # * Do a quick validation first
    # * Check if document exists and status is not complete
    document = session.exec(select(Document).where(Document.id == document_id, Document.user_id == user.user.id)).first()
    user_resource_usage = session.exec(select(UserResourceUsage).where(UserResourceUsage.resource_id == document_id, UserResourceUsage.user_id == user.user.id)).first()

    if document is None or user_resource_usage is None:
        return ServerResponse(error="No document found", status_code=404)

    if user_resource_usage.status not in [UserResourceUsageStatus.QUEUED, UserResourceUsageStatus.IN_PROGRESS] and user_resource_usage.result:
        # todo make a util function and wrap the invocations

        # * Get weight profile
        weight_profile = get_a_weight_profile_for_user_by_id_or_default(session=session, user=user.user, weight_profile_id=weight_profile_id)

        cost_nodes, risk_nodes = transform_data_for_rac(metadata=metadata, result=user_resource_usage.result, module_weight=weight_profile, selected_param={})
        total_cost, total_cost_per_participant = get_total_trial_cost(ct_nodes=cost_nodes, module_weight=weight_profile)
        trial_risk_score_numeric, trial_risk_level = get_trial_risk_score(ct_node=risk_nodes, module_weight=weight_profile)

        return ServerResponse(
            data={
                "document": {
                    **document.model_dump(),
                    "cdn_path": storage_client.get_internal_cdn_url(user_id=user.user.id, object_id=document.id),
                },
                "result": user_resource_usage.result,
                "trial_cost_table": cost_nodes,
                "trial_risk_table": risk_nodes,
                "cost": {"total_cost": total_cost, "total_cost_per_participant": total_cost_per_participant},
                "trial_risk_score": trial_risk_level,
                "trial_risk_score_numeric": trial_risk_score_numeric,
                "weight_profile": weight_profile.model_dump(exclude={"weights"}),
            }
        )

    return StreamingResponse(content=get_status(), media_type="text/event-stream")


@router.get(path="/{document_id}/run")
async def get_document_process_run(
    document_id: int,
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER, RoleEnum.GUEST])),
    session: Session = Depends(get_db),
    metadata=Depends(get_ct_core_metadata_list),
    storage_client: StorageProvider = Depends(get_storage_provider),
    weight_profile_id: int | None = Query(default=None, alias="wp"),
):
    document = session.exec(select(Document).where(Document.id == document_id, Document.user_id == user.user.id)).first()
    user_resource_usage = session.exec(select(UserResourceUsage).where(UserResourceUsage.resource_id == document_id, UserResourceUsage.user_id == user.user.id)).first()

    if document is None or user_resource_usage is None:
        return ServerResponse(error="No document found", status_code=404)

    if user_resource_usage.result is None:
        return ServerResponse(
            data={
                "document": {
                    **document.model_dump(),
                    "cdn_path": storage_client.get_internal_cdn_url(user_id=user.user.id, object_id=document.id),
                }
            }
        )

    # * Get weight profile
    weight_profile = get_a_weight_profile_for_user_by_id_or_default(session=session, user=user.user, weight_profile_id=weight_profile_id)

    cost_nodes, risk_nodes = transform_data_for_rac(metadata=metadata, result=user_resource_usage.result, module_weight=weight_profile, selected_param={})
    total_cost, total_cost_per_participant = get_total_trial_cost(ct_nodes=cost_nodes, module_weight=weight_profile)
    trial_risk_score_numeric, trial_risk_level = get_trial_risk_score(ct_node=risk_nodes, module_weight=weight_profile)

    return ServerResponse(
        data={
            "document": {
                **document.model_dump(),
                "cdn_path": storage_client.get_internal_cdn_url(user_id=user.user.id, object_id=document.id),
            },
            "result": user_resource_usage.result,
            "trial_cost_table": cost_nodes,
            "trial_risk_table": risk_nodes,
            "cost": {"total_cost": total_cost, "total_cost_per_participant": total_cost_per_participant},
            "trial_risk_score": trial_risk_level,
            "trial_risk_score_numeric": trial_risk_score_numeric,
            "weight_profile": weight_profile.model_dump(exclude={"weights"}),
        }
    )


@router.get(path="/cdn/{document_id}")
async def get_a_document_url(
    document_id: int,
    session: Session = Depends(get_db),
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    storage_client: StorageProvider = Depends(get_storage_provider),
):
    document = session.exec(select(Document).where(Document.id == document_id, Document.user_id == user.user.id)).first()

    if document is None:
        return ServerResponse(error="Document not found", status_code=404)

    return ServerResponse(
        data={
            "cdn_path": storage_client.get_internal_cdn_url(user_id=user.user.id, object_id=document.id),
        }
    )


@router.get(path="/cdn/{document_id}/{signature}")
async def get_a_document_object(
    document_id: int,
    signature: str,
    session: Session = Depends(get_db),
    storage_client: StorageProvider = Depends(get_storage_provider),
):
    decoded_signature = decode_sha256(encoded_data=signature)

    if "::" not in decoded_signature:
        return ServerResponse(error="Invalid signature", status_code=400)

    user_id, expiry_time_from_signature = decoded_signature.split("::")

    try:
        expiry_time = int(expiry_time_from_signature)
        current_time = int(datetime.now(UTC).timestamp())
        if current_time > expiry_time:
            return ServerResponse(error="URL has expired", status_code=403)
    except ValueError:
        return ServerResponse(error="Invalid expiry time", status_code=400)

    document = session.exec(select(Document).where(Document.id == document_id, Document.user_id == user_id)).first()

    if document is None:
        return ServerResponse(error="Document not found", status_code=404)

    user_resource_identifier = cast(User, session.exec(select(User).where(User.id == user_id)).first()).user_resource_identifier

    file_content = storage_client.get_file(file_name=f"{CDN_BUCKET_OR_CONTAINER_BASE_PATH}/documents/{user_resource_identifier}/{document.system_assigned_name}")
    if file_content is None:
        return ServerResponse(error="File not found in storage", status_code=404)

    media_type, _ = mimetypes.guess_type(document.system_assigned_name)

    if media_type is None:
        media_type = "application/octet-stream"

    return Response(content=file_content, media_type=media_type, headers={"Content-Disposition": f"inline; filename={document.system_assigned_name}"})


@router.get(path="/public/templates")
async def get_all_document_templates(
    session: Session = Depends(get_db),
):
    template_documents = get_all_template_documents(session=session)
    return ServerResponse(data=template_documents)


@router.get(path="/public/templates/{document_id}")
async def get_document_template_run_result(
    session: Session = Depends(get_db),
):
    template_documents = get_all_template_documents(session=session)
    return ServerResponse(data=template_documents)


@router.get(path="/{document_id}/exports/pdf")
async def export_run_result_to_pdf(
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    db_document: Document = Depends(dep_get_user_document_by_id),
    storage_client: StorageProvider = Depends(get_storage_provider),
    user_resource_usage: UserResourceUsage = Depends(dep_get_user_resource_usage_by_document_id),
    metadata: list[ClinicalTrialMetadata] = Depends(get_ct_core_metadata_list),
    session: Session = Depends(get_db),
) -> Response:
    """
    Export run result to PDF.
    """

    if not PDF_GENERATOR_AVAILABLE:
        logger.error(f"Could not generate analysis report PDF: {WKHTMLTOPDF_IO_ERROR_MESSAGE}")
        return ServerResponse(status_code=500, error="Could not generate analysis report PDF.")

    # Get db user
    db_user = cast(
        User,
        session.exec(select(User).where(User.id == user.user.id)).first(),
    )
    if not db_user:
        logger.error(f"Could not find user with ID {user.user.id} in database.")
        return ServerResponse(status_code=500, error="Error generating analysis report PDF.")

    # Get db analysis report
    db_analysis_report: AnalysisReport | None = cast(
        AnalysisReport,
        session.exec(select(AnalysisReport).where(AnalysisReport.document_id == db_document.id)).first(),
    )

    # Get the analysis report data filename from db record, download it from storage and validate it with schema
    analysis_report_data: AnalysisReportDataSchema | None = None
    if db_analysis_report:
        # Download analysis report data
        analysis_report_file_storage_key = create_analysis_report_file_storage_key(
            user=db_user,
            filename=db_analysis_report.system_assigned_name,
        )
        try:
            filebytes = storage_client.get_file(file_name=analysis_report_file_storage_key)

            # Validate the file with schema
            analysis_report_data_dict = json.loads(filebytes.decode("utf-8"))
            analysis_report_data = AnalysisReportDataSchema.model_validate(analysis_report_data_dict)
        except (Exception,):
            # If the file was not found on storage or is invalid, proceed with creating a new analysis report data
            analysis_report_data = None

    # If no analysis report data was found, create it here
    if not analysis_report_data:
        # Download document
        document_bytes = storage_client.get_file(file_name=f"{CDN_BUCKET_OR_CONTAINER_BASE_PATH}/documents/{db_user.user_resource_identifier}/{db_document.system_assigned_name}")

        # Parse document
        parsed_document = process_document(file_contents=document_bytes)

        # Map document to CT document
        ct_document = map_document_parser_response_to_ct_document(data=parsed_document)

        # Get weight profile
        weight_profile = get_a_weight_profile_for_user_or_default(session=session, user=db_user)

        # Get CT nodes
        ct_cost_nodes, ct_risk_nodes = transform_data_for_rac(
            metadata=metadata,
            result=user_resource_usage.result,
            module_weight=weight_profile,
            selected_param={},
        )

        # Analysis report Logs
        analysis_report_logs = extract_logs_for_analysis_report(
            parsed_document_metadata=dict(parsed_document.metadata),
            user_resource_usage_result=user_resource_usage.result,
        )

        # Create analysis report data and upload it to storage
        try:
            res_create_and_upload_to_storage = create_analysis_report_data_and_upload_to_storage(
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
            )
            analysis_report_data: AnalysisReportDataSchema = res_create_and_upload_to_storage["analysis_report_data"]
        except (Exception,) as e:
            logger.error(f"Could not create analysis report data for document {db_document.id}: {str(e)}")
            return ServerResponse(status_code=500, error="Error creating analysis report PDF")

    # Generate PDF
    pdf_bytes = PdfGenerator().generate_analysis_report(data=analysis_report_data)

    # Filename without the extension
    filename_no_ext = remove_file_extension(db_document.original_document_name)

    return Response(
        content=io.BytesIO(pdf_bytes).getvalue(),
        headers={"Content-Disposition": f"inline; filename=analysis_{filename_no_ext}.pdf"},
        media_type="application/pdf",
    )
