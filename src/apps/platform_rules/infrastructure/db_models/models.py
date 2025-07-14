from typing import Any, Dict, Optional

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.base import Base, ChangedAtMixin, CreatedAtMixin


class SQLAlchemyPlatformRule(Base, CreatedAtMixin, ChangedAtMixin):
    __tablename__ = "platform_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # e.g. {"MAX_SCHEDULE_PERIOD": {"value": 90}} OR {"REDUCED_DAYS": {"dates": {...}}, ...}
    rule_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
