from datetime import datetime, date

from sqlalchemy import Boolean, DateTime, Enum, String, Text, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.apps.assets_journal.domain.enums import (
    StaffAssignmentStatusEnum,
    MedicalSpecializationEnum,
    MedicalDepartmentEnum,
    AreaTypeEnum,
)
from src.shared.infrastructure.base import (
    Base,
    ChangedAtMixin,
    CreatedAtMixin,
    PrimaryKey,
)


class StaffAssignment(Base, PrimaryKey, CreatedAtMixin, ChangedAtMixin):
    """
    Модель назначения медперсонала на участок
    """
    __tablename__ = "staff_assignments"

    # Данные специалиста
    specialist_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    specialization: Mapped[MedicalSpecializationEnum] = mapped_column(
        Enum(MedicalSpecializationEnum), nullable=False, index=True
    )

    # Назначение
    area_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    area_type: Mapped[AreaTypeEnum] = mapped_column(
        Enum(AreaTypeEnum), nullable=False
    )
    department: Mapped[MedicalDepartmentEnum] = mapped_column(
        Enum(MedicalDepartmentEnum), nullable=False, index=True
    )

    # Период работы
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=True, index=True)

    # Время работы (в минутах для точности)
    reception_hours_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reception_minutes_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    area_hours_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    area_minutes_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Статус
    status: Mapped[StaffAssignmentStatusEnum] = mapped_column(
        Enum(StaffAssignmentStatusEnum), nullable=False, default=StaffAssignmentStatusEnum.ACTIVE, index=True
    )

    # Дополнительная информация
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)