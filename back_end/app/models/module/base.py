from sqlmodel import Field, SQLModel, BigInteger, Column


class Module(SQLModel, table=True):
    __tablename__: str = "module"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment="List of modules that users or subscriptions can access"
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    name: str = Field(unique=True, max_length=200, nullable=False)
