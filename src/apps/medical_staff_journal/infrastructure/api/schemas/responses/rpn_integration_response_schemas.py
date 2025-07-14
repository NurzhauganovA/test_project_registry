from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class SpecialistAttachmentInfoSchema(BaseModel):
    specialization_name: str = Field(None, description="Specialist specialization name")
    territory_number: int = Field(
        None, description="The number of the area to which the specialist is assigned"
    )
    organization_name: str = Field(
        None, description="Name of the organization to which the specialist is assigned"
    )
    attachment_date: date = Field(
        ..., description="The date the specialist was assigned to this organization"
    )
    detachment_date: Optional[date] = Field(
        None,
        description="The date when the specialist was detached from this organization",
    )
    department_name: str = Field(
        ..., description="Name of the department to which the specialist is assigned"
    )


class ResponseSpecialistAttachmentInfoSchema(BaseModel):
    first_name: str = Field(..., description="Specialist first name")
    last_name: str = Field(..., description="Specialist last name")
    middle_name: str = Field(..., description="Specialist middle name")
    iin: str = Field(..., description="Specialist IIN")
    attachment_data: Optional[SpecialistAttachmentInfoSchema] = Field(
        None, description="Specialist attachment data"
    )
