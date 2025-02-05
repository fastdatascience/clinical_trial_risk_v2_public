from datetime import UTC, datetime
from enum import Enum

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import BigInteger, Column, DateTime, Field, ForeignKey, Relationship, SQLModel, text
from sqlmodel import Enum as DbEnum


class ResourceTypeName(Enum):
    FILE_PROCESS = "FILE_PROCESS"


class ResourceType(SQLModel, table=True):
    __tablename__: str = "resource_type"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    name: str = Field(nullable=False)
    updated_at: datetime = Field(
        default=datetime.now(UTC),
        sa_column=Column(
            DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False
        ),
    )

    # Relationships
    user_resource_usages: list["UserResourceUsage"] = Relationship(
        back_populates="resource_type"
    )


class UserResourceUsageStatus(Enum):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    REQUIRES_ACTION = "REQUIRES_ACTION"
    EXPIRED = "EXPIRED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class UserResourceUsage(SQLModel, table=True):
    __tablename__: str = "user_resource_usage"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    user_id: int = Field(
        sa_column=Column(BigInteger(), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    )
    resource_type_id: int = Field(
        sa_column=Column(BigInteger(), ForeignKey("resource_type.id"), nullable=False)
    )
    start_time: datetime = Field(
        default=datetime.now(UTC),
        sa_column=Column(
            DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False
        ),
    )
    end_time: datetime | None = Field(
        sa_column=Column(
            DateTime(),
            comment="Null marks that this resource is still under use",
            nullable=True,
        ),
        default=None,
    )
    resource_id: int | None = Field(
        sa_column=Column(
            BigInteger(),
            ForeignKey("document.id", ondelete="CASCADE"),
            nullable=True
        )
    )
    status: UserResourceUsageStatus = Field(
        default=UserResourceUsageStatus.QUEUED,
        sa_column=Column(
            DbEnum(UserResourceUsageStatus),
            server_default=text("'QUEUED'::userresourceusagestatus"),
            nullable=False,
        )
    )
    result: dict | None = Field(default=None, sa_column=Column(JSONB(), nullable=True))

    # Relationships
    # user: "User" = Relationship(back_populates="user_resource_usage")
    resource_type: "ResourceType" = Relationship(back_populates="user_resource_usages")
