from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, Column, BigInteger, ForeignKey, Integer, DateTime, text

if TYPE_CHECKING:
    from app.models.subscription.subscription_type import SubscriptionType


class SubscriptionAttribute(SQLModel, table=True):
    __tablename__: str = "subscription_attribute"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    subscription_type_id: int = Field(
        sa_column=Column(
            BigInteger(), ForeignKey("subscription_type.id"), primary_key=True
        ),
        exclude=True,
    )
    file_processing_limit: int = Field(
        default=0, sa_column=Column(Integer(), server_default=text("0"), nullable=False)
    )
    file_size: int = Field(
        default=0,
        sa_column=Column(
            Integer(),
            server_default=text("0"),
            comment="File size in mega bytes MB",
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default=datetime.now(UTC),
        sa_column=Column(
            DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False
        ),
    )

    # Relationships
    type: "SubscriptionType" = Relationship(back_populates="subscription_attribute")
