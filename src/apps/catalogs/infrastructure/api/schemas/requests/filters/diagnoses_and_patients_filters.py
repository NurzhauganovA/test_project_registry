from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import Query


class DiagnosesAndPatientsFilterParams:
    def __init__(
        self,
        patient_id: Optional[UUID] = Query(
            None,
            description="Filter by patient ID (UUID)",
            examples=["8a98a234-2cf2-11ee-be56-0242ac120002"],
        ),
        doctor_id: Optional[UUID] = Query(
            None,
            description="Filter by doctor ID (UUID)",
            examples=["1b92721d-3cf2-11ee-be56-0242ac120002"],
        ),
        diagnosis_code: Optional[str] = Query(
            None,
            description="Filter by diagnosis code (exact match)",
            examples=["A00", "B12.3"],
        ),
        date_diagnosed_from: Optional[date] = Query(
            None,
            description="Filter by diagnosis date FROM (ISO date, e.g. 2024-07-07)",
        ),
        date_diagnosed_to: Optional[date] = Query(
            None,
            description="Filter by diagnosis date TO (ISO date, e.g. 2024-07-08)",
        ),
    ):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.diagnosis_code = diagnosis_code
        self.date_diagnosed_from = date_diagnosed_from
        self.date_diagnosed_to = date_diagnosed_to

    def to_dict(self, exclude_none: bool = True) -> dict:
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }
