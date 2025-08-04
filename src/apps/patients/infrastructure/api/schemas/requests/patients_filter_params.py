from typing import Optional

from fastapi import Query

from src.apps.patients.domain.enums import (
    PatientMaritalStatusEnum,
    PatientProfileStatusEnum,
    PatientSocialStatusEnum,
)


class PatientsFilterParams:
    def __init__(
        self,
        iin_filter: Optional[str] = Query(
            None,
            description="Patient's IIN (partial match, 2+ symbols only)",
            pattern=r"^\d+$",  # Only digits
        ),
        patient_full_name_filter: Optional[str] = Query(
            None,
            description="Patient's full name (last_name + first_name) search (partial match, 2+ symbols only)",
            # Only letters, spaces, apostrophes and hyphens (In Russian: "дефисы")
            pattern=r"^[A-Za-zА-Яа-яЁё\s\-\']+$",
        ),
        attached_clinic_id_filter: Optional[int] = Query(
            None, description="Medical organization's ID the patient attached to"
        ),
        social_status_filter: Optional[PatientSocialStatusEnum] = Query(
            None, description="Patient's social status (exact match)"
        ),
        marital_status_filter: Optional[PatientMaritalStatusEnum] = Query(
            None, description="Patient's marital status (exact match)"
        ),
        profile_status_filter: Optional[PatientProfileStatusEnum] = Query(
            None, description="Patient's profile status (exact match)"
        ),
    ):
        self.iin = iin_filter
        self.patient_full_name = patient_full_name_filter
        self.attached_clinic_id = attached_clinic_id_filter
        self.social_status = social_status_filter
        self.marital_status = marital_status_filter
        self.profile_status = profile_status_filter

    def to_dict(self, exclude_none: bool = True) -> dict:
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }
