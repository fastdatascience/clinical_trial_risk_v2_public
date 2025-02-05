from fastapi import APIRouter, Depends
from sqlalchemy.orm import joinedload
from sqlmodel import Session, col, select

from app.models.server_response import ServerResponse
from app.models.subscription.subscription_type import SubscriptionType
from app.resources import get_db

router = APIRouter()


@router.get(path="/plans")
async def get_user_subscription(
    session: Session = Depends(get_db),
):
    subscription_plans: list[SubscriptionType] = list(
        session.exec(
            select(SubscriptionType)
            .where(SubscriptionType.is_unavailable == False)
            .options(joinedload(SubscriptionType.subscription_attribute))
            .order_by(col(SubscriptionType.price).asc())
        ).all()
    )

    serialized_subscription_plans = [
        {**subscription_plan.model_dump(), "subscription_attribute": subscription_plan.subscription_attribute.model_dump()} for subscription_plan in subscription_plans
    ]

    return ServerResponse(data=serialized_subscription_plans)
