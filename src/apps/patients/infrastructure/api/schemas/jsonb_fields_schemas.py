from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from src.apps.patients.domain.enums import (
    PatientAddressesEnum,
    PatientContactTypeEnum,
    PatientRelativesKinshipEnum,
)
from src.core.i18n import _
from src.shared.helpers.validation_helpers import (
    validate_date_of_birth,
    validate_field_not_blank,
    validate_iin,
    validate_phone_number,
)


class PatientRelativeItemSchema(BaseModel):
    type: PatientRelativesKinshipEnum
    full_name: str
    iin: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    relation_comment: Optional[str] = None

    @field_validator("full_name", mode="before")
    def validate_full_name(cls, v):
        return validate_field_not_blank(v, "full_name")

    @field_validator("iin", mode="before")
    def validate_iin_field(cls, v):
        return validate_iin(v) if v is not None else v

    @field_validator("birth_date", mode="after")
    def validate_birth_date(cls, v):
        return validate_date_of_birth(v) if v is not None else v

    @field_validator("phone", mode="before")
    def validate_phone(cls, v):
        return validate_phone_number(v) if v is not None else v


class PatientAddressItemSchema(BaseModel):
    type: PatientAddressesEnum
    value: str
    is_primary: bool

    @field_validator("value", mode="before")
    def validate_value_field(cls, v):
        return validate_field_not_blank(v, "value")


class PatientContactInfoItemSchema(BaseModel):
    type: PatientContactTypeEnum
    value: str
    is_primary: bool

    @field_validator("value", mode="before")
    def validate_value_field(cls, v):
        return validate_field_not_blank(v, "value")


class PatientAttachmentDataItemSchema(BaseModel):
    area_number: Optional[int] = Field(
        None, description="Area number (In Russian: Номер участка прикрепления)"
    )
    attached_clinic_id: Optional[int] = Field(
        None, description="Clinic ID patient attached to"
    )

    # Since attachment data was provided as NOT NONE -> at least one of the inner fields must be provided too
    @model_validator(mode="after")
    def check_at_least_one_field(cls, model):
        if model.area_number is None and model.attached_clinic_id is None:
            raise ValueError(
                _(
                    "At least one of 'area_number' or 'attached_clinic_id' must be provided"
                )
            )

        return model
