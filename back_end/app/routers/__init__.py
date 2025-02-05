from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.document import router as document_router
from app.routers.metadata import router as metadata_router
from app.routers.subscription import router as subscription_router
from app.routers.user import router as user_router
from app.routers.weight_profile import router as weight_profile_router

router = APIRouter()

router.include_router(router=auth_router, prefix="/auth", tags=["authentication"])
router.include_router(router=user_router, prefix="/users", tags=["users"])
router.include_router(router=document_router, prefix="/documents", tags=["documents"])
router.include_router(router=subscription_router, prefix="/subscriptions", tags=["subscriptions"])
router.include_router(router=weight_profile_router, prefix="/weight-profiles", tags=["weight profiles"])
router.include_router(router=metadata_router, prefix="/metadata", tags=["metadata"])
