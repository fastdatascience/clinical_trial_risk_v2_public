from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, Column, BigInteger

from app.models.user.user_role import UserRole

if TYPE_CHECKING:
    from app.models.user.base import User


class RoleEnum(Enum):
    PLATFORM_SUPER_ADMIN = 1
    ADMIN = 2
    USER = 3
    GUEST = 4
    EDITOR = 5

    @staticmethod
    def role_to_enum(role_id: int) -> "RoleEnum":
        for enum in RoleEnum:
            if enum.value == role_id:
                return enum
        raise ValueError(f"No matching RoleEnum value for role id: {role_id}")


class Role(SQLModel, table=True):
    __tablename__: str = "role"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    name: str = Field(max_length=100, nullable=False, unique=True)

    # Relationships
    users: list["User"] = Relationship(back_populates="roles", link_model=UserRole)
