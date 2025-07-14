from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class FinancingSourceFullResponseSchema(BaseModel):
    id: int

    name: str = Field(
        default_factory=str,
        description="Financing source name in default language",
    )
    financing_source_code: str = Field(
        ...,
        max_length=20,
        description="Financing source code",
        alias="code",
    )
    lang: str = Field(..., description="Financing source default language")
    name_locales: Optional[dict] = Field(
        None,
        description="Financing source additional languages for the 'name' field",
    )

    changed_at: datetime = Field(..., description="Date of the last update")
    created_at: datetime = Field(..., description="Date of the creation")

    model_config = SettingsConfigDict(from_attributes=True)


class FinancingSourcePartialResponseSchema(BaseModel):
    id: int

    name: str = Field(
        default_factory=str,
        description="Financing source name in default language",
    )
    financing_source_code: str = Field(
        ...,
        max_length=20,
        description="Financing source code",
        alias="code",
    )
    lang: str = Field(..., description="Financing source default language")

    changed_at: datetime = Field(..., description="Date of the last update")
    created_at: datetime = Field(..., description="Date of the creation")

    model_config = SettingsConfigDict(from_attributes=True)


class MultipleFinancingSourcesSchema(BaseModel):
    items: List[
        Union[
            FinancingSourceFullResponseSchema,
            FinancingSourcePartialResponseSchema,
        ]
    ]
    pagination: PaginationMetaDataSchema
