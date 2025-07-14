from typing import Dict, List

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.catalogs.infrastructure.db_models.insurance_info_catalogue import (
    SQLAlchemyInsuranceInfoCatalogue,
)
from src.shared.infrastructure.base import Base, ChangedAtMixin, CreatedAtMixin


class SQLAlchemyFinancingSourcesCatalog(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_financing_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Financing source default name",
        unique=True,
    )
    code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Financing source code", unique=True
    )
    lang: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="Financing source default language"
    )

    name_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Financing source's name additional locales",
    )

    insurance_info_records: Mapped[List["SQLAlchemyInsuranceInfoCatalogue"]] = (
        relationship(
            "SQLAlchemyInsuranceInfoCatalogue",
            back_populates="financing_source",
            lazy="selectin",
            cascade="all, delete-orphan",
        )
    )
