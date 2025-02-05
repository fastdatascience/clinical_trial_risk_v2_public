from datetime import UTC, datetime
from enum import Enum
from re import match
from uuid import uuid4

import bcrypt
import phonenumbers
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, constr, field_validator, validator
from sqlmodel import Field, Relationship, SQLModel, Column, BigInteger, ForeignKey, Text, DateTime, Boolean, text

from app.models.document.document import Document
from app.models.user.role import Role
from app.models.user.user_role import UserRole


class UserPasswordConstraintError(Exception):
    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


def check_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def is_password_allowed_pattern(value: str):
    # Valid password:
    # Must contain at least one upper case char A-Z
    # Must contain at least one lower case char a-z
    # Must contain at least one digit \d
    # Must contain at least one special character from this list: @#$%^&+=!\?\-/
    # 8 to 20 characters ({8,20})
    password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=!\?\-/\*\(\)\\]).{8,20}$"

    return bool(match(password_pattern, value))


def hash_password(value: str) -> str:
    # * Check if it's an already hashed password
    if len(value) > 60 and (value.startswith("$2b$") or value.startswith("$2y$")):
        return value

    if value is None or not 8 <= len(value) <= 20:
        raise UserPasswordConstraintError(value=value, message="Password should be between 8 to 20 characters long")

    if not is_password_allowed_pattern(value):
        raise UserPasswordConstraintError(
            value=value,
            message="Password must meet the following requirements:\n"
                    "- At least one uppercase letter\n"
                    "- At least one digit\n"
                    "- At least one special character (@#$%^&+=!)\n"
                    "- Length between 8 and 20 characters",
        )

    # * Hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(value.encode("utf-8"), salt)

    return hashed_password.decode("utf-8")


class User(SQLModel, table=True):
    __tablename__: str = "user"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    email: str = Field(unique=True, max_length=100, nullable=False)
    password: str | None = Field(max_length=255, exclude=True, nullable=True)
    first_name: str = Field(max_length=50, default=None, nullable=False)
    last_name: str = Field(max_length=50, default=None, nullable=False)
    phone_number: str = Field(max_length=15, default=None, nullable=True)
    last_login: datetime = Field(default=None, nullable=True)
    email_otp: str | None = Field(default=None, nullable=True, exclude=True)
    phone_number_otp: str | None = Field(default=None, nullable=True, exclude=True)
    is_email_verified: bool = Field(
        default=False,
        sa_column=Column(Boolean(), server_default=text("false"), nullable=True),
    )
    is_phone_number_verified: bool = Field(
        default=False,
        sa_column=Column(Boolean(), server_default=text("false"), nullable=True),
    )
    profile_picture: str | None = Field(
        sa_column=Column(Text(), comment="Picture resource uri", nullable=True)
    )
    user_resource_identifier: str = Field(
        exclude=True,
        default_factory=lambda: uuid4().hex,
        sa_column=Column(
            Text(),
            comment="UUID used for managing AWS resources",
            server_default=text("uuid_generate_v4()"),
            nullable=False,
            index=True,
        ),
    )
    terms_and_privacy_accepted: bool = Field(
        default=False,
        sa_column=Column(Boolean(), server_default=text("false"), nullable=False),
    )
    created_at: datetime = Field(
        default=datetime.now(UTC),
        sa_column=Column(
            DateTime(),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default=datetime.now(UTC),
        sa_column=Column(
            DateTime(),
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=lambda: datetime.now(UTC),
            nullable=False,
        ),
    )

    # Relationships
    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRole)
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user", passive_deletes=True)
    documents: list["Document"] = Relationship(back_populates="user", passive_deletes=True)
    # user_weight_profile: "UserWeightProfile" = Relationship(back_populates="user", passive_deletes=True)
    # user_subscriptions: list["UserSubscription"] = Relationship(back_populates="user", passive_deletes=True)
    # user_resource_usage: "UserResourceUsage" = Relationship(back_populates="user", passive_deletes=True)
    # user_modules: list["UserModule"] = Relationship(back_populates="user", passive_deletes=True)

    @field_validator(
        "password",
        mode="before",
    )
    def hash_and_validate_password(cls, value: str) -> str:
        return hash_password(value=value)

    class Config:  # type: ignore
        from_attributes = True


class UserWithRoles(BaseModel):
    user: User
    user_roles: list[Role] = []

    class Config:
        from_attributes = True


class RefreshToken(SQLModel, table=True):
    __tablename__: str = "refresh_token"  # type: ignore
    __table_args__: tuple = (
        dict(
            comment=None
        )
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    user_id: int = Field(
        sa_column=Column(BigInteger(), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    )
    token: str = Field(max_length=500, unique=True, nullable=False)
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean(), server_default=text("true"), nullable=False),
    )
    ip_address: str | None = Field(max_length=45, nullable=True)
    device_info: str | None = Field(sa_column=Column(Text(), nullable=True))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False
        ),
    )
    expires_at: datetime = Field(nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="refresh_tokens")


class UserCreateRequest(BaseModel):
    email: str
    password: str
    first_name: constr(min_length=3, max_length=50)  # type: ignore
    last_name: constr(min_length=2, max_length=50)  # type: ignore
    phone_number: str
    terms_and_privacy_accepted: bool

    @field_validator("phone_number")
    def validate_phone_number(cls, v):
        try:
            parsed_number = phonenumbers.parse(v, None)

            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number")

            # * Format the number in E.164 format
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException as err:
            raise ValueError("Invalid phone number format") from err


class UserUpdateRequest(BaseModel):
    first_name: constr(min_length=4, max_length=50) | None  # type: ignore
    last_name: constr(min_length=2, max_length=50) | None  # type: ignore


class UserLoginRequest(BaseModel):
    email: str
    password: str


class OAuthPayload(BaseModel):
    code: str = Field(..., min_length=1)
    code_verifier: str = Field(..., min_length=1)


class UserRefreshTokenRequest(BaseModel):
    refresh_token: str


class VerificationType(str, Enum):
    EMAIL = "EMAIL"
    PHONE_NUMBER = "PHONE_NUMBER"


class UserVerificationRequest(BaseModel):
    payload: str
    otp: str
    type: VerificationType


class ResendUserVerificationRequest(BaseModel):
    payload: str
    type: VerificationType


class UserPasswordResetRequest(BaseModel):
    email: EmailStr


class UserPasswordResetVerifyRequest(BaseModel):
    password: str
    otp: str

    @validator("password")
    def hash_and_validate_password(cls, value: str) -> str:
        try:
            return hash_password(value)
        except UserPasswordConstraintError as error:
            raise RequestValidationError(errors=[{"loc": ["body", "password"], "msg": error.message}]) from error
