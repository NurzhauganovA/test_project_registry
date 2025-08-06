from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from src.apps.catalogs.infrastructure.api.schemas.validation_helpers import (
    validate_lang_and_locales,
)
from src.core.settings import project_settings
from src.shared.helpers.validation_helpers import validate_field_not_blank


class BaseRequest(BaseModel):
    id: Optional[int] = Field(None, description="Unique citizenship ID")
    country_code: Optional[str] = Field(None, max_length=10, description="Country code (ISO)")
    name: Optional[str] = Field(None, max_length=100, description="Name on default language")
    lang: Optional[str] = Field(
        None,
        max_length=5,
        description="Default language",
    )
    name_locales: Optional[Dict[str, str]] = Field(
        default=None, description="A dictionary of the additional name locales"
    )

    @field_validator("name", mode="before")
    def _check_name_not_blank(cls, v: Any) -> Any:
        if v is not None:
            validate_field_not_blank(v, "name")
        return v

    @field_validator("country_code", mode="before")
    def _check_country_code_not_blank(cls, v: Any) -> Any:
        if v is not None:
            validate_field_not_blank(v, "country_code")
        return v

    _check_lang_and_locales = model_validator(mode="before")(validate_lang_and_locales)


class AddCitizenshipSchema(BaseRequest):
    country_code: str = Field(..., max_length=10, description="Country code (ISO)")
    name: str = Field(..., max_length=100, description="Name on default language")
    lang: str = Field(
        default=project_settings.DEFAULT_LANGUAGE,
        max_length=5,
        description="Default language",
    )
    name_locales: Dict[str, str] = Field(
        default_factory=dict,
        description="A dictionary of the additional name locales"
    )


class UpdateCitizenshipSchema(BaseRequest):
    pass


class DeleteCitizenshipSchema(BaseModel):
    id: int
