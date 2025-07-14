from datetime import date
from typing import Dict, List, Optional, Union

from sqlalchemy import Boolean, Date, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.base import (
    Base,
    ChangedAtMixin,
    CreatedAtMixin,
    PrimaryKey,
)

# flake8: noqa: F821


class User(Base, PrimaryKey, CreatedAtMixin, ChangedAtMixin):
    __tablename__ = "users"

    # Primary key - id from the Auth Service
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=True)
    full_name = mapped_column(String(256), nullable=True)
    iin: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    client_roles: Mapped[List[str]] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    specializations: Mapped[List[Dict[str, Optional[str]]]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    attachment_data: Mapped[Dict[str, Union[int, str]]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )
    served_patient_types: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    # Refers to the checkbox types: "С направлением" (with_referral), "Без направления" (without_referral)
    served_referral_types: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    # Refers to the checkbox types: "Внешняя организация" (from_external_organization),
    # "Самозапись" (self_registration)
    served_referral_origins: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    # Refers to possible types of payment schedules: "ГОБМП" (GOBMP), "ДМС" (DMS),
    # "ОСМС" (OSMS), "Платные" (Paid)
    served_payment_types: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )

    schedules: Mapped[List["Schedule"]] = relationship(
        "Schedule",
        back_populates="doctor",
        cascade="all, delete-orphan",
        foreign_keys="Schedule.doctor_id",
    )

    # Relationships
    diagnoses: Mapped[List["SQLAlchemyPatientsAndDiagnoses"]] = relationship(
        "SQLAlchemyPatientsAndDiagnoses", back_populates="doctor", lazy="selectin"
    )
