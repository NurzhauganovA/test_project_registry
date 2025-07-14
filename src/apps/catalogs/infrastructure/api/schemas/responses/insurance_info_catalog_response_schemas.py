from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class ResponseInsuranceInfoRecordSchema(BaseModel):
    id: int = Field(..., description="ID from the DB")
    policy_number: Optional[str] = Field(
        None,
        description="Policy number",
        max_length=50,
    )
    company: Optional[str] = Field(
        None,
        description="Insurance company",
        max_length=100,
    )
    valid_from: Optional[date] = Field(
        None,
        description="Insurance is valid from",
    )
    valid_till: Optional[date] = Field(
        None,
        description="Insurance is valid till",
    )
    comment: Optional[str] = Field(
        None,
        description="Insurance comment",
    )

    # FKs
    patient_id: UUID = Field(
        ...,
        description="Patient ID",
    )
    financing_source_id: int = Field(
        ...,
        description="Financing source ID",
    )


class MultipleInsuranceInfoRecordsSchema(BaseModel):
    items: List[ResponseInsuranceInfoRecordSchema]
    pagination: PaginationMetaDataSchema
