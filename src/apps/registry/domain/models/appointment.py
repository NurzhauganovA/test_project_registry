from datetime import UTC, datetime, time
from typing import Dict, Optional
from uuid import UUID

from src.apps.registry.domain.enums import (
    AppointmentInsuranceType,
    AppointmentStatusEnum,
    AppointmentTypeEnum,
)
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
        status: AppointmentStatusEnum = AppointmentStatusEnum.BOOKED,
        type: AppointmentTypeEnum,
        insurance_type: AppointmentInsuranceType,
        reason: Optional[str] = None,
        additional_services: Optional[Dict[str, bool]] = None,
        cancelled_at: Optional[datetime] = None,
    ):
        self.id = id
        self.schedule_day_id = schedule_day_id
        self.time = time
        self.patient_id = patient_id
        self.status = status
        self.type = type
        self.insurance_type = insurance_type
        self.reason = reason
        self.additional_services = (
            additional_services if additional_services is not None else {}
        )
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
