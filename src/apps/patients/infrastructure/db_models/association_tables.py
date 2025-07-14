from sqlalchemy import ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql.schema import Column

from src.shared.infrastructure.base import Base

"""
This module represents the associations tables for linking patients
and their financing sources (OSMS - ОСМС, DMS - ДМС etc.),
additional attributes (Unemployed, untransportable etc.)
"""


# patient_financing_source association table
patient_financing_source = Table(
    "patient_financing_source",
    Base.metadata,
    Column(
        "patient_id",
        PG_UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "financing_source_id",
        ForeignKey("cat_financing_sources.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# patient_additional_attribute association table
patient_additional_attribute = Table(
    "patient_additional_attribute",
    Base.metadata,
    Column(
        "patient_id",
        PG_UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "additional_attribute_id",
        ForeignKey("cat_patient_context_attributes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
