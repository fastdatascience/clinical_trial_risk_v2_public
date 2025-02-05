from typing import cast

from sqlmodel import Session, col, select

from app.models.user.base import User
from app.models.weight_profile.base import UserWeightProfile, WeightProfile


def get_default_weight_profiles(session: Session) -> WeightProfile:
    return cast(WeightProfile, session.exec(select(WeightProfile).where(WeightProfile.default == True)).first())  # noqa: E712


def get_all_weight_profiles(session: Session) -> list[WeightProfile]:
    return list(session.exec(select(WeightProfile).order_by(col(WeightProfile.id).desc())).all())


def get_a_weight_profile_for_user_or_default(session: Session, user: User) -> UserWeightProfile | WeightProfile:
    user_weights = list(session.exec(select(UserWeightProfile).where(UserWeightProfile.user_id == user.id).order_by(col(UserWeightProfile.id).desc())).all())

    if user_weights:
        return user_weights.pop()

    return get_default_weight_profiles(session=session)


def get_all_weight_profiles_for_user(session: Session, user: User) -> list[UserWeightProfile]:
    return list(session.exec(select(UserWeightProfile).where(UserWeightProfile.user_id == user.id).order_by(col(UserWeightProfile.id).desc())).all())


def get_a_weight_profile_for_user_by_id(session: Session, user: User, profile_id: int) -> UserWeightProfile | None:
    return session.exec(
        select(UserWeightProfile).where(UserWeightProfile.user_id == user.id, UserWeightProfile.id == profile_id).order_by(col(UserWeightProfile.id).desc())
    ).first()


def get_a_weight_profile_for_user_by_id_or_default(session: Session, user: User, weight_profile_id: int | None) -> WeightProfile | UserWeightProfile:
    """
    Retrieve a user's weight profile by ID or return a default profile.

    This function attempts to fetch a weight profile for a given user based on the provided parameters:
    - If weight_profile_id is None, it returns a default weight profile for the user.
    - If weight_profile_id is provided, it tries to fetch the specific UserWeightProfile.
    - If the specific profile is not found, it falls back to the default weight profile.

    Args:
        session (Session): The database session used to execute queries
        user (User): The user for whom the weight profile is being retrieved
        profile_id (int): The ID of the weight profile to retrieve

    Returns:
        UserWeightProfile | None: The user's weight profile if found; otherwise, the default WeightProfile.
    """
    if weight_profile_id is None:
        return get_a_weight_profile_for_user_or_default(session=session, user=user)

    weight_profile = session.exec(
        select(UserWeightProfile).where(UserWeightProfile.user_id == user.id, UserWeightProfile.id == weight_profile_id).order_by(col(UserWeightProfile.id).desc())
    ).first()

    if weight_profile is None:
        return get_a_weight_profile_for_user_or_default(session=session, user=user)

    return weight_profile
