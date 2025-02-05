from sqlmodel import Session, col, select

from app.models.subscription.subscription_attribute import SubscriptionAttribute
from app.models.subscription.subscription_type import SubscriptionType
from app.models.user.base import User
from app.models.user.user_subscription import UserSubscription


def get_user_subscription(session: Session, user: User) -> tuple[UserSubscription, SubscriptionType, SubscriptionAttribute] | None:
    return session.exec(
        select(UserSubscription, SubscriptionType, SubscriptionAttribute)
        .join(SubscriptionType, col(UserSubscription.subscription_type_id) == SubscriptionType.id)
        .join(SubscriptionAttribute, col(SubscriptionAttribute.subscription_type_id) == SubscriptionType.id)
        .filter(col(UserSubscription.user_id) == user.id)
        .order_by(col(UserSubscription.id).desc())
    ).first()
