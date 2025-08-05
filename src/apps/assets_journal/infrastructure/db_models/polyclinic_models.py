from datetime import datetime, time
from typing import Dict, Any

from sqlalchemy import Boolean, DateTime, Enum, String, Text, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
    PolyclinicVisitTypeEnum,
    PolyclinicServiceTypeEnum,
    PolyclinicOutcomeEnum,
    RejectionReasonByEnum, PolyclinicReasonAppeal, PolyclinicTypeActiveVisit,
)
from src.shared.infrastructure.base import (
    Base,
    ChangedAtMixin,
    CreatedAtMixin,
    PrimaryKey,
)


class PolyclinicAsset(Base, PrimaryKey, CreatedAtMixin, ChangedAtMixin):
    """
    Модель актива поликлиники
    """
    __tablename__ = "polyclinic_assets"

    # Данные из BG
    bg_asset_id: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)

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

    # Данные о посещении поликлиники
    visit_type: Mapped[PolyclinicVisitTypeEnum] = mapped_column(
        Enum(PolyclinicVisitTypeEnum), nullable=False, default=PolyclinicVisitTypeEnum.FIRST_VISIT
    )
    visit_outcome: Mapped[PolyclinicOutcomeEnum] = mapped_column(
        Enum(PolyclinicOutcomeEnum), nullable=True
    )

    # Расписание активов (планирование на будущие периоды)
    schedule_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    schedule_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    schedule_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Недельное расписание в формате JSON
    weekly_schedule: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Недельное расписание работы в формате JSON",
    )

    # Участок и специалист
    area: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(255), nullable=False)
    specialist: Mapped[str] = mapped_column(String(255), nullable=False)
    service: Mapped[PolyclinicServiceTypeEnum] = mapped_column(
        Enum(PolyclinicServiceTypeEnum), nullable=False, default=PolyclinicServiceTypeEnum.CONSULTATION
    )
    reason_appeal: Mapped[PolyclinicReasonAppeal] = mapped_column(
        Enum(PolyclinicReasonAppeal), nullable=False, default=PolyclinicReasonAppeal.PATRONAGE
    )
    type_active_visit: Mapped[PolyclinicTypeActiveVisit] = mapped_column(
        Enum(PolyclinicTypeActiveVisit), nullable=False, default=PolyclinicTypeActiveVisit.FIRST_APPEAL
    )

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

    # Данные об отклонении
    rejection_reason_by: Mapped[RejectionReasonByEnum] = mapped_column(
        Enum(RejectionReasonByEnum), nullable=True
    )
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)

    # Связи
    patient = relationship(
        "SQLAlchemyPatient",
        foreign_keys=[patient_id],
        lazy="joined",
    )