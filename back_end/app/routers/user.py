from typing import cast
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from app.config import CDN_BUCKET_OR_CONTAINER_BASE_PATH
from app.helpers import get_user_analysis_report_data_storage_keys, get_user_documents_storage_keys
from app.log_config import logger
from app.models.document.document import Document
from app.models.server_response import ServerResponse
from app.models.subscription.subscription_type import SubscriptionType
from app.models.user.base import User, UserUpdateRequest, UserWithRoles
from app.models.user.role import RoleEnum
from app.models.user.user_subscription import UserSubscription
from app.resources import get_db, get_storage_provider, get_user_with_roles
from app.services.storage_provider import StorageProvider
from app.utils import serialize_sqlmodel, update_instance_from_dict

router = APIRouter()

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/jpg"]


@router.get(path="/subscriptions")
async def get_user_subscription(
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
):
    user_subscription: UserSubscription | None = session.exec(
        select(UserSubscription)
        .where(UserSubscription.user_id == user.user.id)
        .options(selectinload(UserSubscription.subscription_type).selectinload(SubscriptionType.subscription_attribute))
        .order_by(col(UserSubscription.id).desc())
    ).first()

    serialized_user_subscription = None
    if user_subscription:
        serialized_user_subscription = serialize_sqlmodel(user_subscription)

    return ServerResponse(data={"user_subscription": serialized_user_subscription})


@router.post(path="")
async def update_user(
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
    storage_client: StorageProvider = Depends(get_storage_provider),
    payload: str | None = Form(alias="user", default=None),
    profile_picture: UploadFile | None = File(None),
):
    user_instance = cast(User, session.query(User).get(user.user.id))

    if payload:
        user_update = UserUpdateRequest.parse_raw(str.encode(payload))
        update_instance_from_dict(user_instance, user_update.dict())
        logger.info(f"Updated user {user.user.id}::{user.user.email}")

    # * Process profile picture if present
    if profile_picture:
        logger.info(f"Processing profile picture for user {user.user.id}::{user.user.email}")

        # * Ensure it's an image file with a valid MIME type
        if profile_picture.content_type not in ALLOWED_MIME_TYPES:
            return ServerResponse(status_code=400, error="Invalid file type. Please upload a valid image")

        # * Check the file size
        file_contents = await profile_picture.read()

        # * 2MB in bytes
        if len(file_contents) > 2 * 1024 * 1024:
            return ServerResponse(status_code=413, error="Profile picture file size exceeds 2MB limit")

        file_uuid = uuid4()
        filename = f"{file_uuid}_{profile_picture.filename.replace(' ', '_')}" if profile_picture.filename else str(file_uuid)

        # * Delete previous profile picture if any
        if user_instance.profile_picture:
            storage_client.delete_file(file_name=f"{CDN_BUCKET_OR_CONTAINER_BASE_PATH}/images/{user_instance.profile_picture}")
            logger.info(f"Deleted old profile picture for user {user.user.id}::{user.user.email}")

        user_instance.profile_picture = filename

        upload_path = f"{CDN_BUCKET_OR_CONTAINER_BASE_PATH}/images/{filename}"

        storage_client.put_file(file_name=upload_path, data=file_contents, content_type=profile_picture.content_type)

    session.commit()
    session.refresh(user_instance)

    return ServerResponse(data={**user.dict(), "user": user_instance.dict()})


@router.delete(path="")
async def delete_user(
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
    storage_client: StorageProvider = Depends(get_storage_provider),
):
    # Get db user
    db_user: User = session.exec(select(User).where(User.id == user.user.id)).first()
    if not db_user:
        return ServerResponse(status_code=204)

    logger.info(f"Delete user request from user {db_user.id}::{db_user.email}.")

    # Get document IDs from db
    db_document_ids = cast(
        list[int],
        session.exec(select(Document.id).where(Document.user_id == db_user.id)).all(),
    )

    # Delete all analysis reports and documents from storage
    analysis_report_files_to_delete = get_user_analysis_report_data_storage_keys(
        user=db_user,
        document_ids=db_document_ids,
        session=session,
    )
    document_files_to_delete = get_user_documents_storage_keys(
        user=db_user,
        document_ids=db_document_ids,
        session=session,
        included_annotated_documents=True,
    )
    all_files_to_delete = analysis_report_files_to_delete + document_files_to_delete
    logger.info(f"Deleting all analysis report data and documents from storage by user {db_user.id}::{db_user.email}: {all_files_to_delete}")
    storage_client.delete_files(file_names=all_files_to_delete)

    # Delete user record
    # All data associated to this user via a foreign key will be deleted
    session.delete(db_user)

    # Commit
    session.commit()

    logger.info(f"User {db_user.id}::{db_user.email} deleted.")

    return ServerResponse(status_code=204)
