import logging
import os
from typing import Literal, cast

from dotenv import load_dotenv

load_dotenv()

ENV: str = os.getenv("ENV", "production").lower()

if ENV not in ("production", "development", "testing"):
    raise ValueError(f"ENV={ENV} is not valid. It should be 'production', 'development' or 'testing'")

DEBUG: bool = ENV != "production"

TESTING: bool = ENV == "testing"
DEVELOPMENT: bool = ENV == "development"

LOG_LEVEL = logging.INFO if ENV == "production" else logging.DEBUG

os.environ["LOGURU_LEVEL"] = os.getenv("LOG_LEVEL") or (DEBUG and "DEBUG") or "INFO"
os.environ["LOGURU_DEBUG_COLOR"] = "<fg #777>"

__SERVER_VERSION = "1.4.0"

# * NLTK
NLTK_DATA_PATH = "/tmp/nltk_data"

# * Redis config
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
if all([REDIS_HOST, REDIS_PORT]):
    REDIS_ENDPOINT = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
else:
    REDIS_ENDPOINT = "redis://127.0.0.1:6379/0"

# * Database config
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL: str | None = None

if all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB]):
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# * JWT config
JWT_SECRET_KEY: str | None = os.getenv("JWT_SECRET_KEY")

# * Mail server config
MAIL_SMTP_HOSTNAME: str | None = os.getenv("MAIL_SMTP_HOSTNAME")
MAIL_SMTP_USERNAME: str | None = os.getenv("MAIL_SMTP_USERNAME")
MAIL_SMTP_PASSWORD: str | None = os.getenv("MAIL_SMTP_PASSWORD")
MAIL_SMTP_PORT: int = int(os.getenv("MAIL_SMTP_PORT", "465"))

# * MAIL config
MAIL_FROM_ADDRESS = "Fast Data Science <noreply@fastdatascience.net>"

# * Storage provider config
STORAGE_PROVIDER = cast(Literal["s3", "azure", "local"], os.getenv("STORAGE_PROVIDER", "local"))
BUCKET_OR_CONTAINER_NAME = os.getenv("BUCKET_OR_CONTAINER_NAME", "fds-cdn")
CDN_BUCKET_OR_CONTAINER_BASE_PATH = os.getenv("CDN_BUCKET_OR_CONTAINER_BASE_PATH", "cdn")

# * AWS config
DEFAULT_REGION = "eu-west-2"
DOCUMENT_PROCESSING_QUEUE_URL = "https://sqs.eu-west-2.amazonaws.com/017696512810/fds-fcnlp-document-processing-queue.fifo"

# * Azure storage config
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")

# * API prefix config
API_V1_STR: str = "/api/v1"

# * Client URL config
CLIENT_URL: str | None = os.getenv("CLIENT_URL")

# * Tika gRPC config
GRPC_HOST = os.getenv("GRPC_HOST")
GRPC_PORT = os.getenv("GRPC_PORT")
if all([GRPC_HOST, GRPC_PORT]):
    GRPC_ENDPOINT = f"{GRPC_HOST}:{GRPC_PORT}"
else:
    GRPC_ENDPOINT = "127.0.0.1:8888"

# * Google config for oAuth
GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: str | None = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI: str | None = os.getenv("GOOGLE_REDIRECT_URI")

# * Platform settings
DEMO_ACCOUNT_EMAIL: str | None = os.getenv("DEMO_ACCOUNT_EMAIL")
if not DEMO_ACCOUNT_EMAIL:
    DEMO_ACCOUNT_EMAIL = None

MAX_DEMO_ACCOUNT_FILE_PROCESSING_COUNT = int(os.getenv("MAX_DEMO_ACCOUNT_FILE_PROCESSING_COUNT", 3))

WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH", "/usr/bin/wkhtmltopdf")

# * DNS for the current server
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5000")

# * If the application is running with the public docker release
PUBLIC_DOCKER = os.getenv("PUBLIC_DOCKER", "false").lower() == "true"
PUBLIC_DOCKER_USER_PASSWORD = os.getenv("PUBLIC_DOCKER_USER_PASSWORD")
