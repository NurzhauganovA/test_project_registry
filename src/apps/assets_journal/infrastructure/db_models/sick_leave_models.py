from datetime import datetime, date, time

from sqlalchemy import Boolean, DateTime, Enum, String, Text, Date, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.assets_journal.domain.enums import (
    SickLeaveStatusEnum,
    SickLeaveReasonEnum,
    WorkCapacityEnum,
)
from src.shared.infrastructure.base import (
    Base,
    ChangedAtMixin,
    CreatedAtMixin,
    PrimaryKey,
)


class SickLeave(Base, PrimaryKey, CreatedAtMixin, ChangedAtMixin):
    """
    Модель больничного листа
    """
    __tablename__ = "sick_leaves"

    # Связь с пациентом
    patient_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Адрес проживания пациента
    patient_location_address: Mapped[str] = mapped_column(Text, nullable=True)

    # Данные о получении
    receive_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    receive_time: Mapped[time] = mapped_column(Time, nullable=False)
    actual_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_from: Mapped[str] = mapped_column(String(255), nullable=False)
    is_repeat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Наименование места работы
    workplace_name: Mapped[str] = mapped_column(String(500), nullable=True)

    # Период нетрудоспособности
    disability_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    disability_end_date: Mapped[date] = mapped_column(Date, nullable=True)

    # Медицинские данные
    status: Mapped[SickLeaveStatusEnum] = mapped_column(
        Enum(SickLeaveStatusEnum), nullable=False, default=SickLeaveStatusEnum.OPEN
    )
    sick_leave_reason: Mapped[SickLeaveReasonEnum] = mapped_column(
        Enum(SickLeaveReasonEnum), nullable=True
    )
    work_capacity: Mapped[WorkCapacityEnum] = mapped_column(
        Enum(WorkCapacityEnum), nullable=False, default=WorkCapacityEnum.TEMPORARILY_DISABLED
    )

    # Участок и специалист
    area: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(255), nullable=False)
    specialist: Mapped[str] = mapped_column(String(255), nullable=False)

    # Дополнительная информация
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    parent_sick_leave_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sick_leaves.id"),
        nullable=True,
    )

    # Связи
    patient = relationship(
        "SQLAlchemyPatient",
        foreign_keys=[patient_id],
        lazy="joined",
    )

    # Самоссылка для продлений - ИСПРАВЛЕНО
    parent_sick_leave = relationship(
        "SickLeave",
        remote_side="SickLeave.id",  # Используем строку вместо выражения
        back_populates="extensions",
        foreign_keys=[parent_sick_leave_id],
    )

    extensions = relationship(
        "SickLeave",
        back_populates="parent_sick_leave",
        cascade="all, delete-orphan",
    )