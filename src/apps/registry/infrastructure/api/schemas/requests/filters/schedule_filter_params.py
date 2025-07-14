from typing import List, Optional
from uuid import UUID

from fastapi import Query


class ScheduleFilterParams:
    def __init__(
        self,
        name_filter: Optional[str] = Query(
            None, description="Name to filter schedules by"
        ),
        doctor_full_name_filter: Optional[
            str
        ] = Query(  # "{last_name} {first_name} {middle_name}"
            None, description="Doctor's full name to filter schedules by"
        ),
        doctor_iin_filter: Optional[str] = Query(
            None,
            description="Doctor's IIN to filter schedules by",
        ),
        doctor_id_filter: Optional[UUID] = Query(
            None, description="Doctor's ID to filter schedules by"
        ),
        status_filter: Optional[bool] = Query(
            None, description="Filter schedules by status"
        ),
        serviced_area_number_filter: Optional[
            int
        ] = Query(  # In Russian: "Фильтр по участку"
            None, description="Serviced area number to filter schedules by"
        ),
        doctor_specializations_filter: Optional[List[str]] = Query(
            None, description="List of specializations to filter schedules by"
        ),
    ):
        self.name_filter = name_filter
        self.doctor_full_name_filter = doctor_full_name_filter
        self.doctor_iin_filter = doctor_iin_filter
        self.doctor_id_filter = doctor_id_filter
        self.status_filter = status_filter
        self.serviced_area_number_filter = serviced_area_number_filter
        self.doctor_specializations_filter = doctor_specializations_filter

    def to_dict(self, exclude_none: bool = True) -> dict:
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }
