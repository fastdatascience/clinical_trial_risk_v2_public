import asyncio

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
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


class ExcludeStreamGZipMiddleware(GZipMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers_dict = {k.lower(): v for k, v in scope["headers"]}
        accept_encoding = headers_dict.get(b"accept-encoding", b"").decode("utf-8")
        content_type = headers_dict.get(b"content-type", b"").decode("utf-8")

        if "text/event-stream" in content_type:
            await self.app(scope, receive, send)
            return

        # * If the client did NOT request gzip, skip compression
        if "gzip" not in accept_encoding.lower():
            await self.app(scope, receive, send)
            return

        await super().__call__(scope, receive, send)


# app.add_middleware(ExcludeStreamGZipMiddleware, minimum_size=1000)


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
