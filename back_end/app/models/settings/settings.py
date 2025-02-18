from datetime import UTC, datetime

from sqlmodel import Field, SQLModel, Column, BigInteger, DateTime, text


class Settings(SQLModel, table=True):
    __tablename__: str = "settings"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    name: str = Field(max_length=50, default=None, nullable=False, unique=True)
    value: str = Field(max_length=50, default=None, nullable=False)
    description: str = Field(max_length=50, default=None, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    )
