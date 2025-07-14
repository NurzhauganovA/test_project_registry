from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class NationalityCatalogFullResponseSchema(BaseModel):
    id: int

    name: str = Field(
        default_factory=str,
        description="Nationality name in default language",
    )
    lang: str = Field(..., description="Nationality default language")
    name_locales: Optional[dict] = Field(
        None,
        description="Nationality additional languages for the 'name' field",
    )

    changed_at: datetime = Field(..., description="Date of the last update")
    created_at: datetime = Field(..., description="Date of the creation")

    model_config = SettingsConfigDict(from_attributes=True)


class NationalityCatalogPartialResponseSchema(BaseModel):
    id: int

    name: str = Field(
        default_factory=str,
        description="Nationality name in default language",
    )
    lang: str = Field(..., description="Nationality default language")

    changed_at: datetime = Field(..., description="Date of the last update")
    created_at: datetime = Field(..., description="Date of the creation")

    model_config = SettingsConfigDict(from_attributes=True)


class MultipleNationalitiesCatalogSchema(BaseModel):
    items: List[
        Union[
            NationalityCatalogFullResponseSchema,
            NationalityCatalogPartialResponseSchema,
        ]
    ]
    pagination: PaginationMetaDataSchema
