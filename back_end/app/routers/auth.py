from datetime import UTC, datetime, timedelta
from typing import cast
from urllib.parse import unquote as url_unquote
from uuid import uuid4

import httpx
from aiosmtplib import SMTP
from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from redis import Redis
from redis.asyncio import Redis as RedisAsync
from sqlmodel import Session, func, select

from app.config import CLIENT_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
from app.log_config import logger
from app.mail import EmailDetails, get_smtp_client, send_mail
from app.models.server_response import ServerResponse
from app.models.user.base import (
    OAuthPayload,
    RefreshToken,
    ResendUserVerificationRequest,
    User,
    UserCreateRequest,
    UserLoginRequest,
    UserPasswordResetRequest,
    UserPasswordResetVerifyRequest,
    UserRefreshTokenRequest,
    UserVerificationRequest,
    UserWithRoles,
    VerificationType,
    check_password,
    hash_password,
)
from app.models.user.repo import deactivate_refresh_token, get_user_by_email, get_user_subscription
from app.models.user.role import RoleEnum
from app.models.user.user_role import UserRole
from app.models.user.user_subscription import UserSubscription
from app.resources import create_or_update_tag_counter, get_db, get_redis_async, get_user_with_roles, is_demo_account
from app.security import TokenData, create_access_token, encode_sha256
from app.utils import generate_otp, mask_email, serialize_sqlmodel
from app.services import EmailGenerator
from app.schemas.email_generator import EmailGeneratorSignUpData, EmailGeneratorResetPasswordData

router = APIRouter()


@router.get("/user")
async def get_authenticated_user(
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
):
    # * Get user subscription
    user_subscription = await run_in_threadpool(get_user_subscription, session=session, user=user.user)

    serialized_user_subscription = None
    if user_subscription:
        serialized_user_subscription = serialize_sqlmodel(user_subscription)

    return ServerResponse(data={**user.model_dump(), "user_subscription": serialized_user_subscription})


@router.post(path="/login")
async def login(
    user_request: UserLoginRequest,
    session: Session = Depends(get_db),
    redis: RedisAsync = Depends(get_redis_async),
):
    user: User | None = get_user_by_email(session=session, email=user_request.email)

    if user is None or user.id is None:
        logger.warning(f"User with email {user_request.email} does not exist")
        return ServerResponse(error="Invalid user details", status_code=400)

    # * Check is email is verified
    if not user.is_email_verified:
        logger.warning(f"User {user.id}::{user.email} email not verified")
        return ServerResponse(error="Email not verified", errors=["User must verify email to login", f"Check email sent at {mask_email(user.email)}"], status_code=401)

    demo_account = is_demo_account(email=user.email)

    if demo_account:
        access_token = create_access_token(data=TokenData(user_id=user.id, email=user.email), expires_delta=timedelta(minutes=30))
        x_tag, _ = await create_or_update_tag_counter(redis=redis)
        return ServerResponse(data={"user": user.model_dump(), "access_token": access_token, "demo_user": True}, headers={"X-Tag": x_tag})

    if user.password is None:
        # * Login using password is not allowed for this user, use oauth route
        return ServerResponse(error="Password not set", errors=["User other login methods for password-less login"], status_code=401)

    is_password_valid = check_password(plain_password=user_request.password, hashed_password=user.password)

    if not is_password_valid or user.id is None:
        logger.warning(f"User with email {user_request.email} incorrect password")
        return ServerResponse(error="Invalid user details", status_code=400)

    # * Update the last login
    user.last_login = datetime.now(UTC)

    access_token = create_access_token(data=TokenData(user_id=user.id, email=user.email), expires_delta=timedelta(hours=1))
    refresh_token = encode_sha256(source_data=f"{user.id}::{user.email}")

    session.add(instance=RefreshToken(user_id=user.id, token=refresh_token, expires_at=datetime.now(UTC) + timedelta(days=90), ip_address=None, device_info=None))
    session.commit()

    return ServerResponse(data={"user": user.model_dump(), "access_token": access_token, "refresh_token": refresh_token})


@router.post(path="/logout")
async def logout(
    refresh_token_request: UserRefreshTokenRequest,
    user: UserWithRoles = Depends(get_user_with_roles(required_roles=[RoleEnum.USER])),
    session: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_async),
):
    deactivate_refresh_token(session=session, user=user.user, refresh_token=refresh_token_request.refresh_token)

    await redis.delete(f"user:{user.user.id}")

    return ServerResponse(status_code=204)


@router.post(path="/refresh-token")
async def get_access_token(refresh_token_request: UserRefreshTokenRequest, session: Session = Depends(get_db)):
    refresh_token: RefreshToken | None = session.exec(select(RefreshToken).where(RefreshToken.token == refresh_token_request.refresh_token)).first()

    if refresh_token is None:
        logger.info("Invalid refresh token")
        return ServerResponse(error="Invalid refresh token", status_code=401)

    user: User = refresh_token.user

    # * Update the last login
    refresh_token.user.last_login = datetime.now(UTC)
    session.commit()

    access_token = create_access_token(data=TokenData(user_id=cast(int, user.id), email=user.email), expires_delta=timedelta(hours=1))

    return ServerResponse(data={"user": user.model_dump(), "access_token": access_token})


@router.post(path="/signup")
async def signup(user_request: UserCreateRequest, session: Session = Depends(get_db), mail_client: SMTP = Depends(get_smtp_client)):
    try:
        logger.info(f"Signup request with email {user_request.email}")
        existing_user: User | None = session.exec(select(User).where(User.email == user_request.email)).first()  # pyright: ignore [reportGeneralTypeIssues]
        if existing_user:
            logger.info(f"User with email {user_request.email} already exists")
            return ServerResponse(error="Email already exists", status_code=400)

        user = User(**user_request.model_dump())
        user.password = hash_password(user_request.password)

        # * Generate email otp
        user.email_otp = generate_otp()

        session.add(user)
        session.commit()
        session.refresh(user)

        # * Assign USER role
        if user.id:
            user_data = []
            user_data.append(UserRole(user_id=user.id, role_id=RoleEnum.USER.value))
            user_data.append(UserSubscription(user_id=user.id, subscription_type_id=4, end_date=datetime.now(UTC)))

            session.add_all(user_data)
            session.commit()

        subject = "Please verify your account"
        content = EmailGenerator().generate_sign_up(data=EmailGeneratorSignUpData(
            first_name=user.first_name,
            subject=subject,
            otp=user.email_otp,
        ))
        email_message = EmailDetails(to=user.email, subject=subject, content=content)

        await send_mail(mail_client=mail_client, email_details=email_message)
        logger.info(f"Email sent to {user.email} for email verification")
    except Exception as e:
        return ServerResponse(error=str(e), status_code=500)

    return ServerResponse(data=user, status_code=201)


@router.post(path="/google")
async def authenticate_or_login_with_google(payload: OAuthPayload, session: Session = Depends(get_db)):
    logger.debug(f"Google code: {payload.code} and verifier {payload.code_verifier}")

    try:
        # * Exchange authorization code for access token
        token_data = {
            "code": url_unquote(payload.code),
            "code_verifier": payload.code_verifier,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI,
        }
        async with httpx.AsyncClient() as client:
            token_response = await client.post("https://oauth2.googleapis.com/token", data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
            access_token = token_info["access_token"]

        # * Get user profile from Google
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)
            response.raise_for_status()
            google_user = response.json()

        logger.info(f"Google user {google_user['sub']}::{google_user['email']} found, looking up locally")

        # * Check if the user already exists
        user = session.exec(select(User).where(func.lower(User.email) == google_user["email"].lower())).first()

        if not user:
            logger.info(f"User with {google_user['sub']}::{google_user['email']} not found, creating new user")

            # * Create a new user
            name_parts = google_user["name"].split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            user = User(email=google_user["email"], first_name=first_name, password=None, last_name=last_name, profile_picture=google_user["picture"], is_email_verified=True)
            session.add(user)
            session.commit()
            session.refresh(user)

            # * Assign base role as USER
            user_role = UserRole(user_id=cast(int, user.id), role_id=RoleEnum.USER.value)
            session.add(user_role)

            # * Assign free subscription
            current_date = datetime.now(UTC)
            end_date = current_date + timedelta(days=30)
            user_subscription = UserSubscription(
                start_date=current_date,
                end_date=end_date,
                user_id=cast(int, user.id),
                subscription_type_id=1,
            )
            session.add(user_subscription)
            session.commit()

        access_token = create_access_token(data=TokenData(user_id=cast(int, user.id), email=user.email), expires_delta=timedelta(hours=1))
        refresh_token = encode_sha256(source_data=f"{user.id}::{user.email}")

        session.add(instance=RefreshToken(user_id=cast(int, user.id), token=refresh_token, expires_at=datetime.now(UTC) + timedelta(days=90), ip_address=None, device_info=None))
        session.commit()

        return ServerResponse(data={"user": {**user.model_dump()}, "access_token": access_token, "refresh_token": refresh_token})

    except httpx.HTTPStatusError as exc:
        logger.error(f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}")
        return ServerResponse(error=exc.response.json()["error_description"], status_code=exc.response.status_code)
    except Exception as e:
        logger.error(str(e))
        return ServerResponse(error="Error at our end", status_code=502)


@router.post(path="/verify")
async def verify_user(user_verification_request: UserVerificationRequest, session: Session = Depends(get_db)):
    logger.info(f"{user_verification_request.type} for user with email {user_verification_request.payload}")

    def get_user_by_verification_type(type: VerificationType) -> User | None:  # pyright: ignore [reportGeneralTypeIssues]
        user: User | None = None  # pyright: ignore [reportGeneralTypeIssues]
        match type:
            case VerificationType.EMAIL:
                user = session.exec(select(User).where(User.email == user_verification_request.payload, User.email_otp == user_verification_request.otp)).first()
                if user:
                    user.email_otp = None
                    user.is_email_verified = True
            case _:
                user = session.exec(select(User).where(User.email == user_verification_request.payload, User.phone_number_otp == user_verification_request.otp)).first()
                if user:
                    user.phone_number_otp = None
                    user.is_phone_number_verified = True
        return user

    user: User | None = get_user_by_verification_type(user_verification_request.type)  # pyright: ignore [reportGeneralTypeIssues]

    if user is None:
        logger.warn(f"User with email {user_verification_request.payload} does not exist or provided invalid otp")
        return ServerResponse(error="Invalid user details or otp provided", status_code=400)

    session.add(user)
    session.commit()
    session.refresh(user)

    return ServerResponse(data=user)


@router.post(path="/resend/otp")
async def resend_user_verification(user_verification_request: ResendUserVerificationRequest, session: Session = Depends(get_db), mail_client: SMTP = Depends(get_smtp_client)):
    logger.info(f"{user_verification_request.type} resend request for user with email {user_verification_request.payload}")

    user: User | None = None  # pyright: ignore [reportGeneralTypeIssues]

    match user_verification_request.type:
        case VerificationType.EMAIL:
            user = session.exec(select(User).where(User.email == user_verification_request.payload, User.is_email_verified == False)).first()  # noqa: E712
        case _:
            user = session.exec(select(User).where(User.phone_number == user_verification_request.payload, User.is_phone_number_verified == False)).first()  # noqa: E712

    if not user:
        # * Do not give indication that user does not exist
        # * This is to discourage bad actors
        logger.warn(f"No user with {user_verification_request.type} {user_verification_request.payload} exist or is already verified")
        return ServerResponse(data=None)

    # * Generate new email otp
    # todo add phone otp later
    user.email_otp = generate_otp()

    session.add(user)
    session.commit()
    session.refresh(user)

    subject = "Please verify your account"
    content = EmailGenerator().generate_sign_up(data=EmailGeneratorSignUpData(
        first_name=user.first_name,
        subject=subject,
        otp=user.email_otp,
    ))
    email_message = EmailDetails(to=user.email, subject=subject, content=content)

    await send_mail(mail_client=mail_client, email_details=email_message)
    logger.info(f"Email sent to {user.email} for email verification")

    return ServerResponse(data=None)


@router.post(path="/password-reset/init")
async def init_password_reset(user_password_reset_request: UserPasswordResetRequest, session: Session = Depends(get_db), mail_client: SMTP = Depends(get_smtp_client)):
    logger.info(f"Password reset request init request for {user_password_reset_request.email}")

    user: User | None = session.exec(select(User).where(User.email == user_password_reset_request.email, User.is_email_verified == True)).first()  # noqa: E712 # pyright: ignore [reportGeneralTypeIssues]

    if user is None:
        logger.info(f"Password reset request init request for {user_password_reset_request.email} did not succeed. Invalid email")
        return ServerResponse(data=None)

    # * For now reuse email_otp
    user.email_otp = f"{str(uuid4())}-{str(uuid4())}".replace("-", "")

    session.add(user)
    session.commit()
    session.refresh(user)

    subject = "Password reset link"
    content = EmailGenerator().generate_reset_password(data=EmailGeneratorResetPasswordData(
        first_name=user.first_name,
        subject=subject,
        reset_link=f"{CLIENT_URL}/{user.email_otp}"
    ))
    email_message = EmailDetails(to=user.email, subject=subject, content=content)

    await send_mail(mail_client=mail_client, email_details=email_message)
    logger.info(f"Email sent to {user.email} for email verification")

    return ServerResponse(data=None)


@router.post(path="/password-reset")
async def rest_password(user_password_reset_verify_request: UserPasswordResetVerifyRequest, session: Session = Depends(get_db), mail_client: SMTP = Depends(get_smtp_client)):
    user: User | None = session.exec(select(User).where(User.is_email_verified == True, User.email_otp == user_password_reset_verify_request.otp)).first()  # noqa: E712 # pyright: ignore [reportGeneralTypeIssues]

    if user is None:
        return ServerResponse(error="Invalid user", status_code=400)

    user.password = user_password_reset_verify_request.password
    user.email_otp = None

    session.add(user)
    session.commit()
    session.refresh(user)

    subject = "Password reset link"
    content = EmailGenerator().generate_reset_password(data=EmailGeneratorResetPasswordData(
        first_name=user.first_name,
        subject=subject,
        reset_link=f"{CLIENT_URL}/{user.email_otp}"
    ))
    email_message = EmailDetails(to=user.email, subject=subject, content=content)

    await send_mail(mail_client=mail_client, email_details=email_message)
    logger.info(f"Email sent to {user.email} for email verification")

    return ServerResponse(data=None)
