from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.apps.users.infrastructure.validation_helpers import validate_user_client_roles
from src.shared.helpers.validation_helpers import (
    validate_date_of_birth,
    validate_field_not_blank,
    validate_iin,
)


class SpecializationModel(BaseModel):
    name: str
    id: Optional[str] = None

    @field_validator("name")
    def name_is_not_blank(cls, v: str, info):
        label = info.field_name.replace("_", " ").capitalize()
        validate_field_not_blank(v, label)
        return v.strip()


class AttachmentDataModel(BaseModel):
    area_number: Optional[int] = None
    organization_name: Optional[str] = None
    attachment_date: Optional[str] = None
    detachment_date: Optional[str] = None
    department_name: Optional[str] = None


class UserSchema(BaseModel):
    """
    Pydantic model for receiving/delivering user data in the registry service.
    """

    id: Optional[UUID]
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    iin: str
    date_of_birth: date
    enabled: bool

    # JSONB fields
    client_roles: List[str]
    specializations: List[SpecializationModel]
    attachment_data: Optional[AttachmentDataModel] = None
    served_patient_types: List[str]
    served_referral_types: List[str]
    served_referral_origins: List[str]
    served_payment_types: List[str]

    @field_validator("first_name", "last_name")
    def validate_field_not_blank(cls, v: str, info) -> str:
        label = info.field_name.replace("_", " ").capitalize()
        validate_field_not_blank(v, label)

        return v.strip()

    @field_validator("iin", mode="before")
    def iin_valid(cls, v):
        return validate_iin(v)

    @field_validator("date_of_birth")
    def validate_date_of_birth(cls, v: date) -> date:
        validate_date_of_birth(v)
        return v

    @field_validator("client_roles")
    def validate_client_roles(cls, v: List[str]) -> List[str]:
        validate_user_client_roles(v)
        return v

    @field_validator(
        "served_patient_types",
        "served_referral_types",
        "served_referral_origins",
        "served_payment_types",
    )
    def validate_served_lists(cls, v: List[str]) -> List[str]:
        cleaned = [item.strip() for item in v if isinstance(item, str) and item.strip()]
        return cleaned

    def get_specializations(self) -> List[dict[str, str]]:
        """
        Converts a list of SpecializationModels into a list of dictionaries
        with keys 'id' and 'name', ready for UserDomain.
        """
        specs: List[dict[str, str]] = []
        for spec in self.specializations or []:
            specs.append(
                {
                    "id": str(spec.id),
                    "name": spec.name,
                }
            )
        return specs


class DeleteUserSchema(BaseModel):
    id: UUID


class DoctorTruncatedResponseSchema(BaseModel):
    """A truncated version of the doctor's response schema for the client"""

    id: UUID

    iin: str = Field(..., description="Doctor's IIN")
    first_name: str = Field(..., description="Doctor's first name")
    last_name: str = Field(..., description="Doctor's last name")
    middle_name: Optional[str] = Field(None, description="Doctor's middle name")
