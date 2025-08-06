from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from src.apps.catalogs.infrastructure.api.schemas.validation_helpers import (
    validate_addresses_and_locales,
    validate_lang_and_locales,
)
from src.core.settings import project_settings
from src.shared.helpers.validation_helpers import validate_field_not_blank


class BaseMedicalOrganizationSchema(BaseModel):
    id: Optional[int] = Field(None, description="Unique medical organization ID")
    name: Optional[str] = Field(None, max_length=256, description="Name on default language")
    organization_code: Optional[str] = Field(
        None, max_length=20, description="Medical organization internal code"
    )
    address: Optional[str] = Field(None, max_length=256, description="Address on default language")
    lang: Optional[str] = Field(None, max_length=5, description="Default language")

    name_locales: Optional[Dict[str, str]] = Field(
        None, description="A dictionary of the additional name locales"
    )
    address_locales: Optional[Dict[str, str]] = Field(
        None, description="A dictionary of the additional address locales"
    )

    @field_validator("name", mode="before")
    def _check_name_not_blank(cls, v: Any) -> Any:
        if v is not None:
            validate_field_not_blank(v, "name")
        return v

    @field_validator("organization_code", mode="before")
    def _check_code_not_blank(cls, v: Any) -> Any:
        if v is not None:
            validate_field_not_blank(v, "organization_code")
        return v

    @field_validator("address", mode="before")
    def _check_address_not_blank(cls, v: Any) -> Any:
        if v is not None:
            validate_field_not_blank(v, "address")
        return v

    _check_lang_and_locales = model_validator(mode="before")(validate_lang_and_locales)
    _validate_addresses_and_locales = model_validator(mode="before")(validate_addresses_and_locales)


class AddMedicalOrganizationSchema(BaseMedicalOrganizationSchema):
    name: str = Field(..., max_length=256, description="Name on default language")
    organization_code: str = Field(..., max_length=20, description="Medical organization internal code")
    address: str = Field(..., max_length=256, description="Address on default language")
    lang: str = Field(
        max_length=5,
        default=project_settings.DEFAULT_LANGUAGE,
        description="Default language",
    )
    name_locales: Dict[str, str] = Field(
        default_factory=dict, description="A dictionary of the additional name locales"
    )
    address_locales: Dict[str, str] = Field(
        default_factory=dict, description="A dictionary of the additional address locales"
    )


class UpdateMedicalOrganizationSchema(BaseMedicalOrganizationSchema):
    pass


class DeleteMedicalOrganizationSchema(BaseModel):
    id: int
