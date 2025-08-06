from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.base import Base, ChangedAtMixin, CreatedAtMixin


class SQLAlchemyInsuranceInfoCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_insurance_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    policy_number: Mapped[str] = mapped_column(
        String(50), nullable=True, comment="Insurance policy number"
    )
    company: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Insurance company name"
    )
    valid_from: Mapped[date] = mapped_column(
        Date, nullable=True, comment="Insurance valid from"
    )
    valid_till: Mapped[date] = mapped_column(
        Date, nullable=True, comment="Insurance valid till"
    )
    comment: Mapped[str] = mapped_column(
        String(256), nullable=True, comment="Insurance comment"
    )

    # Relations with different tables
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patients.id"), nullable=False, comment="Insurance ID"
    )
    patient: Mapped["SQLAlchemyPatient"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "SQLAlchemyPatient",
        back_populates="insurances",
        lazy="selectin",
    )

    financing_source_id: Mapped[int] = mapped_column(
        ForeignKey("cat_financing_sources.id"),
        nullable=False,
        comment="Financing source ID",
    )
    financing_source: Mapped["SQLAlchemyFinancingSourcesCatalog"] = (  # type: ignore[name-defined]  # noqa: F821
        relationship(
            "SQLAlchemyFinancingSourcesCatalog",
            back_populates="insurance_info_records",
            lazy="selectin",
        )
    )
