from datetime import UTC, datetime

from sqlmodel import Field, SQLModel, Column, BigInteger, ForeignKey


class AnalysisReport(SQLModel, table=True):
    __tablename__: str = "analysis_report"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    document_id: int = Field(
        sa_column=Column(BigInteger(), ForeignKey("document.id", ondelete="CASCADE"), nullable=False)
    )
    system_assigned_name: str = Field(max_length=255)
    type: str = Field(max_length=20)
    created_at: datetime = Field(default=datetime.now(UTC))
