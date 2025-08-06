import contextvars
import gettext
from pathlib import Path
from typing import Optional

_locale_ctx = contextvars.ContextVar("current_locale", default="en")
_translators = {}


def set_locale(lang: str):
    from src.core.settings import project_settings

    if lang not in project_settings.LANGUAGES:
        lang = project_settings.DEFAULT_LANGUAGE

    _locale_ctx.set(lang)


def get_locale():
    return _locale_ctx.get()


def get_translator(lang: Optional[str] = None):
    lang = lang or get_locale()
    if lang not in _translators:
        base_dir = Path(__file__).resolve().parent.parent.parent
        localedir = base_dir / "locale"
        _translators[lang] = gettext.translation(
            "messages", localedir=localedir, languages=[lang], fallback=True
        )

    return _translators[lang].gettext


def _(message, *args, **kwargs):
    return get_translator()(message, *args, **kwargs)
