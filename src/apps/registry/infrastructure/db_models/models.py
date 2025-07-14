import uuid
from datetime import date, datetime, time
from typing import Dict, List

from sqlalchemy import UUID as sqlalchemy_UUID
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.apps.registry.domain.enums import (
    AppointmentInsuranceType,
    AppointmentStatusEnum,
    AppointmentTypeEnum,
)
from src.shared.infrastructure.base import (
    Base,
    ChangedAtMixin,
    CreatedAtMixin,
    PrimaryKey,
)

# flake8: noqa: F821


class Schedule(Base, PrimaryKey, CreatedAtMixin, ChangedAtMixin):
    __tablename__ = "schedules"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )  # User's id from the Auth Service (Keycloak)
    schedule_name: Mapped[str] = mapped_column(String(20), nullable=False)

    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # 0 <= appointment_interval <= 60
    appointment_interval: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15,
    )
    description: Mapped[str] = mapped_column(String(256), nullable=True)

    days: Mapped[List["ScheduleDay"]] = relationship(
        "ScheduleDay", back_populates="schedule", cascade="all, delete-orphan"
    )

    doctor: Mapped["User"] = relationship(
        "User",
        back_populates="schedules",
        foreign_keys=[doctor_id],
        lazy="joined",
    )

    __table_args__ = (
        CheckConstraint(
            "appointment_interval >= 0 AND appointment_interval <= 60",
            name="ck_appointment_interval_range",
        ),
    )


class ScheduleDay(Base, PrimaryKey, CreatedAtMixin, ChangedAtMixin):
    __tablename__ = "schedule_days"

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )  # 1 - Monday, ..., 7 - Sunday
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    work_start_time: Mapped[time] = mapped_column(Time, nullable=False)
    work_end_time: Mapped[time] = mapped_column(Time, nullable=False)
    break_start_time: Mapped[time] = mapped_column(Time, nullable=True)
    break_end_time: Mapped[time] = mapped_column(Time, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="days")
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="schedule_day", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "day_of_week BETWEEN 1 AND 7", name="ck_schedule_days_day_of_week"
        ),
    )


class Appointment(Base, CreatedAtMixin, ChangedAtMixin):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    time: Mapped[time] = mapped_column(Time, nullable=False)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=True,
    )  # User's id from the Auth Service
    status: Mapped[AppointmentStatusEnum] = mapped_column(
        Enum(AppointmentStatusEnum), nullable=False
    )
    type: Mapped[AppointmentTypeEnum] = mapped_column(
        Enum(AppointmentTypeEnum), nullable=False
    )
    insurance_type: Mapped[AppointmentInsuranceType] = mapped_column(
        Enum(AppointmentInsuranceType), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    additional_services: Mapped[Dict[str, bool]] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    schedule_day_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("schedule_days.id", ondelete="CASCADE"), nullable=False
    )

    # Optional field to track when the appointment was cancelled (updatable only by the server)
    cancelled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    patient: Mapped["SQLAlchemyPatient"] = relationship(
        "SQLAlchemyPatient",
        back_populates="appointments",
        foreign_keys=[patient_id],
        lazy="joined",
    )
    schedule_day: Mapped["ScheduleDay"] = relationship(
        "ScheduleDay", back_populates="appointments"
    )
