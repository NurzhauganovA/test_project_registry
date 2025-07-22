from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.catalogs.enums import IdentityDocumentTypeEnum
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class IdentityDocumentResponseSchema(BaseModel):
    id: int = Field(..., description="Identity document record ID")
    patient_id: UUID = Field(..., description="Related Patient ID")
    type: IdentityDocumentTypeEnum = Field(..., description="Identity Document Type")
    series: Optional[str] = Field(None, description="Document Series")
    number: Optional[str] = Field(None, description="Document Number")
    issued_by: Optional[str] = Field(None, description="Issued By")
    issue_date: Optional[date] = Field(None, description="Document Issue Date")
    expiration_date: Optional[date] = Field(
        None, description="Document Expiration Date"
    )


class MultipleIdentityDocumentsCatalogResponseSchema(BaseModel):
    items: List[IdentityDocumentResponseSchema]
    pagination: PaginationMetaDataSchema
