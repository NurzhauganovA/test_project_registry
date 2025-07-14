from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from src.apps.patients.infrastructure.api.schemas.responses.patient_response_schemas import (
    PatientTruncatedResponseSchema,
)
from src.apps.users.infrastructure.schemas.user_schemas import (
    DoctorTruncatedResponseSchema,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


# ------- Base schemas -------
class DiagnosesCatalogBaseResponseSchema(BaseModel):
    id: int
    diagnosis_code: str = Field(
        ...,
        description="Diagnosis code",
        max_length=20,
    )
    description: Optional[str] = Field(
        None,
        description="Diagnosis description",
        max_length=256,
    )
    is_active: bool = Field(..., description="Diagnosis status")


class DiagnosedPatientDiagnosisBaseResponseSchema(BaseModel):
    id: UUID
    date_diagnosed: Optional[date] = Field(
        None, description="Date when the diagnosis was made"
    )
    comment: Optional[str] = Field(
        None,
        description="Optional comment for the diagnosis",
        max_length=256,
    )


# ------- Typical schemas -------
class DiagnosesCatalogResponseSchema(DiagnosesCatalogBaseResponseSchema):
    model_config = SettingsConfigDict(from_attributes=True)


class MultipleDiagnosesCatalogResponseSchema(BaseModel):
    items: List[DiagnosesCatalogResponseSchema]
    pagination: PaginationMetaDataSchema


class DiagnosedPatientDiagnosisResponseSchema(
    DiagnosedPatientDiagnosisBaseResponseSchema
):
    diagnosis: DiagnosesCatalogResponseSchema = Field(
        ...,
        description="Diagnosis",
    )
    patient: PatientTruncatedResponseSchema = Field(
        ...,
        description="Patient who has been diagnosed",
    )
    doctor: Optional[DoctorTruncatedResponseSchema] = Field(
        None, description="Doctor who has diagnosed"
    )


class MultipleDiagnosedPatientDiagnosisResponseSchema(BaseModel):
    items: List[DiagnosedPatientDiagnosisResponseSchema]
    pagination: PaginationMetaDataSchema
