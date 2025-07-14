from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Boolean, Date

from src.shared.infrastructure.base import (
    Base,
    ChangedAtMixin,
    CreatedAtMixin,
    PrimaryKey,
)


class SQLAlchemyDiagnosesCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_diagnoses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    diagnosis_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        comment="Diagnosis code",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
        comment="Diagnosis description",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    # Relationships
    patients: Mapped[List["SQLAlchemyPatientsAndDiagnoses"]] = relationship(
        "SQLAlchemyPatientsAndDiagnoses", back_populates="diagnosis", lazy="selectin"
    )


class SQLAlchemyPatientsAndDiagnoses(Base, PrimaryKey, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "patients_and_diagnoses"

    # Primary key is not needed here - it's provided by the 'PrimaryKey' mixin

    date_diagnosed: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    # FKs
    diagnosis_id: Mapped[int] = mapped_column(
        ForeignKey("cat_diagnoses.id"), nullable=False
    )
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relationships
    diagnosis: Mapped["SQLAlchemyDiagnosesCatalogue"] = relationship(
        "SQLAlchemyDiagnosesCatalogue", lazy="joined"
    )
    patient: Mapped["SQLAlchemyPatient"] = relationship(  # noqa: F821
        "SQLAlchemyPatient", lazy="joined"
    )
    doctor: Mapped[Optional["User"]] = relationship("User", lazy="joined")  # noqa: F821
