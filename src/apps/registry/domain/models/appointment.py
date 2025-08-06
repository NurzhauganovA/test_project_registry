from datetime import UTC, datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.apps.registry.domain.enums import AppointmentStatusEnum, AppointmentTypeEnum
from src.apps.registry.domain.exceptions import InvalidAppointmentStatusDomainError
from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.exceptions import (
    ScheduleDayIsNotActiveError,
    ScheduleIsNotActiveError,
)
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    ResponseScheduleDaySchema,
)
from src.core.i18n import _


class AppointmentDomain:
    """Appointment domain class"""

    def __init__(
            self,
            *,
            id: Optional[int] = None,
            schedule_day_id: UUID,
            time: time,
            patient_id: Optional[UUID],
            phone_number: Optional[str] = None,
            address: Optional[str] = None,
            status: AppointmentStatusEnum = AppointmentStatusEnum.BOOKED,
            type: Optional[AppointmentTypeEnum] = None,
            financing_sources_ids: Optional[List[int]] = None,
            reason: Optional[str] = None,
            additional_services: Optional[List[Dict[str, Any]]] = None,
            office_number: Optional[int] = None,
            cancelled_at: Optional[datetime] = None,
    ):
        self.id = id
        self.schedule_day_id = schedule_day_id
        self.time = time
        self.patient_id = patient_id
        self.phone_number = phone_number
        self.address = address
        self.status = status
        self.type = type
        self.financing_sources_ids = (
            financing_sources_ids if financing_sources_ids else []
        )
        self.reason = reason
        self.additional_services = (
            additional_services if additional_services is not None else []
        )
        self.office_number = office_number
        self.cancelled_at = cancelled_at

    def book(
        self, schedule: ScheduleDomain, schedule_day: ResponseScheduleDaySchema
    ) -> None:
        """
        Method for booking an appointment. Checks that both schedule and day are active.
        Moreover, if the current status is CANCELLED, it resets the 'cancelled_at' field.
        """
        if not schedule.is_active:
            raise ScheduleIsNotActiveError(
                status_code=409,
                detail=_("Associated schedule is inactive."),
            )
        if not schedule_day.is_active:
            raise ScheduleDayIsNotActiveError(
                status_code=409,
                detail=_("Associated schedule day is inactive."),
            )

        # If the current status is CANCELLED, reset the 'cancelled_at' field
        if self.status == AppointmentStatusEnum.CANCELLED:
            self.cancelled_at = None

        self.status = AppointmentStatusEnum.BOOKED

    def cancel(self):
        """
        Method for canceling a reservation.
        Moreover, it sets the 'cancelled_at' field to the current datetime (UTC).
        """
        if self.status != AppointmentStatusEnum.CANCELLED:
            self.status = AppointmentStatusEnum.CANCELLED
            self.cancelled_at = datetime.now(UTC)

    def validate_appointment_status(self):
        """
        Validates the consistency between the appointment status and the presence of a patient ID.

        Note:
            If the `status` is 'APPOINTMENT', a `patient_id` must be provided (not None).
            If the `status` is 'BOOKED', there must NOT be a `patient_id` (it should be None).

        Raises:
            InvalidAppointmentStatusDomainError: If the appointment status does not match the
                `patient_id` presence rules.
        """
        if self.status == AppointmentStatusEnum.APPOINTMENT and self.patient_id is None:
            raise InvalidAppointmentStatusDomainError(
                detail="Invalid appointment status. "
                "You can't select an 'appointment' status without 'patient_id' provided."
            )
        if self.status == AppointmentStatusEnum.BOOKED and self.patient_id is not None:
            raise InvalidAppointmentStatusDomainError(
                detail="Invalid appointment status. "
                "You can't select an 'booked' status with 'patient_id' provided."
            )
