import os
import pathlib
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import wraps
from time import time
from typing import Any, Callable
from uuid import uuid4

import nltk
import clinicaltrials.core as ct_core
import grpc
from clinicaltrials.core import ClinicalTrial
from clinicaltrials.core import Metadata as ClinicalTrialMetadata
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.security import HTTPAuthorizationCredentials
from loguru import logger
from pydantic import ValidationError
from redis.asyncio import Redis as RedisAsync
from sqlmodel import Session, SQLModel

from app.database import SessionLocal, engine
from app.database_default_data import db_create_all_extensions, db_insert_all_default_data
from app.models.document.document import Document
from app.models.document.repo import get_a_document_by_id
from app.models.user.base import User, UserWithRoles
from app.models.user.role import Role, RoleEnum
from app.models.weight_profile.base import UserWeightProfile, WeightProfile
from app.security import JWTBearer, JWTUserExceptionError
from app.services.storage_provider import StorageProvider

from . import config
from .ct_core import celery as document_processor_celery_instance
from .models.user.repo import get_user_resource_usage_by_document_id
from .models.user.user_resource_usage import UserResourceUsage
from .models.weight_profile.repo import get_a_weight_profile_for_user_or_default

this_folder = pathlib.Path(__file__).parent.resolve()

sys.path.append(f"{this_folder}/../clinical_trials_core/src")

__redis_async = RedisAsync.from_url(config.REDIS_ENDPOINT)

logger.debug("Building clinical trials core metadata")
ct = ClinicalTrial()
__CORE_LIB_VERSION = ct_core.__version__
logger.info(f"Clinical Trials Core version: {__CORE_LIB_VERSION}")

# * List of module names loaded for ct core
__ct_core_modules = ct.modules
__ct_core_metadata_list = ct.metadata
__ct_core_metadata_dict = ct.metadata_dict

# * Remove from memory
del ct
logger.debug("Clinical trials core metadata built. Removing reference from memory")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    await startup(app)
    try:
        yield
    finally:
        await shutdown(app)


async def startup(app: FastAPI) -> None:
    redis = get_redis_async()

    # Download NLTK data (stopwords)
    redis_key_nltk_data_downloaded = "nltk_data_downloaded"
    nltk_data_downloaded_lock_acquired = await redis.set(
        name=redis_key_nltk_data_downloaded,
        value=1,
        nx=True,
        ex=30,
    )
    if nltk_data_downloaded_lock_acquired:
        try:
            if not os.path.isdir(config.NLTK_DATA_PATH):
                os.makedirs(config.NLTK_DATA_PATH)
            nltk.data.path.append(config.NLTK_DATA_PATH)
            nltk.download("stopwords", download_dir=config.NLTK_DATA_PATH)
            logger.info(f"NLTK data downloaded to {config.NLTK_DATA_PATH}.")
        except (Exception,) as e:
            logger.error(f"Could not download NLTK data: {str(e)}")

    # Insert database defaults
    if not config.DEVELOPMENT:
        redis_key_database_defaults_inserted = "database_defaults_inserted"
        database_defaults_inserted_lock_acquired = await redis.set(
            name=redis_key_database_defaults_inserted,
            value=1,
            nx=True,
            ex=30,
        )
        if database_defaults_inserted_lock_acquired:
            # Create extensions
            logger.info("Creating extensions, will not attempt to recreate extensions already present in the target database.")
            db_create_all_extensions()

            # Create tables
            logger.info("Creating tables found in SQLModel.metadata, will not attempt to recreate tables already present in the target database.")
            SQLModel.metadata.create_all(engine)

            # Insert default data into tables
            db_insert_all_default_data()

    show_config()

    # * Calls to connect to database and other services
    app.state.security = JWTBearer()

    if check_celery_status():
        logger.info("Celery is online, document processing available...")
    else:
        logger.info("Celery is offline, document processing will not be available...")

    ping_grpc(config.GRPC_ENDPOINT)

    logger.info(f"Storage provider {config.STORAGE_PROVIDER} selected")
    logger.info(f"Storage provider using container/bucket {config.BUCKET_OR_CONTAINER_NAME}")

    logger.info("Started...")


async def shutdown(app: FastAPI) -> None:
    # * Calls to disconnect from database and other services
    logger.info("...Shutdown")


def show_config() -> None:
    config_vars = {key: getattr(config, key) for key in sorted(dir(config)) if key.isupper()}
    logger.debug(config_vars)


def format_validation_errors(exc: ValidationError | RequestValidationError | str) -> list[str]:
    errors = []

    if isinstance(exc, str):
        return [exc]

    for error in exc.errors():
        loc = ".".join(str(loc_part) for loc_part in error.get("loc", []))
        msg = error.get("msg", "")
        errors.append(f"{loc}: {msg}")
    return errors


def get_db():
    session = SessionLocal()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_redis_async() -> RedisAsync:
    return __redis_async


def get_current_user(request: Request, _: HTTPAuthorizationCredentials = Depends(JWTBearer())) -> UserWithRoles:
    user_data = getattr(request.state, "user_data", None)
    if not user_data:
        raise JWTUserExceptionError(status_code=401, error="User data not found", errors=["User data could not be retrieved."])

    user = User(**user_data["user"])
    roles = [Role(**role_data) for role_data in user_data["user_roles"]]

    return UserWithRoles(user=user, user_roles=roles)


def get_user_with_roles(*, required_roles: list[RoleEnum] | None = None):
    def _get_user_with_roles(current_user: UserWithRoles = Depends(get_current_user)) -> UserWithRoles:
        user_roles_enum = [RoleEnum.role_to_enum(role.id) for role in current_user.user_roles if role.id]

        if required_roles and not any(role_enum in required_roles for role_enum in user_roles_enum):
            raise JWTUserExceptionError(status_code=403, error="Role not authorized", errors=[f"Required roles: {', '.join([role.name for role in required_roles])}"])
        return current_user

    return _get_user_with_roles


def get_ct_core_modules_list() -> list[str]:
    return __ct_core_modules


def get_ct_core_metadata_list() -> list[ClinicalTrialMetadata]:
    return __ct_core_metadata_list


def get_ct_core_metadata_dict() -> list[dict]:
    return __ct_core_metadata_dict


def check_celery_status():
    try:
        inspector = document_processor_celery_instance.control.inspect(timeout=2)
        status = inspector.ping()

        return bool(status)
    except Exception:
        return False


def ping_grpc(endpoint: str):
    try:
        with grpc.insecure_channel(endpoint) as channel:
            grpc.channel_ready_future(channel).result(timeout=2)
            logger.info(f"Tika server avalable at {endpoint} document parsing is available")
    except grpc.FutureTimeoutError:
        logger.info(f"Tika server at {endpoint} is offline or unreachable document parsing is unavailable")


def get_storage_provider():
    return StorageProvider()


def is_demo_account(email: str | None = None, current_user: UserWithRoles = Depends(get_current_user)) -> bool:
    """
    Check if the current user is a demo user or if the provided email matches the demo account email
    """
    if email is not None:
        return email == config.DEMO_ACCOUNT_EMAIL
    return current_user.user.email == config.DEMO_ACCOUNT_EMAIL


def get_core_lib_version():
    return __CORE_LIB_VERSION


def get_server_version():
    return config.__SERVER_VERSION


def dep_get_user_document_by_id(
    document_id: int,
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
) -> Document:
    """
    Get document by ID.
    """

    document = get_a_document_by_id(session=session, user=user.user, document_id=document_id)
    if document:
        return document

    raise HTTPException(status_code=404, detail="No document found.")


def dep_get_user_resource_usage_by_document_id(
    document_id: int,
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
) -> UserResourceUsage:
    """
    Get user resource usage by ID.
    """

    user_resource_usage = get_user_resource_usage_by_document_id(session=session, user=user.user, document_id=document_id)
    if user_resource_usage and user_resource_usage.result:
        return user_resource_usage

    raise HTTPException(status_code=404, detail="No user resource usage found.")


def dep_get_user_weight_profile_or_default(
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
) -> UserWeightProfile | WeightProfile:
    """
    Get user weight profile or the default weight profile.
    """

    weight_profile = get_a_weight_profile_for_user_or_default(session=session, user=user.user)
    if weight_profile:
        return weight_profile

    raise HTTPException(status_code=404, detail="No weight profile found.")


async def create_or_update_tag_counter(redis: RedisAsync, x_tag: str | None = None) -> tuple[str, int]:
    """
    Used for demo account to keep track of volatile resources
    """
    if not x_tag:
        x_tag = f"{uuid4()}{uuid4()}{int(time())}".replace("-", "")

        # * Set the key with an expiration of 30 days and initialize it with "1"
        await redis.setex(name=x_tag, time=30 * 24 * 60 * 60, value=1)
        count = 1
    else:
        # * Increment the counter for an existing tag
        count = await redis.incr(x_tag)

    return x_tag, count


# todo maybe move this somewhere else


def use_gzip(func: Callable[..., Any]):
    """Decorator to mark a route for GZIP compression"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    setattr(wrapper, "__enable_gzip", True)
    return wrapper
