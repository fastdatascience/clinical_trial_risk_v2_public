from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, col, select

from app.database import paginate
from app.models.server_response import ServerResponse
from app.models.user.base import UserWithRoles
from app.models.user.role import RoleEnum
from app.models.weight_profile.base import DynamicProfile, UpdateDynamicProfile, UserWeightProfile, WeightProfile, WeightProfileBase, WeightTypeEnum
from app.resources import get_ct_core_modules_list, get_db, get_user_with_roles

router = APIRouter()


def get_weight_type(weight_type: str | None = Query(None, alias="t")) -> WeightTypeEnum | None:
    return WeightTypeEnum.parse(weight_type)


def transform_weights_by_weight_type(data: WeightProfile, weight_type: WeightTypeEnum | None):
    weights = WeightProfileBase(**data.weights)

    match weight_type:
        case WeightTypeEnum.CRM:
            return weights.to_serializable_cost_risk_models(group=True)
        case WeightTypeEnum.SST:
            return weights.to_serializable_sample_size_tertiles()
        case WeightTypeEnum.RT:
            return weights.to_serializable_risk_thresholds()
        case _:
            return weights.to_serializable(group=True)


@router.get(path="")
async def get_default_weight_profiles(
    weight_type: WeightTypeEnum | None = Depends(get_weight_type),
    _: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
):
    paginated_weight_profiles = paginate(session=session, query=select(WeightProfile).order_by(col(WeightProfile.id).desc()), page=page, page_size=page_size)

    for content in paginated_weight_profiles.contents:
        content.weights = transform_weights_by_weight_type(content, weight_type)

    return ServerResponse(data=paginated_weight_profiles.to_dict())


@router.get(path="/users")
async def get_user_weight_profiles(
    weight_type: WeightTypeEnum | None = Depends(get_weight_type),
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
):
    paginated_user_weight_profiles = paginate(
        session=session, query=select(UserWeightProfile).where(UserWeightProfile.user_id == user.user.id).order_by(col(UserWeightProfile.id).desc()), page=page, page_size=page_size
    )

    # * Sort weights by key
    for content in paginated_user_weight_profiles.contents:
        content.weights = transform_weights_by_weight_type(content, weight_type)

    return ServerResponse(data=paginated_user_weight_profiles.to_dict())


@router.post(path="/users")
async def create_user_weight_profiles(
    new_user_weight_profile_payload: DynamicProfile,
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
    allowed_modules: list[str] = Depends(get_ct_core_modules_list),
):
    # * Invoke validation
    DynamicProfile.validate_allowed_keys(new_user_weight_profile_payload.weights, allowed_modules)

    # * New profile should have same number of module keys
    if len(new_user_weight_profile_payload.weights.keys()) < len(allowed_modules):
        return ServerResponse(error="Invalid payload", errors=["Partial weight profiles are not accepted"], status_code=400)

    # * Check for duplicate profile based on name
    profile_exists = (
        session.exec(select(UserWeightProfile.id).where(UserWeightProfile.user_id == user.user.id, UserWeightProfile.name == new_user_weight_profile_payload.name)).unique().first()
    )

    if profile_exists:
        return ServerResponse(error=f"Profile {new_user_weight_profile_payload.name} already exists", status_code=409)

    new_user_weight_profile = UserWeightProfile(user_id=user.user.id, name=new_user_weight_profile_payload.name, weights=new_user_weight_profile_payload.to_serializable())

    session.add(new_user_weight_profile)
    session.commit()
    session.refresh(new_user_weight_profile)

    return ServerResponse(data={**new_user_weight_profile.model_dump()}, status_code=201)


@router.patch(path="/users/{user_weight_profile_id}")
async def update_user_weight_profiles(
    user_weight_profile_id: int,
    update_user_weight_profile_payload: UpdateDynamicProfile,
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
    allowed_modules: list[str] = Depends(get_ct_core_modules_list),
):
    user_weight_profile = session.exec(select(UserWeightProfile).where(UserWeightProfile.id == user_weight_profile_id, UserWeightProfile.user_id == user.user.id)).unique().first()

    if user_weight_profile is None:
        return ServerResponse(error="User weight profile not found", status_code=404)

    # * Invoke validation
    DynamicProfile.validate_allowed_keys(update_user_weight_profile_payload.weights, allowed_modules)

    updated_weights = user_weight_profile.weights.copy() if user_weight_profile.weights else {}

    for module_name, incoming_weight in update_user_weight_profile_payload.weights.items():
        updated_weights[module_name] = incoming_weight.model_dump()

    user_weight_profile.weights = updated_weights

    if update_user_weight_profile_payload.name is not None:
        user_weight_profile.name = update_user_weight_profile_payload.name

    session.add(user_weight_profile)
    session.commit()
    session.refresh(user_weight_profile)

    return ServerResponse(data={**user_weight_profile.model_dump()}, status_code=200)


@router.delete(path="/users/{user_weight_profile_id}")
async def delete_user_weight_profiles(
    user_weight_profile_id: int,
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
):
    user_weight_profile = session.exec(select(UserWeightProfile).where(UserWeightProfile.id == user_weight_profile_id, UserWeightProfile.user_id == user.user.id)).unique().first()

    if user_weight_profile is None:
        return ServerResponse(error="User weight profile not found", status_code=404)

    session.delete(user_weight_profile)
    session.commit()

    return ServerResponse(status_code=204)
