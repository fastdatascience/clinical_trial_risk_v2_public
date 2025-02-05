from sqlmodel import Field, SQLModel, Column, BigInteger, ForeignKey


class UserRole(SQLModel, table=True):
    __tablename__: str = "user_role"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    user_id: int = Field(sa_column=Column(BigInteger(), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True))
    role_id: int = Field(sa_column=Column(BigInteger(), ForeignKey("role.id"), primary_key=True))
