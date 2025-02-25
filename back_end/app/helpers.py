import json
from collections import OrderedDict
from json import JSONDecodeError
from typing import cast
from uuid import uuid4

from spacy.tokens import Doc as SpacyDoc
from sqlmodel import Session, select

from app import services, models, utils, schemas, config
from app.log_config import logger
from app.models import AnalysisReport
from app.models.document.document import Document
from app.models.user.base import User
from app.models.weight_profile.base import (
    UserWeightProfile,
    WeightProfile,
    WeightProfileBase,
)
from app.services import storage_provider
from app.services import transform
from app.utils import (
    create_analysis_report_file_storage_key,
    create_document_file_storage_key,
    get_file_extension,
    remove_file_extension,
)


def create_analysis_report_data_and_upload_to_storage(
    db_user: User,
    db_document: Document,
    ct_cost_nodes: list[transform.CTNode],
    ct_risk_nodes: list[transform.CTNode],
    user_resource_usage_result: dict,
    tokenised_pages: list[SpacyDoc],
    weight_profile: UserWeightProfile | WeightProfile,
    storage_client: storage_provider.StorageProvider,
    weights: WeightProfileBase,
    session: Session,
    logs: OrderedDict[str, list[str]],
    analysis_run_time: float = None,
) -> dict[str, models.AnalysisReport | schemas.AnalysisReportData]:
    """
    Create analysis report data, upload analysis report data to storage and create analysis report record in database.
    """

    # Generate analysis report data
    logger.info(f"Generating analysis report data for document {db_document.id}.")
    analysis_report_data = services.AnalysisReportData(
        db_document=db_document,
        tokenised_pages=tokenised_pages,
        user_resource_usage_result=user_resource_usage_result,
        trial_risk_score=transform.get_trial_risk_score(
            ct_node=ct_risk_nodes, module_weight=weight_profile
        ),
        ct_cost_nodes=ct_cost_nodes,
        ct_risk_nodes=ct_risk_nodes,
        weights=weights,
        logs=logs,
        analysis_run_time=analysis_run_time,
    ).generate()
    analysis_report_data_dict = analysis_report_data.model_dump(mode="json")

    # Store analysis report data to storage
    logger.info(
        f"Uploading analysis report data to storage for document {db_document.id}."
    )
    system_assigned_name = f"{uuid4()}_analysis_report.json"
    analysis_report_data_bytes = json.dumps(analysis_report_data_dict).encode("utf-8")
    analysis_report_file_storage_key = utils.create_analysis_report_file_storage_key(
        user_resource_identifier=db_user.user_resource_identifier,
        filename=system_assigned_name,
    )
    storage_client.put_file(
        file_name=analysis_report_file_storage_key,
        data=analysis_report_data_bytes,
        content_type="application/json",
    )

    # Create analysis report record in database
    logger.info(
        f"Adding analysis report record to database for document {db_document.id}."
    )
    db_analysis_report = models.AnalysisReport(
        document_id=db_document.id,
        system_assigned_name=system_assigned_name,
        type="application/json",
    )
    session.add(db_analysis_report)
    session.commit()

    logger.info(
        f"Analysis report data successfully created for document {db_document.id}."
    )

    return {
        "db_analysis_report": db_analysis_report,
        "analysis_report_data": analysis_report_data,
    }


def extract_logs_for_analysis_report(
    parsed_document_metadata: dict[str, str] = None,
    user_resource_usage_result: dict = None,
) -> OrderedDict[str, list[str]]:
    """
    Extract logs from:
     - The parsed document metadata.
     - The user resource usage result.

    :param parsed_document_metadata: Metadata from the parsed document.
    :param user_resource_usage_result: The user resource usage result.
    :returns: This is a dictionary where the key is the subject logged, and the value is a list with the log messages.
    """

    if not parsed_document_metadata:
        parsed_document_metadata = {}
    if not user_resource_usage_result:
        user_resource_usage_result = {}

    logs: OrderedDict[str, list[str]] = OrderedDict()

    # Get parsed document logs
    parsed_document_logs_json: str = parsed_document_metadata.get("logs", "[]")
    try:
        parsed_document_logs: list[str] = json.loads(parsed_document_logs_json)
    except JSONDecodeError:
        parsed_document_logs: list[str] = []
    if parsed_document_logs:
        logs["parsed_document"] = parsed_document_logs

    # Get logs from user resource usage result
    for key, value in user_resource_usage_result.items():
        if value_logs := value.get("logs"):
            logs[key] = value_logs

    return logs


def get_user_analysis_report_data_storage_keys(
    session: Session,
    user: User,
    document_ids: list[int],
) -> list[str]:
    """
    Get user analysis report data storage keys by using the document IDs.

    :param session: The session.
    :param user: The user.
    :param document_ids: The IDs of the documents from which the analysis reports were created.
    """

    if not document_ids:
        return []

    # Get analysis report records from db
    db_analysis_reports = cast(
        list[AnalysisReport],
        session.exec(
            select(AnalysisReport)
            .where(AnalysisReport.document_id.in_(document_ids))
            .join(Document, Document.id == AnalysisReport.document_id)
            .where(Document.user_id == user.id)
        ).all(),
    )

    file_names = [
        create_analysis_report_file_storage_key(
            user_resource_identifier=user.user_resource_identifier,
            filename=x.system_assigned_name,
        )
        for x in db_analysis_reports
    ]

    return file_names


def get_user_documents_storage_keys(
    session: Session,
    user: User,
    document_ids: list[int],
    included_annotated_documents: bool = False
) -> list[str]:
    """
    Get user documents storage keys by using the document IDs.

    :param session: The session.
    :param user: The user.
    :param document_ids: The document IDs.
    :param included_annotated_documents: Whether to include the annotated documents or not.
    """

    if not document_ids:
        return []

    # Get document records from db
    db_documents = cast(
        list[Document],
        session.exec(
            select(Document).where(
                Document.user_id == user.id, Document.id.in_(document_ids)
            )
        ).all(),
    )

    file_names: list[str] = []
    for db_document in db_documents:
        # Append the document file names
        file_names.append(
            create_document_file_storage_key(
                user_resource_identifier=user.user_resource_identifier,
                filename=db_document.system_assigned_name,
            )
        )

        # Append the annotated document file names
        if included_annotated_documents:
            file_no_ext = remove_file_extension(db_document.system_assigned_name)
            file_extension = get_file_extension(db_document.system_assigned_name)
            file_names.append(
                create_document_file_storage_key(
                    user_resource_identifier=user.user_resource_identifier,
                    filename=f"{file_no_ext}_annotated.{file_extension}",
                )
            )

    return file_names
