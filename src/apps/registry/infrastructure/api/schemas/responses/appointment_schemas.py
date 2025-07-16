from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.patients.infrastructure.api.schemas.responses.patient_response_schemas import (
    ResponsePatientSchema,
)
from src.apps.registry.domain.enums import AppointmentStatusEnum, AppointmentTypeEnum
from src.apps.registry.infrastructure.api.schemas.appointment_schemas import (
    AdditionalServiceSchema,
)
from src.apps.users.infrastructure.schemas.user_schemas import UserSchema
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class ResponseAppointmentSchema(BaseModel):
    id: int
    schedule_day_id: UUID
    start_time: time
    end_time: time  # Not in the 'appointments' DB table
    date: date  # Not in the 'appointments' DB table
    doctor: (
        UserSchema  # Not in the 'appointments' DB table, only 'doctor_id' is in the DB
    )
    patient: Optional[ResponsePatientSchema] = (
        None  # Not in the 'appointments' DB table, only 'patient_id' is in the DB
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

    # Optional field. Is being set by the server when the appointment is cancelled.
    cancelled_at: Optional[datetime] = None


class MultipleAppointmentsResponseSchema(BaseModel):
    items: List[ResponseAppointmentSchema]
    pagination: PaginationMetaDataSchema
