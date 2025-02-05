from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, Column, Text, BigInteger, ForeignKey, Integer, String, DateTime, \
    text, Boolean

if TYPE_CHECKING:
    from app.models.user.base import User


class Document(SQLModel, table=True):
    __tablename__: str = "document"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    original_document_name: str = Field(
        sa_column=Column(Text(), comment="Original document name", nullable=False)
    )
    system_assigned_name: str = Field(sa_column=Column(Text(), nullable=False))
    document_type: str = Field(
        default="application/pdf",
        max_length=20,
        sa_column=Column(
            String(), server_default=text("'application/pdf'::character varying"), nullable=False
        ),
    )
    document_size: int = Field(
        default=0,
        sa_column=Column(
            Integer(),
            comment="File size in bytes",
            server_default=text("0"),
            nullable=False,
        ),
    )
    user_id: int = Field(
        exclude=True,
        sa_column=Column(BigInteger(), ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
    )
    template: bool = Field(
        default=False,
        exclude=True,
        sa_column=Column(Boolean(), server_default=text("false"), nullable=False),
    )
    created_at: datetime = Field(
        default=datetime.now(UTC),
        sa_column=Column(
            DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False
        ),
    )

    # Relationships
    user: "User" = Relationship(back_populates="documents")
