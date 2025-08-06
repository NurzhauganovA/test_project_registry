from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.middlewares.i18n_middleware import LocalesTranslationMiddleware
from src.shared.exception_handlers import generic_exception_handler


def FastAPIResource(
    routers: List[Dict[str, Any]],
    exception_handlers: List[Dict[str, Any]],
    project_name: str,
    project_version: str,
    api_prefix: str,
    debug: bool,
    enable_docs: bool,
    backend_cors_origins: List[str],
) -> FastAPI:
    app = FastAPI(
        title=project_name,
        version=project_version,
        debug=debug,
        root_path="/registry-module-orkendeu-project",
        openapi_url="/openapi.json" if enable_docs else None,
        docs_url="/docs" if enable_docs else None,
    )

    # CORS
    if backend_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=backend_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # i18n middleware
    app.add_middleware(LocalesTranslationMiddleware)

    # Exception handlers
    for handler_dict in exception_handlers:
        handler = handler_dict["handler"]
        error_it_handles = handler_dict["error"]
        app.add_exception_handler(error_it_handles, handler)

    # Universal catch-all exception handler if nothing else above catches
    app.add_exception_handler(Exception, generic_exception_handler)

    # Routers
    for router_dict in routers:
        router: APIRouter = router_dict["router"]
        tags = router_dict["tags"]
        app.include_router(router, prefix=api_prefix, tags=tags)

    return app
