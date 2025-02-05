from sqlmodel import SQLModel, Field, Column, BigInteger, ForeignKey


class UserModule(SQLModel, table=True):
    __tablename__: str = "user_module"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment="Directly links users to modules in cases where a user is manually assigned to a specific module, bypassing subscriptions"
        )
    )

    user_id: int = Field(sa_column=Column(BigInteger(), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True))
    module_id: int = Field(sa_column=Column(BigInteger(), ForeignKey("module.id"), primary_key=True))

    # Relationships
    # user: "User" = Relationship(back_populates="user_modules")
