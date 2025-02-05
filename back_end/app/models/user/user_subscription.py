from datetime import datetime, UTC

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel, Column, BigInteger, ForeignKey, DateTime, text

from app.models.subscription.subscription_type import SubscriptionType


class UserSubscription(SQLModel, table=True):
    __tablename__: str = "user_subscription"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    user_id: int = Field(
        sa_column=Column(BigInteger(), ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        exclude=True,
    )
    subscription_type_id: int = Field(
        sa_column=Column(
            BigInteger(), ForeignKey("subscription_type.id"), nullable=False
        )
    )
    start_date: datetime = Field(
        default=datetime.now(UTC),
        sa_column=Column(
            DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False
        ),
    )
    end_date: datetime = Field(nullable=False)
    created_at: datetime = Field(
        default=datetime.now(UTC),
        sa_column=Column(
            DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False
        ),
    )

    # Relationships
    subscription_type: Mapped["SubscriptionType"] = Relationship(
        back_populates="user_subscriptions"
    )
