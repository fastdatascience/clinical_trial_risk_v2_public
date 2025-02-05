from sqlmodel import Field, SQLModel, Column, BigInteger, ForeignKey


class SubscriptionModule(SQLModel, table=True):
    __tablename__: str = "subscription_module"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    subscription_type_id: int = Field(sa_column=Column(BigInteger(), ForeignKey("subscription_type.id"), primary_key=True))
    module_id: int = Field(sa_column=Column(BigInteger(), ForeignKey("module.id"), primary_key=True))
