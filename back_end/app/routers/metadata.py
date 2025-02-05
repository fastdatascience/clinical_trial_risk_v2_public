from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.ct_utils import get_derived_modules_and_metadata
from app.models.server_response import ServerResponse
from app.models.user.base import UserWithRoles
from app.models.user.role import RoleEnum
from app.resources import get_core_lib_version, get_ct_core_metadata_dict, get_ct_core_modules_list, get_db, get_server_version, get_user_with_roles

router = APIRouter()


@router.get(path="/platform/health-check")
async def get_platform_health(
    session: Session = Depends(get_db),
):
    statement = select(1)
    db_result = session.exec(statement).first()

    data = {"database": "fail" if db_result is None else "ok", "server": "ok"}

    return ServerResponse(data=data)


@router.get(path="/platform")
async def get_platform_metadata(core_lib_version: str = Depends(get_core_lib_version), server_version: str = Depends(get_server_version)):
    # * 1 hour from now
    expiration_time = datetime.now() + timedelta(hours=1)
    expires_header = expiration_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    max_age = int(timedelta(hours=1).total_seconds())

    return ServerResponse(
        data={"core_lib_version": core_lib_version, "server_version": server_version}, headers={"Cache-Control": f"public, max-age={max_age}", "Expires": expires_header}
    )


@router.get(path="/engine")
async def get_ct_core_metadata(
    _: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    modules: list[str] = Depends(get_ct_core_modules_list),
    metadata: list[dict] = Depends(get_ct_core_metadata_dict),
    derived_modules_and_metadata=Depends(get_derived_modules_and_metadata),
):
    derived_modules, derived_metadata_dict, _ = derived_modules_and_metadata

    all_modules = modules + list(derived_modules)
    all_metadata = metadata + list(derived_metadata_dict)

    all_modules.sort()
    all_metadata = sorted(all_metadata, key=lambda x: x.get("id", 0))

    return ServerResponse(data={"modules": all_modules, "metadata": all_metadata})


@router.get(path="/engine/weights")
async def get_ct_core_module_weight(
    _: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    modules: list[str] = Depends(get_ct_core_modules_list),
):
    module_weights = {module: {"weight": 0, "score": 0} for module in modules}
    return ServerResponse(data=module_weights)
