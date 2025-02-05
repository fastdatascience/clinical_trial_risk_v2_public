from datetime import UTC, datetime, timezone

from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select, update

from app.models.subscription.subscription_type import SubscriptionType
from app.models.user.base import RefreshToken, User
from app.models.user.user_resource_usage import UserResourceUsage
from app.models.user.user_subscription import UserSubscription


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def get_user_subscription(session: Session, user: User) -> UserSubscription | None:
    return session.exec(
        select(UserSubscription)
        .where(UserSubscription.user_id == user.id)
        .options(selectinload(UserSubscription.subscription_type).selectinload(SubscriptionType.subscription_attribute))
        .order_by(col(UserSubscription.id).desc())
    ).first()


def get_user_resource_usage_in_resource_ids(session: Session, user: User, resource_ids: list[int]):
    return session.exec(
        select(UserResourceUsage).where(
            col(UserResourceUsage.resource_id).in_(resource_ids),
            UserResourceUsage.user_id == user.id,
        )
    ).all()


def get_user_resource_usage_by_document_id(session: Session, user: User, document_id: int):
    return session.exec(select(UserResourceUsage).where(UserResourceUsage.resource_id == document_id, UserResourceUsage.user_id == user.id)).first()


def get_user_by_refresh_token(session: Session, refresh_token: str) -> User | None:
    statement = select(RefreshToken).where(RefreshToken.token == refresh_token, RefreshToken.is_active == True, RefreshToken.expires_at > datetime.now(UTC))

    result = session.exec(statement).first()

    if result:
        return result.user

    return None


def deactivate_refresh_token(session: Session, user: User, refresh_token: str) -> bool:
    statement = select(RefreshToken).where(
        RefreshToken.token == refresh_token, RefreshToken.user_id == user.id, RefreshToken.is_active == True, RefreshToken.expires_at > datetime.now(UTC)
    )

    token_record = session.exec(statement).first()

    if token_record:
        token_record.is_active = False

        session.add(token_record)
        session.commit()

        return True

    return False


def get_user_resource_identifier(session: Session, user: User) -> str | None:
    ___user = session.exec(select(User).where(User.id == user.id)).first()

    if ___user:
        return ___user.user_resource_identifier

    return None
