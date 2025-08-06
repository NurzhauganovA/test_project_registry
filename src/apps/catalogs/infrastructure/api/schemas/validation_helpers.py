from typing import Any, Dict

from src.core.i18n import _
from src.core.settings import project_settings
from src.shared.helpers.validation_helpers import validate_field_not_blank


def validate_lang_and_locales(values: Dict[str, Any]) -> Dict[str, Any]:
    lang = values.get("lang")
    default = project_settings.DEFAULT_LANGUAGE
    if lang is not None and lang != default:
        raise ValueError(
            _("Field 'lang' must be the default language: '%(DEFAULT)s'.")
            % {"DEFAULT": default}
        )

    locales = values.get("name_locales")
    if locales:
        allowed = set(project_settings.LANGUAGES) - {default}
        extra = set(locales) - allowed
        if extra:
            raise ValueError(
                _(
                    "Unsupported locale(s): %(EXTRA)s. Supported additional languages: %(ALLOWED)s."
                )
                % {
                    "EXTRA": sorted(extra),
                    "ALLOWED": sorted(allowed),
                }
            )
        for code, val in locales.items():
            validate_field_not_blank(val, f"name_locales['{code}']")

    return values


def validate_addresses_and_locales(values: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates that 'lang' is the default language and that both
    and 'address_locales' dictionaries contain only allowed locales and
    non-blank values.
    """
    lang = values.get("lang")
    default = "ru"
    if lang is not None and lang != default:
        raise ValueError(
            _("Field 'lang' must be the default language: '%(DEFAULT)s'.")
            % {"DEFAULT": default}
        )

    allowed = set({"ru", "kk", "en"}) - {default}

    address_locales = values.get("address_locales") or {}
    invalid_address = set(address_locales) - allowed
    if invalid_address:
        raise ValueError(
            _(
                "Unsupported locale(s) in address_locales: %(EXTRA)s. "
                "Supported additional languages: %(ALLOWED)s."
            )
            % {"EXTRA": sorted(invalid_address), "ALLOWED": sorted(allowed)}
        )
    for code, val in address_locales.items():
        validate_field_not_blank(val, f"address_locales['{code}']")

    return values
