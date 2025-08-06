from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.catalogs.enums import IdentityDocumentTypeEnum
from src.shared.infrastructure.base import Base, ChangedAtMixin, CreatedAtMixin


class SQLAlchemyIdentityDocumentsCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_identity_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[IdentityDocumentTypeEnum] = mapped_column(
        SAEnum(
            IdentityDocumentTypeEnum,
            name="identity_document_type_enum",
            validate_strings=True,
            values_callable=lambda enums: [enum.value for enum in enums],
        ),
        nullable=False,
        comment="Identity document type",
    )
    series: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    issued_by: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # FKs
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Patient ID",
    )

    # Relationship
    patient: Mapped["SQLAlchemyPatient"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "SQLAlchemyPatient",
        back_populates="identity_documents",
    )
