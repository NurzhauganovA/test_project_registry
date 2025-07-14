from datetime import date, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from src.core.i18n import _


class CreateScheduleDaySchema(BaseModel):
    schedule_id: UUID
    day_of_week: int = Field(..., ge=1, le=7, description="1 - Monday, ..., 7 - Sunday")
    is_active: bool = False
    work_start_time: time
    work_end_time: time
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None
    date: date

    # Work & break time validation
    @model_validator(mode="after")
    def validate_work_time(self) -> "CreateScheduleDaySchema":
        # Work time validation
        if self.work_start_time >= self.work_end_time:
            raise ValueError(_("Work start time must be earlier than work end time."))
        # Break time validation
        if self.break_start_time and self.break_end_time:
            if self.break_start_time >= self.break_end_time:
                raise ValueError(
                    _("Break start time must be earlier than break end time.")
                )
            if (
                self.break_start_time < self.work_start_time
                or self.break_end_time > self.work_end_time
            ):
                raise ValueError(_("Break time must be within work time."))

        return self


class UpdateScheduleDaySchema(BaseModel):
    is_active: Optional[bool] = None
    work_start_time: Optional[time] = None
    work_end_time: Optional[time] = None
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None

    # Work & break time validation
    @model_validator(mode="after")
    def validate_work_time(self) -> "UpdateScheduleDaySchema":
        # Work time validation
        if self.work_start_time and self.work_end_time:
            if self.work_start_time >= self.work_end_time:
                raise ValueError(
                    _("Work start time must be earlier than work end time.")
                )
        # Break time validation
        if (
            self.break_start_time
            and self.break_end_time
            and self.work_start_time
            and self.work_end_time
        ):
            if self.break_start_time >= self.break_end_time:
                raise ValueError(
                    _("Break start time must be earlier than break end time.")
                )
            if (
                self.break_start_time < self.work_start_time
                or self.break_end_time > self.work_end_time
            ):
                raise ValueError(_("Break time must be within work time."))

        return self


class ScheduleDayTemplateSchema(BaseModel):
    day_of_week: int = Field(..., ge=1, le=7, description="1 - Monday, ..., 7 - Sunday")
    is_active: bool = False
    work_start_time: time
    work_end_time: time
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None

    # Work & break time validation
    @model_validator(mode="after")
    def validate_work_time(self) -> "ScheduleDayTemplateSchema":
        # Work time validation
        if self.work_start_time >= self.work_end_time:
            raise ValueError(_("Work start time must be earlier than work end time."))
        # Break time validation
        if self.break_start_time and self.break_end_time:
            if self.break_start_time >= self.break_end_time:
                raise ValueError(
                    "Break start time must be earlier than break end time."
                )
            if (
                self.break_start_time < self.work_start_time
                or self.break_end_time > self.work_end_time
            ):
                raise ValueError(_("Break time must be within work time."))

        return self
