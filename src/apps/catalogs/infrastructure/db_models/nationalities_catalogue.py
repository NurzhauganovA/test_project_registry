from typing import Dict

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.base import Base, ChangedAtMixin, CreatedAtMixin


class SQLAlchemyNationalitiesCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_nationalities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Nationality default name"
    )
    lang: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="Nationality default language"
    )

    name_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Nationality's name additional locales",
    )
