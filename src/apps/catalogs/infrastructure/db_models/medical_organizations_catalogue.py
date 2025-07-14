from typing import Dict

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.base import Base, ChangedAtMixin, CreatedAtMixin


class SQLAlchemyMedicalOrganizationsCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_medical_organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Medical organization internal code",
        unique=True,
    )
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="Medical organization default name",
        unique=True,
    )
    address: Mapped[str] = mapped_column(
        String(256), nullable=False, comment="Medical organization default address"
    )
    lang: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="Medical organization default language"
    )

    name_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Medical organization's name additional locales",
    )
    address_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Medical organization's address additional locales",
    )
