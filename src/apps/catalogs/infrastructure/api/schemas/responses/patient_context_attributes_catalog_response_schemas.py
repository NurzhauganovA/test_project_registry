from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class PatientContextAttributeCatalogFullResponseSchema(BaseModel):
    id: int

    name: str = Field(
        default_factory=str,
        description="Patient context attribute name in default language",
    )
    lang: str = Field(..., description="Patient context attribute default language")
    name_locales: Optional[dict] = Field(
        None,
        description="Patient context attribute additional languages for the 'name' field",
    )

    changed_at: datetime = Field(..., description="Date of the last update")
    created_at: datetime = Field(..., description="Date of the creation")

    model_config = SettingsConfigDict(from_attributes=True)


class PatientContextAttributeCatalogPartialResponseSchema(BaseModel):
    id: int

    name: str = Field(
        default_factory=str,
        description="Patient context attribute name in default language",
    )
    lang: str = Field(..., description="Patient context attribute default language")

    changed_at: datetime = Field(..., description="Date of the last update")
    created_at: datetime = Field(..., description="Date of the creation")

    model_config = SettingsConfigDict(from_attributes=True)


class MultiplePatientContextAttributesSchema(BaseModel):
    items: List[
        Union[
            PatientContextAttributeCatalogFullResponseSchema,
            PatientContextAttributeCatalogPartialResponseSchema,
        ]
    ]
    pagination: PaginationMetaDataSchema
