import datetime
import uuid
from typing import Any, Dict

from sqlalchemy import UUID as sqlalchemy_UUID
from sqlalchemy import DateTime, MetaData, func, orm
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.logger import LoggerService


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    type_annotation_map = {
        datetime.datetime: DateTime(timezone=True),
        Dict[str, Any]: JSONB,
    }


@orm.declarative_mixin
class PrimaryKey:
    id: orm.Mapped[uuid.UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


@orm.declarative_mixin
class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


@orm.declarative_mixin
class ChangedAtMixin:
    changed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BaseRepository:
    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        self._async_db_session = async_db_session
        self._logger = logger
