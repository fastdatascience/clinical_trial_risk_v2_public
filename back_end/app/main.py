import asyncio
import gzip
from io import BytesIO

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, StreamingResponse
from hypercorn import Config
from hypercorn.asyncio import serve
from pydantic import ValidationError
from starlette.middleware.gzip import GZipMiddleware
from starlette.types import Receive, Scope, Send

from app.models.server_response import ServerResponse
from app.security import JWTUserExceptionError

from . import config, log_config
from .resources import format_validation_errors, lifespan
from .routers import router

__api_description__ = """
Base server response shape
``` json
{
    "timestamp": long,
    "data": {},
    "error": null or string,
    "errors": null or [strings]
}
```
"""

app = FastAPI(title="clinical_trials_backend", debug=config.DEBUG, default_response_class=ORJSONResponse, lifespan=lifespan, description=__api_description__)

# * Configure CORS middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def gzip_middleware(request: Request, call_next):
    """
    Middleware to gzip responses from endpoints marked with `__enable_gzip`
    """
    response = await call_next(request)

    # * Check if the route is marked for GZIP compression
    endpoint = request.scope.get("endpoint")
    if endpoint and getattr(endpoint, "__enable_gzip", False):
        # * Collect the original response body (non-streaming only)
        original_body = b""
        async for chunk in response.body_iterator:
            original_body += chunk

        # * Compress the response using gzip
        gzip_buffer = BytesIO()
        with gzip.GzipFile(mode="wb", fileobj=gzip_buffer) as gzip_file:
            gzip_file.write(original_body)
        compressed_content = gzip_buffer.getvalue()

        # * Create a new Response with compressed content
        new_response = Response(
            content=compressed_content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
        # * Add GZIP-specific headers
        new_response.headers["Content-Encoding"] = "gzip"
        new_response.headers["Content-Length"] = str(len(compressed_content))
        return new_response

    return response


# * Custom exception handler
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_: Request, exc: RequestValidationError):
    errors = format_validation_errors(exc)
    return ServerResponse(data=None, error="Validation Error", errors=errors, status_code=422)


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(_: Request, exc: ValidationError):
    errors = format_validation_errors(exc)
    return ServerResponse(data=None, error="Validation Error Invalid request body", errors=errors, status_code=400)


@app.exception_handler(ValueError)
async def value_error_exception_handler(_: Request, exc: ValueError):
    errors = format_validation_errors(exc.__str__())
    return ServerResponse(data=None, error="Validation Error Invalid request body", errors=errors, status_code=400)


@app.exception_handler(JWTUserExceptionError)
async def jwt_user_exception_handler(_: Request, exc: JWTUserExceptionError):
    return ServerResponse(data=None, error=exc.error, errors=exc.errors, status_code=exc.status_code)


@app.exception_handler(Exception)
async def general_exception_handler(_: Request, exc: Exception):
    # * Default to 500 for unknown exceptions
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", str(exc))

    return ServerResponse(data=None, errors=[detail], status_code=status_code)


app.include_router(router=router, prefix=config.API_V1_STR)

if __name__ == "__main__":
    log_config.logger.setLevel(level=config.LOG_LEVEL)

    _config = Config()
    asyncio.run(serve(app, _config))  # type: ignore
