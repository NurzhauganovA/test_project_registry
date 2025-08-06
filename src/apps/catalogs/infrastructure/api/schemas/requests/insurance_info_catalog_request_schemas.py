from datetime import date
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from src.core.i18n import _
from src.shared.helpers.validation_helpers import validate_field_not_blank


class BaseInsuranceInfoRecordSchema(BaseModel):
    id: Optional[int] = Field(None, description="Unique insurance record ID")
    policy_number: Optional[str] = Field(
        None,
        description="Policy number",
        max_length=50,
    )
    company: Optional[str] = Field(
        None,
        description="Insurance company",
        max_length=100,
    )
    valid_from: Optional[date] = Field(
        None,
        description="Insurance is valid from",
    )
    valid_till: Optional[date] = Field(
        None,
        description="Insurance is valid till",
    )
    comment: Optional[str] = Field(
        None,
        description="Insurance comment",
    )

    patient_id: Optional[UUID] = Field(
        None,
        description="Patient ID",
    )
    financing_source_id: Optional[int] = Field(
        None,
        description="Financing source ID",
    )

    @field_validator("policy_number", "company", "comment", mode="before")
    def validate_field_not_blank(cls, value: Any, info):
        if value is None:
            return value

        validate_field_not_blank(value, info.field_name)

        return value

    @model_validator(mode="after")
    def check_dates(cls, model):
        valid_from = model.valid_from
        valid_till = model.valid_till

        if valid_from and valid_till and valid_till < valid_from:
            raise ValidationError(
                _("'valid_till' date must be equal or greater than 'valid_from' date.")
            )

        return model


class AddInsuranceInfoRecordSchema(BaseInsuranceInfoRecordSchema):
    patient_id: UUID = Field(
        ...,
        description="Patient ID",
    )
    financing_source_id: int = Field(
        ...,
        description="Financing source ID",
    )


class UpdateInsuranceInfoRecordSchema(BaseInsuranceInfoRecordSchema):
    pass


class DeleteInsuranceInfoRecordSchema(BaseModel):
    id: int
