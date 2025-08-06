from datetime import date
from typing import List, Optional
from uuid import UUID

from src.apps.registry.domain.exceptions import ScheduleValidationError
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    ResponseScheduleDaySchema,
)
from src.core.i18n import _


class ScheduleDomain:
    """Schedule domain class"""

    MAX_PERIOD_MONTHS = 3

    def __init__(
        self,
        *,
        id: Optional[UUID] = None,
        doctor_id: UUID,
        schedule_name: str,
        period_start: date,
        period_end: date,
        is_active: bool = True,
        appointment_interval: int,
        description: Optional[str] = None,
        days: Optional[List[ResponseScheduleDaySchema]] = None,
    ):
        self.id = id
        self.doctor_id = doctor_id
        self.schedule_name = schedule_name
        self.period_start = period_start
        self.period_end = period_end
        self.is_active = is_active
        self.appointment_interval = appointment_interval
        self.description = description
        self.days = days  # List of pre-generated dictionaries

    def update_basic_info(
        self,
        *,
        schedule_name: Optional[str] = None,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        is_active: Optional[bool] = None,
        appointment_interval: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Updates basic schedule fields.

        :raise ScheduleValidationError: If the schedule name is longer than 20 characters.
        """
        if schedule_name is not None:
            if len(schedule_name) > 20:
                raise ScheduleValidationError(
                    _("Schedule name cannot exceed 20 characters.")
                )
            self.schedule_name = schedule_name
        if period_start is not None:
            self.period_start = period_start
        if period_end is not None:
            self.period_end = period_end
        if is_active is not None:
            self.is_active = is_active
        if appointment_interval is not None:
            if not (0 <= appointment_interval <= 60):
                raise ScheduleValidationError(
                    _(
                        "Appointment interval must be equal to or greater than "
                        "0 and less than or equal to 60 minutes."
                    )
                )
            self.appointment_interval = appointment_interval
        if description:
            if len(description) > 256:
                raise ScheduleValidationError(
                    _("Schedule description cannot exceed 256 characters.")
                )
