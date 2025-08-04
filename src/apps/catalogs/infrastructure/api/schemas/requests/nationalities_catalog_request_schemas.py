from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from src.apps.catalogs.infrastructure.api.schemas.validation_helpers import (
    validate_lang_and_locales,
)
from src.core.settings import project_settings
from src.shared.helpers.validation_helpers import validate_field_not_blank


class NationalityBaseRequestSchema(BaseModel):
    id: Optional[int] = Field(
        None, description="Unique identifier (provide only if needed to override ID)"
    )
    name: Optional[str] = Field(
        None, max_length=100, description="Name on default language"
    )
    lang: Optional[str] = Field(None, max_length=5, description="Default language")
    name_locales: Optional[Dict[str, str]] = Field(
        None, description="A dictionary of the additional name locales"
    )

    @field_validator("name", mode="before")
    def _check_name_not_blank(cls, v: Any) -> Any:
        if v is not None:
            validate_field_not_blank(v, "name")
        return v

    _check_lang_and_locales = model_validator(mode="before")(validate_lang_and_locales)


class AddNationalitySchema(NationalityBaseRequestSchema):
    name: str = Field(..., max_length=100, description="Name on default language")
    lang: str = Field(
        max_length=5,
        default=project_settings.DEFAULT_LANGUAGE,
        description="Default language",
    )
    name_locales: Dict[str, str] = Field(
        default_factory=dict, description="A dictionary of the additional name locales"
    )


class UpdateNationalitySchema(NationalityBaseRequestSchema):
    pass


class DeleteNationalitySchema(BaseModel):
    id: int
