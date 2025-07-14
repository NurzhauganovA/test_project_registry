from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class MedicalOrganizationCatalogFullResponseSchema(BaseModel):
    id: int

    name: str = Field(
        default_factory=str,
        description="Medical organization name in default language",
    )
    organization_code: str = Field(
        default_factory=str,
        description="Medical organization's internal organization code",
        alias="code",
    )
    address: str = Field(
        default_factory=str,
        description="Medical organization's address in default language",
    )
    lang: str = Field(..., description="Medical organization default language")

    name_locales: Optional[dict] = Field(
        None,
        description="Medical organization additional languages for the 'name' field",
    )
    address_locales: Optional[dict] = Field(
        None,
        description="Medical organization additional languages for the 'address' field",
    )

    changed_at: datetime = Field(..., description="Date of the last update")
    created_at: datetime = Field(..., description="Date of the creation")

    model_config = SettingsConfigDict(from_attributes=True)


class MedicalOrganizationCatalogPartialResponseSchema(BaseModel):
    id: int

    name: str = Field(
        default_factory=str,
        description="Medical organization name in default language",
    )
    organization_code: str = Field(
        default_factory=str,
        description="Medical organization's internal organization code",
    )
    address: str = Field(
        default_factory=str,
        description="Medical organization's address in default language",
    )
    lang: str = Field(..., description="Medical organization default language")

    changed_at: datetime = Field(..., description="Date of the last update")
    created_at: datetime = Field(..., description="Date of the creation")

    model_config = SettingsConfigDict(from_attributes=True)


class MultipleMedicalOrganizationsSchema(BaseModel):
    items: List[
        Union[
            MedicalOrganizationCatalogFullResponseSchema,
            MedicalOrganizationCatalogPartialResponseSchema,
        ]
    ]
    pagination: PaginationMetaDataSchema
