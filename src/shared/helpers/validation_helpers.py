import re
from datetime import date

from src.core.i18n import _


def validate_field_not_blank(value: str, field_label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(_("%(FIELD)s must not be empty." % {"FIELD": field_label}))

    return value


def validate_date_of_birth(date_of_birth: date) -> date:
    today = date.today()
    if date_of_birth > today:
        raise ValueError(_("Date of birth cannot be in the future."))

    return date_of_birth


def validate_iin(iin: str) -> str:
    if not re.fullmatch(r"^\d{12}$", iin):
        raise ValueError(_("IIN must be exactly 12 digits."))

    return iin


def validate_phone_number(phone: str) -> str:
    pattern = re.compile(r"^7\d{10}$")
    if not pattern.fullmatch(phone):
        raise ValueError(_("Invalid phone number format."))

    return phone


def validate_pagination_limit(limit: int) -> int:
    if limit < 1:
        raise ValueError(_("Pagination limit must be greater or equal to 1."))
    if limit > 100:
        raise ValueError(_("Pagination limit must be less or equal to 100."))

    return limit


def validate_pagination_page(page: int) -> int:
    if page < 1:
        raise ValueError(_("Pagination page must be greater or equal to 1."))

    return page


def normalize_empty(value):
    """
    Normalize JSONB field value for PATCH requests.
    Returns None for None, or empty list. Returns value otherwise.
    """
    if value is None or value == []:
        return None

    return value
