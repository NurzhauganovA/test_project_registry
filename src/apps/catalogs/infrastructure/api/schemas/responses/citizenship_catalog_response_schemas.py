from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class CitizenshipCatalogFullResponseSchema(BaseModel):
    id: int

    country_code: str = Field(..., description="Citizenship country code (ISO)")
    name: str = Field(
        default_factory=str,
        description="Citizenship name in default language",
    )
    lang: str = Field(..., description="Citizenship default language")
    name_locales: Optional[dict] = Field(
        None,
        description="Citizenship additional languages for the 'name' field",
    )

    changed_at: datetime = Field(..., description="Date of the last update")
    created_at: datetime = Field(..., description="Date of the creation")

    model_config = SettingsConfigDict(from_attributes=True)


class CitizenshipCatalogPartialResponseSchema(BaseModel):
    id: int

    country_code: str = Field(..., description="Citizenship country code (ISO)")
    name: str = Field(
        default_factory=str,
        description="Patient context attribute name in default language",
    )
    lang: str = Field(..., description="Patient context attribute default language")

    changed_at: datetime = Field(..., description="Date of the last update")
    created_at: datetime = Field(..., description="Date of the creation")

    model_config = SettingsConfigDict(from_attributes=True)


class MultipleCitizenshipSchema(BaseModel):
    items: List[
        Union[
            CitizenshipCatalogFullResponseSchema,
            CitizenshipCatalogPartialResponseSchema,
        ]
    ]
    pagination: PaginationMetaDataSchema
