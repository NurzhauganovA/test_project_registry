from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.apps.patients.domain.enums import (
    PatientGenderEnum,
    PatientMaritalStatusEnum,
    PatientProfileStatusEnum,
    PatientSocialStatusEnum,
)
from src.apps.patients.infrastructure.api.schemas.jsonb_fields_schemas import (
    PatientAddressItemSchema,
    PatientAttachmentDataItemSchema,
    PatientContactInfoItemSchema,
    PatientRelativeItemSchema,
)
from src.apps.patients.infrastructure.api.schemas.validation_helpers import (
    ensure_has_primary,
)
from src.shared.helpers.validation_helpers import (
    normalize_empty,
    validate_date_of_birth,
    validate_field_not_blank,
    validate_iin,
)


class CreatePatientSchema(BaseModel):
    iin: str
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    maiden_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: date
    gender: Optional[PatientGenderEnum] = None
    citizenship_id: int
    nationality_id: int
    financing_sources_ids: List[int]
    context_attributes_ids: Optional[List[int]] = None
    social_status: Optional[PatientSocialStatusEnum] = None
    marital_status: Optional[PatientMaritalStatusEnum] = None
    attachment_data: Optional[PatientAttachmentDataItemSchema] = None
    relatives: Optional[List[PatientRelativeItemSchema]] = None
    addresses: Optional[List[PatientAddressItemSchema]] = None
    contact_info: Optional[List[PatientContactInfoItemSchema]] = None
    profile_status: Optional[PatientProfileStatusEnum] = None

    @field_validator(
        "first_name", "last_name", "middle_name", "maiden_name", mode="before"
    )
    def validate_fields_not_blank(cls, v, info):
        return validate_field_not_blank(v, info.field_name) if v is not None else v

    @field_validator("iin", mode="before")
    def validate_iin(cls, v):
        return validate_iin(v)

    @field_validator("date_of_birth", mode="after")
    def validate_birth_date(cls, v):
        return validate_date_of_birth(v) if v is not None else v

    @field_validator("relatives", mode="before")
    def check_relatives(cls, v):
        return normalize_empty(v)

    @field_validator("addresses", mode="before")
    def check_addresses_empty(cls, v):
        return normalize_empty(v)

    @field_validator("addresses", mode="after")
    def check_addresses_primary(cls, v):
        return ensure_has_primary(v, field="is_primary") if v is not None else v

    @field_validator("contact_info", mode="before")
    def check_contacts_empty(cls, v):
        return normalize_empty(v)

    @field_validator("contact_info", mode="after")
    def check_contacts_primary(cls, v):
        return ensure_has_primary(v, field="is_primary") if v is not None else v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "iin": "040806501543",
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Иванович",
                "maiden_name": "Петрова",
                "date_of_birth": "1985-07-14",
                "gender": "male",
                "citizenship_id": 1,
                "nationality_id": 1,
                "financing_sources_ids": [1],
                "context_attributes_ids": [1],
                "social_status": "employed",
                "marital_status": "married",
                "attachment_data": {
                    "area_number": 12,
                    "attached_clinic_id": 1,
                },
                "relatives": [
                    {
                        "type": "mother",
                        "full_name": "Иванова Мария Петровна",
                        "iin": "620514300101",
                        "birth_date": "1960-05-14",
                        "phone": "77011234567",
                        "relation_comment": "Главный опекун",
                    }
                ],
                "addresses": [
                    {
                        "type": "registration",
                        "value": "г. Алматы, ул. Абая, д. 10",
                        "is_primary": True,
                    }
                ],
                "contact_info": [
                    {"type": "phone_number", "value": "77019876543", "is_primary": True}
                ],
                "profile_status": "active",
            }
        }
    )


class UpdatePatientSchema(BaseModel):
    iin: Optional[str] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    maiden_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[PatientGenderEnum] = None
    citizenship_id: Optional[int] = None
    nationality_id: Optional[int] = None
    financing_sources_ids: Optional[List[int]] = None
    context_attributes_ids: Optional[List[int]] = None
    social_status: Optional[PatientSocialStatusEnum] = None
    marital_status: Optional[PatientMaritalStatusEnum] = None
    attachment_data: Optional[PatientAttachmentDataItemSchema] = None
    relatives: Optional[List[PatientRelativeItemSchema]] = None
    addresses: Optional[List[PatientAddressItemSchema]] = None
    contact_info: Optional[List[PatientContactInfoItemSchema]] = None
    profile_status: Optional[PatientProfileStatusEnum] = None

    @field_validator(
        "first_name", "last_name", "middle_name", "maiden_name", mode="after"
    )
    def validate_fields_not_blank(cls, v, info):
        return validate_field_not_blank(v, info.field_name) if v is not None else v

    @field_validator("iin", mode="before")
    def validate_iin(cls, v):
        return validate_iin(v) if v is not None else v

    @field_validator("date_of_birth", mode="after")
    def validate_birth_date(cls, v):
        return validate_date_of_birth(v) if v is not None else v

    @field_validator("addresses", mode="after")
    def check_addresses_primary(cls, v):
        return ensure_has_primary(v, field="is_primary") if v is not None else v

    @field_validator("contact_info", mode="after")
    def check_contacts_primary(cls, v):
        return ensure_has_primary(v, field="is_primary") if v is not None else v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "iin": "040806501543",
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Иванович",
                "attachment_data": {
                    "area_number": 13,
                    "attached_clinic_id": 1,
                },
                "social_status": "retired",
                "profile_status": "inactive",
            }
        }
    )
