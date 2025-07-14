from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, Enum, String, Text, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)
from src.shared.infrastructure.base import (
    Base,
    ChangedAtMixin,
    CreatedAtMixin,
    PrimaryKey,
)


class StationaryAsset(Base, PrimaryKey, CreatedAtMixin, ChangedAtMixin):
    """
    Модель актива стационара
    """
    __tablename__ = "stationary_assets"

    # Данные из BG
    bg_asset_id: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    card_number: Mapped[str] = mapped_column(String(50), nullable=True)

    # Связь с пациентом
    patient_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Данные о получении актива
    receive_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    receive_time: Mapped[time] = mapped_column(Time, nullable=False)
    actual_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_from: Mapped[str] = mapped_column(String(255), nullable=False)
    is_repeat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Данные пребывания в стационаре
    stay_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stay_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    stay_outcome: Mapped[str] = mapped_column(String(255), nullable=True)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=False)

    # Участок и специалист
    area: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(255), nullable=True)
    specialist: Mapped[str] = mapped_column(String(255), nullable=False)

    # Примечание
    note: Mapped[str] = mapped_column(Text, nullable=True)

    # Статусы
    status: Mapped[AssetStatusEnum] = mapped_column(
        Enum(AssetStatusEnum), nullable=False, default=AssetStatusEnum.REGISTERED
    )
    delivery_status: Mapped[AssetDeliveryStatusEnum] = mapped_column(
        Enum(AssetDeliveryStatusEnum),
        nullable=False,
        default=AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY
    )
    reg_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=datetime.utcnow
    )

    # Флаги для совместимости с BG
    has_confirm: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_files: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_refusal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Связи
    patient = relationship(
        "SQLAlchemyPatient",
        foreign_keys=[patient_id],
        lazy="joined",
    )