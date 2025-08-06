from datetime import date as DTdate
from datetime import datetime, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.patients.infrastructure.api.schemas.responses.patient_response_schemas import (
    PatientTruncatedAppointmentBlankInfoSchema,
    PatientTruncatedResponseSchema,
)
from src.apps.registry.domain.enums import AppointmentStatusEnum, AppointmentTypeEnum
from src.apps.registry.infrastructure.api.schemas.appointment_schemas import (
    AdditionalServiceSchema,
)
from src.apps.users.infrastructure.schemas.user_schemas import DoctorTruncatedResponseSchema
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class ResponseAppointmentSchema(BaseModel):
    id: int
    schedule_day_id: UUID
    start_time: time
    end_time: time  # Not in the 'appointments' DB table
    date: DTdate  # Not in the 'appointments' DB table
    doctor: (
        DoctorTruncatedResponseSchema
    )
    patient: Optional[PatientTruncatedResponseSchema] = (
        None
    )
    phone_number: Optional[str] = None
    address: Optional[str] = None
    status: AppointmentStatusEnum
    type: Optional[AppointmentTypeEnum] = None
    financing_sources_ids: Optional[List[int]] = None
    reason: str
    additional_services: Optional[List[AdditionalServiceSchema]] = Field(
        default_factory=list
    )
    office_number: Optional[int] = Field(
        None,
        description="Office number where appointment will be processed in",
    )

    # Optional field. Is being set by the server when the appointment is cancelled.
    cancelled_at: Optional[datetime] = None


class MultipleAppointmentsResponseSchema(BaseModel):
    items: List[ResponseAppointmentSchema]
    pagination: PaginationMetaDataSchema


class AppointmentBlankInfoSchema(BaseModel):
    appointment_id: int = Field(..., description="Unique identifier of the appointment")
    date: DTdate = Field(..., description="Date of the appointment")
    start_time: time = Field(..., description="Start time of the appointment")
    doctor_full_name: str = Field(
        ...,
        description="Full name of the doctor (Last name, First name, Middle name if available)"
    )
    doctor_speciality: Optional[str] = Field(None, description="Primary medical specialty of the doctor")
    reason: str = Field(..., description="Reason or purpose for the appointment")
    office_number: Optional[int] = Field(
        None,
        description="Office number where appointment will be processed in",
    )
    patient: Optional[PatientTruncatedAppointmentBlankInfoSchema] = Field(
        None,
        description="Brief information about the patient related to this appointment"
    )
