from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from src.shared.helpers.validation_helpers import validate_field_not_blank


# ------- Base schemas -------
class BaseNotBlankValidator(BaseModel):
    @field_validator("*", mode="before", check_fields=False)
    def _validate_not_blank_field(cls, v, info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        if isinstance(v, str):
            return validate_field_not_blank(v, field_label=info.field_name)
        return v


class DiagnosesCatalogBaseRequestSchema(BaseNotBlankValidator):
    id: Optional[int] = Field(None, description="Unique diagnosis ID")
    diagnosis_code: Optional[str] = Field(
        None,
        description="Diagnosis code",
        max_length=20,
    )
    description: Optional[str] = Field(
        None,
        description="Diagnosis description",
        max_length=256,
    )
    is_active: Optional[bool] = Field(True, description="Diagnosis status")


class DiagnosedPatientDiagnosisBaseRequestSchema(BaseNotBlankValidator):
    date_diagnosed: Optional[date] = Field(
        None, description="Date when the diagnosis was made"
    )
    comment: Optional[str] = Field(
        None,
        description="Optional comment for the diagnosis",
        max_length=256,
    )
    doctor_id: Optional[UUID] = Field(
        None,
        description="Doctor ID",
    )


# ------- Typical schemas -------
class AddDiagnosisRequestSchema(DiagnosesCatalogBaseRequestSchema):
    diagnosis_code: str = Field(
        ...,
        description="Diagnosis code",
        max_length=20,
    )


class UpdateDiagnosisRequestSchema(DiagnosesCatalogBaseRequestSchema):
    pass


class AddDiagnosedPatientDiagnosisRecordRequestSchema(
    DiagnosedPatientDiagnosisBaseRequestSchema
):
    diagnosis_id: int = Field(
        ...,
        description="Diagnosis ID",
    )
    patient_id: UUID = Field(
        ...,
        description="Patient ID",
    )


class UpdateDiagnosedPatientDiagnosisRecordRequestSchema(
    DiagnosedPatientDiagnosisBaseRequestSchema
):
    pass


class DeleteDiagnosisSchema(BaseModel):
    id: int
