from typing import Dict

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.base import Base, ChangedAtMixin, CreatedAtMixin


class SQLAlchemyCitizenshipCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_citizenship"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    country_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        unique=True,
        comment="Citizenship country code (ISO)",
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Citizenship default name"
    )
    lang: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="Citizenship default language"
    )

    name_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Citizenship's name additional locales",
    )
