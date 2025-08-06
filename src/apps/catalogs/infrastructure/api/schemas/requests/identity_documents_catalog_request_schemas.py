from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from src.apps.catalogs.enums import IdentityDocumentTypeEnum
from src.core.i18n import _


class IdentityDocumentRequestBaseSchema(BaseModel):
    id: Optional[int] = Field(None, description="Unique identity document record ID")
    patient_id: Optional[UUID] = Field(None, description="Related Patient ID")
    type: Optional[IdentityDocumentTypeEnum] = Field(
        None, description="Identity Document Type"
    )
    series: Optional[str] = Field(None, max_length=20, description="Document Series")
    number: Optional[str] = Field(None, max_length=20, description="Document Number")
    issued_by: Optional[str] = Field(None, max_length=256, description="Issued By")
    issue_date: Optional[date] = Field(None, description="Document Issue Date")
    expiration_date: Optional[date] = Field(
        None, description="Document Expiration Date"
    )

    @model_validator(mode="after")
    def check_dates(self):
        if self.issue_date and self.expiration_date:
            if self.expiration_date <= self.issue_date:
                raise ValueError(
                    _("Document expiration date must be later than issue date.")
                )
        return self


class AddIdentityDocumentRequestSchema(IdentityDocumentRequestBaseSchema):
    patient_id: UUID = Field(..., description="Related Patient ID")
    type: IdentityDocumentTypeEnum = Field(..., description="Identity Document Type")


class UpdateIdentityDocumentRequestSchema(IdentityDocumentRequestBaseSchema):
    pass


class DeleteIdentityDocumentSchema(BaseModel):
    id: int
