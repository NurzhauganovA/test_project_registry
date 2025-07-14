from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.apps.users.infrastructure.validation_helpers import validate_user_client_roles
from src.shared.helpers.validation_helpers import (
    validate_date_of_birth,
    validate_field_not_blank,
    validate_iin,
)


class UserDomain:
    """
    Domain model describing a user from the
    Auth Service in the Registry Service

    Attributes:
        id (UUID): user ID from the Auth Service
        first_name (str): first name
        last_name (str): last name
        middle_name (Optional[str]): middle name
        iin (str): user IIN
        date_of_birth (date): date of birth
        client_roles (List[str]): list of roles
        enabled (bool): user activity flag
        specializations (List[Dict[str, str]]): doctor specializations
        attachment_data (Dict[str, Any]): doctor profile data
        served_patient_types (List[str]): patient types
        served_referral_types (List[str]): referral types
        served_referral_origins (List[str]): referral origins
        served_payment_types (List[str]): payment types
    """

    def __init__(
        self,
        *,
        id: Optional[UUID] = None,
        first_name: str,
        last_name: str,
        middle_name: Optional[str] = None,
        iin: str,
        date_of_birth: date,
        client_roles: List[str],
        enabled: bool,
        specializations: List[Dict[str, str | None]],
        attachment_data: Dict[str, Any],
        served_patient_types: List[str],
        served_referral_types: List[str],
        served_referral_origins: List[str],
        served_payment_types: List[str],
    ) -> None:
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.iin = iin
        self.date_of_birth = date_of_birth
        self.enabled = enabled

        # JSONB fields
        self.client_roles = client_roles
        self.specializations = specializations or []
        self.attachment_data = attachment_data or {}
        self.served_patient_types = served_patient_types or []
        self.served_referral_types = served_referral_types or []
        self.served_referral_origins = served_referral_origins or []
        self.served_payment_types = served_payment_types or []

    @property
    def is_enabled(self) -> bool | None:
        return self.enabled

    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def update_name(self, first_name: str, last_name: str, middle_name: str) -> None:
        validate_field_not_blank(first_name, "First name")
        validate_field_not_blank(last_name, "Last name")
        validate_field_not_blank(middle_name, "Middle name")

        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.middle_name = middle_name.strip()

    def update_date_of_birth(self, date_of_birth: date) -> None:
        validate_date_of_birth(date_of_birth)
        self.date_of_birth = date_of_birth

    def update_client_roles(self, new_roles: List[str]) -> None:
        """
        Completely refreshes the list of client roles.
        Checks for type and absence of duplicates.
        """
        validate_user_client_roles(new_roles)
        self.client_roles = new_roles.copy()

    def update_iin(self, new_iin: str) -> None:
        validate_iin(new_iin)
        self.iin = new_iin

    def deactivate(self) -> None:
        """Sets 'enabled' flag to False."""
        self.enabled = False

    def activate(self) -> None:
        """Sets 'enabled' flag to True."""
        self.enabled = True

    def to_dict(self) -> Dict[str, Any]:
        user_as_dict: Dict[str, Any] = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "iin": self.iin,
            "date_of_birth": self.date_of_birth,
            "client_roles": self.client_roles,
            "enabled": self.enabled,
            "specializations": self.specializations,
            "attachment_data": self.attachment_data,
            "served_patient_types": self.served_patient_types,
            "served_referral_types": self.served_referral_types,
            "served_referral_origins": self.served_referral_origins,
            "served_payment_types": self.served_payment_types,
        }

        return user_as_dict
