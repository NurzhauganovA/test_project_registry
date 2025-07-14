from datetime import date
from typing import Any, Dict, List

from sqlalchemy import Date
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.catalogs.infrastructure.db_models.financing_sources_catalogue import (
    SQLAlchemyFinancingSourcesCatalog,
)
from src.apps.catalogs.infrastructure.db_models.patient_context_attributes_catalogue import (
    SQLAlchemyPatientContextAttributesCatalogue,
)
from src.apps.patients.domain.enums import (
    PatientGenderEnum,
    PatientMaritalStatusEnum,
    PatientProfileStatusEnum,
    PatientSocialStatusEnum,
)
from src.apps.patients.infrastructure.db_models.association_tables import (
    patient_additional_attribute,
    patient_financing_source,
)
from src.apps.registry.infrastructure.db_models.models import Appointment
from src.shared.infrastructure.base import (
    Base,
    ChangedAtMixin,
    CreatedAtMixin,
    PrimaryKey,
)


class SQLAlchemyPatient(Base, PrimaryKey, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "patients"

    iin: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=True)
    maiden_name: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="Patient's maiden name (девичья фамилия). The optional field.",
    )
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[PatientGenderEnum] = mapped_column(
        SAEnum(
            PatientGenderEnum,
            name="gender_enum",
            validate_strings=True,
            values_callable=lambda enums: [enum.value for enum in enums],
        ),
        nullable=True,
        server_default=PatientGenderEnum.NOT_SPECIFIED.value,
        comment="Patient's gender. The optional field. Default is 'NOT_SPECIFIED'.",
    )
    citizenship_id: Mapped[int] = mapped_column(
        ForeignKey("cat_citizenship.id"), nullable=False
    )
    nationality_id: Mapped[int] = mapped_column(
        ForeignKey("cat_nationalities.id"), nullable=False
    )
    social_status: Mapped[PatientSocialStatusEnum] = mapped_column(
        SAEnum(
            PatientSocialStatusEnum,
            name="social_status_enum",
            validate_strings=True,
            values_callable=lambda enums: [enum.value for enum in enums],
        ),
        nullable=True,
        server_default=PatientSocialStatusEnum.NOT_SPECIFIED.value,
        comment="Patient's social status. The optional field. Default is 'NOT_SPECIFIED'.",
    )
    marital_status: Mapped[PatientMaritalStatusEnum] = mapped_column(
        SAEnum(
            PatientMaritalStatusEnum,
            name="marital_status_enum",
            validate_strings=True,
            values_callable=lambda enums: [enum.value for enum in enums],
        ),
        nullable=True,
        server_default=PatientMaritalStatusEnum.NOT_SPECIFIED.value,
        comment="Patient's marital_status. The optional field. Default is 'NOT_SPECIFIED'.",
    )
    attachment_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Patient's attachment data. The optional field.",
    )
    relatives: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment=(
            "Patient's relatives as a list of objects. "
            "Each object should have: "
            "'type' (relation type, e.g., 'mother', 'father', 'spouse'), "
            "'full_name' (relative's full name), "
            "'iin' (optional, relative's IIN), "
            "'birth_date' (optional, ISO date string), "
            "'phone' (optional), "
            "'relation_comment' (optional, any additional info). "
            "Example: "
            "[{'type': 'mother', 'full_name': 'Ivanova Maria Petrovna', 'iin': '620514300101'}]. "
            "Field is optional, default is NULL."
        ),
    )
    addresses: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment=(
            "Patient's addresses as a list of objects. "
            "Each object should have: "
            "'type' (address type, e.g., 'residence', 'registration'), "
            "'value' (address string), "
            "'is_primary' (boolean flag for main address). "
            "Example: "
            "[{'type': 'residence', 'value': 'Akmola Region, Kokshetau, Mamyshuly St, 60', 'is_primary': true}]. "
            "Field is optional, default is NULL."
        ),
    )
    contact_info: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment=(
            "Patient's contact information as a list of objects (phones, emails, etc.). "
            "Each object should have: "
            "'type' (contact type, e.g., 'mobile', 'email', 'work'), "
            "'value' (contact detail), "
            "'is_primary' (boolean flag for main contact). "
            "Example: "
            "[{'type': 'mobile', 'value': '77774057759', 'is_primary': true}]. "
            "Field is optional, default is NULL."
        ),
    )
    profile_status: Mapped[PatientProfileStatusEnum] = mapped_column(
        SAEnum(
            PatientProfileStatusEnum,
            name="profile_status_enum",
            validate_strings=True,
            values_callable=lambda enums: [enum.value for enum in enums],
        ),
        nullable=True,
        server_default=PatientProfileStatusEnum.ACTIVE.value,
        comment="Patient's profile status. The optional field. Default is 'ACTIVE'.",
    )

    # Relationships
    citizenship = relationship("SQLAlchemyCitizenshipCatalogue", lazy="joined")
    nationality = relationship("SQLAlchemyNationalitiesCatalogue", lazy="joined")

    financing_sources: Mapped[List["SQLAlchemyFinancingSourcesCatalog"]] = relationship(
        "SQLAlchemyFinancingSourcesCatalog",
        secondary=patient_financing_source,
        lazy="selectin",
        backref="patients",
    )
    additional_attributes: Mapped[
        List["SQLAlchemyPatientContextAttributesCatalogue"]
    ] = relationship(
        "SQLAlchemyPatientContextAttributesCatalogue",
        secondary=patient_additional_attribute,
        lazy="selectin",
        backref="patients",
    )
    insurances: Mapped[List["SQLAlchemyInsuranceInfoCatalogue"]] = (  # noqa: F821
        relationship(
            "SQLAlchemyInsuranceInfoCatalogue",
            back_populates="patient",
            cascade="all, delete-orphan",
            lazy="selectin",
        )
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="patient",
        lazy="selectin",
    )
    diagnoses: Mapped[List["SQLAlchemyPatientsAndDiagnoses"]] = (  # noqa: F821
        relationship(
            "SQLAlchemyPatientsAndDiagnoses",  # in the diagnoses_catalogue.py
            back_populates="patient",
            lazy="selectin",
            cascade="all, delete-orphan",
        )
    )
