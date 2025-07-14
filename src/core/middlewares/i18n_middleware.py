from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.i18n import set_locale
from src.core.settings import project_settings


class LocalesTranslationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        lang = request.headers.get("accept-language", project_settings.DEFAULT_LANGUAGE)
        if lang not in project_settings.LANGUAGES:
            lang = project_settings.DEFAULT_LANGUAGE

        set_locale(lang)

        response = await call_next(request)
        return response
