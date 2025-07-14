from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.apps.registry.infrastructure.api.schemas.requests.schedule_day_schemas import (
    ScheduleDayTemplateSchema,
)
from src.core.i18n import _


class CreateScheduleSchema(BaseModel):
    schedule_name: str = Field(..., max_length=20)
    period_start: date
    period_end: date
    is_active: bool = True
    appointment_interval: int = Field(
        ..., ge=5, le=60, description="Appointment interval in minutes."
    )
    description: Optional[str] = Field(
        None,
        max_length=256,
        description="The description of the schedule.",
    )
    week_days_template: list[ScheduleDayTemplateSchema] = Field(..., max_length=7)

    @field_validator("appointment_interval", mode="before")
    def validate_appointment_interval(cls, v: int) -> int:
        if not 5 <= v <= 60:
            raise ValueError(
                _(
                    "Appointment interval must be equal to or greater than "
                    "5 and less than or equal to 60 minutes."
                )
            )

        return v

    @field_validator("schedule_name", mode="before")
    def validate_schedule_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Schedule name cannot be empty.")

        return v

    @model_validator(mode="after")
    def validate_period_dates(self) -> "CreateScheduleSchema":
        if self.period_start < date.today():
            raise ValueError(_("Schedule start date cannot be in the past."))
        if self.period_start > self.period_end:
            raise ValueError(
                _("Period start date must be earlier than period end date.")
            )

        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "schedule_name": "Primary Schedule",
                "period_start": "2025-04-15",
                "period_end": "2025-05-15",
                "appointment_interval": 15,
                "is_active": True,
                "week_days_template": [
                    {
                        "day_of_week": 1,
                        "is_active": True,
                        "work_start_time": "09:00",
                        "work_end_time": "18:00",
                    },
                    {
                        "day_of_week": 2,
                        "is_active": True,
                        "work_start_time": "09:00",
                        "work_end_time": "18:00",
                        "break_start_time": "13:00",
                        "break_end_time": "14:00",
                    },
                    {
                        "day_of_week": 3,
                        "is_active": True,
                        "work_start_time": "10:00",
                        "work_end_time": "17:00",
                    },
                    {
                        "day_of_week": 4,
                        "is_active": True,
                        "work_start_time": "09:00",
                        "work_end_time": "18:00",
                        "break_start_time": "13:00",
                        "break_end_time": "14:00",
                    },
                    {
                        "day_of_week": 5,
                        "is_active": True,
                        "work_start_time": "08:30",
                        "work_end_time": "14:00",
                    },
                    {
                        "day_of_week": 6,
                        "is_active": True,
                        "work_start_time": "09:00",
                        "work_end_time": "18:00",
                        "break_start_time": "13:00",
                        "break_end_time": "14:00",
                    },
                    {
                        "day_of_week": 7,
                        "is_active": True,
                        "work_start_time": "09:00",
                        "work_end_time": "18:00",
                        "break_start_time": "13:00",
                        "break_end_time": "14:00",
                    },
                ],
            }
        }
    )


class UpdateScheduleSchema(BaseModel):
    schedule_name: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    is_active: Optional[bool] = True
    appointment_interval: Optional[int] = Field(
        None, ge=5, le=60, description="Appointment interval in minutes."
    )
    description: Optional[str] = Field(
        None,
        max_length=256,
        description="The description of the schedule.",
    )

    @field_validator("appointment_interval", mode="before")
    def validate_appointment_interval(cls, v: int) -> int:
        if not 5 <= v <= 60:
            raise ValueError(
                _(
                    "Appointment interval must be equal to or greater than "
                    "5 and less than or equal to 60 minutes."
                )
            )

        return v

    @field_validator("schedule_name", mode="before")
    def validate_schedule_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError(_("Schedule name cannot be empty."))
        if len(v) > 20:
            raise ValueError(_("Schedule name cannot exceed 20 characters."))
        return v

    @model_validator(mode="after")
    def validate_period_dates(self) -> "UpdateScheduleSchema":
        if self.period_start is None or self.period_end is None:
            return self

        if self.period_start < date.today():
            raise ValueError(_("Schedule start date cannot be in the past."))
        if self.period_start > self.period_end:
            raise ValueError(
                _("Period start date must be earlier than period end date.")
            )

        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "doctor_id": "b40d096d-d8c7-4f0d-afdb-0fd3590a5187",
                "schedule_name": "Updated Schedule",
                "period_start": "2025-04-15",
                "period_end": "2025-05-15",
                "is_active": True,
                "appointment_interval": 15,
            }
        }
    )
