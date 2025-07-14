from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID

from src.apps.registry.domain.exceptions import ScheduleValidationError
from src.apps.registry.infrastructure.api.schemas.requests.schedule_day_schemas import (
    CreateScheduleDaySchema,
    ScheduleDayTemplateSchema,
)
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

    def regenerate_days(
        self, week_days_template: List[ScheduleDayTemplateSchema]
    ) -> None:
        """
        Regenerate the list of days of the schedule based on the period and weekday pattern.
        The method uses generation logic similar to the service method and updates self.days.

        :param week_days_template: list of days containing a pattern for each day of the week,
        where the key is 'day_of_week' (int from 1 to 7)

            Example:
                 [
                   {"day_of_week": 1, "is_active": True, "appointment_interval": 30,
                   "work_start_time": "09:00", "work_end_time": "17:00",
                   "break_start_time": "12:00", "break_end_time": "13:00"},
                   {"day_of_week": 2, ...},
                   ...
                 ]

        :return: List of days.
        """
        # Transform the template: key is the day of the week number
        template_by_day = {
            template["day_of_week"]: template.model_dump()
            for template in week_days_template
        }
        new_days: List[CreateScheduleDaySchema] = []
        current_date = self.period_start
        while current_date <= self.period_end:
            # weekday() returns 0 for Monday, so add 1
            day_of_week = current_date.weekday() + 1
            if day_of_week in template_by_day:
                template_data = template_by_day[day_of_week]
                day_schema = CreateScheduleDaySchema(
                    schedule_id=self.id,
                    date=current_date,
                    day_of_week=day_of_week,
                    is_active=template_data.get("is_active", False),
                    work_start_time=template_data["work_start_time"],
                    work_end_time=template_data["work_end_time"],
                    break_start_time=template_data.get("break_start_time"),
                    break_end_time=template_data.get("break_end_time"),
                )
                new_days.append(day_schema)
            current_date += timedelta(days=1)
        self.days = new_days
