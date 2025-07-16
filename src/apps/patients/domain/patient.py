from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.apps.patients.domain.enums import (
    PatientGenderEnum,
    PatientMaritalStatusEnum,
    PatientProfileStatusEnum,
    PatientSocialStatusEnum,
)
from src.core.settings import project_settings


class PatientDomain:
    def __init__(
        self,
        *,
        id: Optional[UUID],
        iin: str,
        first_name: str,
        last_name: str,
        middle_name: Optional[str],
        maiden_name: Optional[str],
        date_of_birth: date,
        gender: Optional[PatientGenderEnum] = None,
        citizenship_id: int,
        nationality_id: int,
        financing_sources_ids: Optional[List[int]] = None,
        context_attributes_ids: Optional[List[int]] = None,
        social_status: Optional[PatientSocialStatusEnum] = None,
        marital_status: Optional[PatientMaritalStatusEnum] = None,
        attachment_data: Optional[Dict[str, Any]] = None,
        relatives: Optional[List[Dict[str, Any]]],
        addresses: Optional[List[Dict[str, Any]]],
        contact_info: Optional[List[Dict[str, Any]]],
        profile_status: Optional[PatientProfileStatusEnum] = None,
    ) -> None:
        self.id = id
        self.iin = iin
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.maiden_name = maiden_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.citizenship_id = citizenship_id
        self.nationality_id = nationality_id
        self.financing_sources_ids = financing_sources_ids or []
        self.context_attributes_ids = context_attributes_ids or []
        self.social_status = social_status
        self.marital_status = marital_status
        self.attachment_data = attachment_data
        self.relatives = relatives or []
        self.addresses = addresses or []
        self.contact_info = contact_info or []
        self.profile_status = profile_status

    def is_adult(self) -> bool:
        today = datetime.today().date()
        age = (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

        return age >= project_settings.ADULT_AGE_LIMIT
