import base64
import hashlib
import json
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ValidationError
from redis.asyncio import Redis as RedisAsync
from sqlmodel import select

from app import config
from app.log_config import logger
from app.models.user.base import User
from app.models.user.role import Role
from app.models.user.user_role import UserRole
from app.utils import mask_email

from .config import JWT_SECRET_KEY
from .database import SessionLocal

if JWT_SECRET_KEY is None:
    raise Exception("JWT secret not set, check .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# * Initialize Redis asynchronously
redis = RedisAsync.from_url(config.REDIS_ENDPOINT)


class TokenData(BaseModel):
    user_id: int
    email: str


class JWTUserExceptionError(Exception):
    def __init__(self, status_code: int, error: str, errors: list[str] | None = None):
        self.status_code = status_code
        self.error = error
        self.errors = errors


def create_access_token(data: TokenData, expires_delta: timedelta) -> str:
    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(**payload)
    except (jwt.PyJWTError, ValidationError):
        return None


def encode_sha256(source_data: str, key: str = "secret_sauce") -> str:
    nonce = secrets.token_hex(16)
    combined_data = nonce + source_data
    encoded_data = combined_data.encode("utf-8")

    hmac = hashlib.sha256(key.encode())
    hmac.update(encoded_data)
    hash_digest = hmac.digest()

    return base64.urlsafe_b64encode(encoded_data + b"!" + hash_digest).decode().rstrip("=")


def decode_sha256(encoded_data: str, key: str = "secret_sauce") -> str:
    # * Add padding
    encoded_data += "=" * ((4 - len(encoded_data) % 4) % 4)

    decoded_data = base64.urlsafe_b64decode(encoded_data)

    encoded_part, hash_part = decoded_data.rsplit(b"!", 1)

    hmac = hashlib.sha256(key.encode())
    hmac.update(encoded_part)
    calculated_hash = hmac.digest()

    if calculated_hash != hash_part:
        raise ValueError("Hash verification failed")

    # * Remove the first 32 characters (nonce) and return the data part
    return encoded_part[32:].decode("utf-8")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)

        if not credentials:
            raise JWTUserExceptionError(status_code=401, error="Could not validate credentials. No token provided", errors=["No authentication credentials provided."])

        token_data = self.verify_jwt(credentials.credentials)

        if not token_data:
            raise JWTUserExceptionError(status_code=401, error="Invalid or expired token", errors=["The provided token is invalid or has expired."])

        user_id = token_data.user_id
        redis_key = f"user:{user_id}"

        logger.debug(f"Attempting to retrieve user data from Redis with key: {redis_key}")

        # * Attempt to retrieve user data from Redis
        cached_user_json = await redis.get(redis_key)

        if cached_user_json:
            try:
                user_with_roles_data = json.loads(cached_user_json)
                request.state.user_data = user_with_roles_data
                logger.debug(f"User data for user_id {user_id} retrieved from cache")
                return credentials
            except json.JSONDecodeError:
                # * Proceed to fetch from DB if cache is corrupted
                logger.warning(f"Failed to decode cached user data for user_id: {user_id}")

        # * Fetch from database if not in cache or cache is corrupted
        with SessionLocal() as session:
            user_query = select(User).where(User.id == user_id)
            user: User | None = session.exec(user_query).first()

            if not user:
                logger.warning(f"User {user_id} does not exist")
                raise JWTUserExceptionError(status_code=401, error="Could not validate credentials", errors=["User does not exist."])

            # * Check if email is verified
            if not user.is_email_verified:
                logger.warning(f"User {user_id} email not verified")
                raise JWTUserExceptionError(
                    status_code=401, error="Email not verified", errors=["User must verify email to login", f"Check email sent at {mask_email(user.email)}"]
                )

            # * Serialize user data for caching
            user_data = user.model_dump()
            user_roles = session.exec(select(Role).join(UserRole).where(UserRole.user_id == user.id)).all()
            roles_data = [role.model_dump() for role in user_roles]
            user_with_roles_data = {"user": user_data, "user_roles": roles_data}
            user_with_roles_data_json = jsonable_encoder(user_with_roles_data)

            # * Cache the serialized user data in Redis for 10 minutes (600 seconds)
            await redis.set(redis_key, json.dumps(user_with_roles_data_json), ex=600)
            logger.debug(f"User data for user_id {user_id} cached in Redis")

            # * Attach user data to request state
            request.state.user_data = user_with_roles_data

        return credentials

    def verify_jwt(self, jwt_token: str) -> TokenData | None:
        try:
            return decode_access_token(jwt_token)
        except (jwt.PyJWTError, ValidationError):
            return None
