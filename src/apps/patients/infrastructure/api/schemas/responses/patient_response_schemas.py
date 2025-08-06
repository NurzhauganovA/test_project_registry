from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.patients.domain.enums import (
    PatientGenderEnum,
    PatientMaritalStatusEnum,
    PatientProfileStatusEnum,
    PatientSocialStatusEnum,
)
from src.apps.patients.infrastructure.api.schemas.jsonb_fields_schemas import (
    PatientAddressItemSchema,
    PatientAttachmentDataItemSchema,
    PatientContactInfoItemSchema,
    PatientRelativeItemSchema,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class ResponsePatientSchema(BaseModel):
    id: UUID
    iin: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    maiden_name: Optional[str] = None
    date_of_birth: date
    gender: PatientGenderEnum
    citizenship_id: int
    nationality_id: int
    financing_sources_ids: List[int]
    context_attributes_ids: Optional[List[int]]
    social_status: PatientSocialStatusEnum
    marital_status: PatientMaritalStatusEnum
    attachment_data: Optional[PatientAttachmentDataItemSchema] = None
    relatives: Optional[List[PatientRelativeItemSchema]] = None
    addresses: Optional[List[PatientAddressItemSchema]] = None
    contact_info: Optional[List[PatientContactInfoItemSchema]] = None
    profile_status: PatientProfileStatusEnum


class PatientTruncatedResponseSchema(BaseModel):
    """A truncated version of the patient's response schema for the client"""

    id: UUID

    iin: str = Field(..., description="Patient's IIN")
    first_name: str = Field(..., description="Patient's first name")
    last_name: str = Field(..., description="Patient's last name")
    middle_name: Optional[str] = Field(None, description="Patient's middle name")


class PatientTruncatedAppointmentBlankInfoSchema(PatientTruncatedResponseSchema):
    maiden_name: Optional[str] = Field(None, description="Patient's maiden name")
    date_of_birth: date = Field(..., description="Patient's birth date")
    gender: PatientGenderEnum = Field(..., description="Patient's gender")
    address: Optional[str] = Field(None, description="Patient's primary address")
    ambulatory_card_number: Optional[int] = Field(None, description="Patient's ambulatory card number")


class MultiplePatientsResponseSchema(BaseModel):
    items: List[ResponsePatientSchema]
    pagination: PaginationMetaDataSchema
