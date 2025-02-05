from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel, Column, ForeignKey, BigInteger, Numeric, Text, text, Boolean, \
    DateTime, Enum as DbEnum

from app.models.subscription.subscription_attribute import SubscriptionAttribute

if TYPE_CHECKING:
    from app.models.user.user_subscription import UserSubscription


class SubscriptionTypeEnum(Enum):
    BASIC = 1
    STANDARD = 2
    PRO = 3
    FREE = 4
    GUEST = 5


class SubscriptionDuration(str, Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class SubscriptionType(SQLModel, table=True):
    __tablename__: str = "subscription_type"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    name: str = Field(unique=True, nullable=False)
    price: Decimal = Field(
        sa_column=Column(Numeric(10, 2), server_default=text("0"), nullable=False)
    )
    description: str | None = Field(sa_column=Column(Text(), nullable=True))
    duration: SubscriptionDuration = Field(
        sa_column=Column(
            DbEnum(SubscriptionDuration),
            server_default=text("'MONTHLY'::subscriptionduration"),
            nullable=False,
        )
    )
    currency_id: int = Field(
        sa_column=Column(BigInteger(), ForeignKey("currency.id"), nullable=False)
    )
    is_unavailable: bool = Field(
        default=False,
        sa_column=Column(Boolean(), server_default=text("false"), nullable=False),
    )
    updated_at: datetime = Field(
        default=datetime.now(UTC),
        sa_column=Column(
            DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False
        ),
    )

    # Relationships
    user_subscriptions: Mapped[list["UserSubscription"]] = Relationship(
        back_populates="subscription_type"
    )
    subscription_attribute: Mapped["SubscriptionAttribute"] = Relationship(
        back_populates="type", sa_relationship_kwargs={"uselist": False}
    )
