import json

from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.logger import logger
from src.shared.exceptions import (
    ApplicationError,
    AuthServiceError,
    DependencyError,
    RpnIntegrationServiceError,
)


async def application_error_handler(request: Request, exc: ApplicationError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def auth_service_error_handler(request: Request, exc: AuthServiceError):
    error_raw = exc.detail
    try:
        parsed = json.loads(error_raw)
    except (TypeError, json.JSONDecodeError):
        # If it's not a JSON - leave it as it is
        content = error_raw
    else:
        content = parsed

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


async def rpn_integration_error_handler(
    request: Request, exc: RpnIntegrationServiceError
):
    error_raw = exc.detail
    try:
        parsed = json.loads(error_raw)
    except (TypeError, json.JSONDecodeError):
        # If it's not a JSON - leave it as it is
        content = error_raw
    else:
        content = parsed

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


async def dependencies_error_handler(request: Request, exc: DependencyError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions globally and return a generic error response.

    This exception handler captures all unhandled exceptions that occur during
    request processing, logs the exception details with traceback for diagnostics,
    and returns a generic HTTP 500 Internal Server Error response to the client.

    Args:
        request (Request): The incoming FastAPI request object.
        exc (Exception): The unhandled exception instance.

    Returns:
        JSONResponse: A JSON response with HTTP status code 500 and an error message.

    This handler should be registered as the last exception handler to catch any exceptions
    not handled by more specific handlers.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please, try again later."},
    )
