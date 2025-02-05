from sqlmodel import Field, SQLModel, Column, BigInteger


class Currency(SQLModel, table=True):
    __tablename__: str = "currency"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    code: str = Field(nullable=False)
