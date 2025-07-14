import json

from fastapi import Request
from fastapi.responses import JSONResponse

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
