from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import Query

from src.apps.registry.domain.enums import AppointmentStatusEnum


class AppointmentFilterParams:
    def __init__(
        self,
        schedule_id: Optional[UUID] = Query(
            None, description="Schedule ID to filter appointments by"
        ),
        period_start: Optional[date] = Query(
            None, description="Date (FROM) to filter appointments by"
        ),
        period_end: Optional[date] = Query(
            None, description="Date (TO) to filter appointments by"
        ),
        patient_full_name_filter: Optional[str] = Query(
            # "{last_name} {first_name} {middle_name}"
            None,
            description="Patient's full name to filter appointments by",
        ),
        patient_iin_filter: Optional[str] = Query(
            None, description="Patient's IIN to filter appointments by"
        ),
        doctor_id_filter: Optional[UUID] = Query(
            None, description="Doctor's ID to filter appointments by"
        ),
        appointment_status_filter: Optional[AppointmentStatusEnum] = Query(
            None,
            description="Filter appointments by status: (e.g. 'BOOKED', 'CANCELLED' etc.)",
        ),
        attached_area_number_filter: Optional[int] = Query(
            # In Russian: "Фильтр по участку прикрепления"
            None,
            description="Serviced area number to filter appointments by",
        ),
        doctor_specialization_filter: Optional[str] = Query(
            None, description="Doctor's specialization to filter appointments by"
        ),
    ):
        self.schedule_id = schedule_id
        self.period_start = period_start
        self.period_end = period_end
        self.patient_full_name_filter = patient_full_name_filter
        self.patient_iin_filter = patient_iin_filter
        self.doctor_id_filter = doctor_id_filter
        self.appointment_status_filter = appointment_status_filter
        self.attached_area_number_filter = attached_area_number_filter
        self.doctor_specialization_filter = doctor_specialization_filter

    def to_dict(self, exclude_none: bool = True) -> dict:
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }
