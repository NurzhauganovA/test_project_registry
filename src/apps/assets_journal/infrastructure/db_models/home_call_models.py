from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, Enum, String, Text, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.assets_journal.domain.enums import (
    HomeCallStatusEnum,
    HomeCallCategoryEnum,
    HomeCallSourceEnum,
    HomeCallReasonEnum,
    HomeCallTypeEnum,
    HomeCallVisitTypeEnum,
)
from src.shared.infrastructure.base import (
    Base,
    ChangedAtMixin,
    CreatedAtMixin,
    PrimaryKey,
)


class HomeCall(Base, PrimaryKey, CreatedAtMixin, ChangedAtMixin):
    """
    Модель вызова на дом
    """
    __tablename__ = "home_calls"

    # Номер вызова
    call_number: Mapped[str] = mapped_column(String(50), nullable=True, index=True)

    # Связь с пациентом
    patient_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Адрес и телефон пациента
    patient_address: Mapped[str] = mapped_column(Text, nullable=True)
    patient_phone: Mapped[str] = mapped_column(String(20), nullable=True)

    # Данные о регистрации вызова
    registration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    registration_time: Mapped[time] = mapped_column(Time, nullable=False)
    registration_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Исполнение вызова
    execution_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_time: Mapped[time] = mapped_column(Time, nullable=True)

    # Медицинские данные
    area: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(255), nullable=False)
    specialist: Mapped[str] = mapped_column(String(255), nullable=False)

    # Страхование
    is_insured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_oms: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Данные о вызове
    source: Mapped[HomeCallSourceEnum] = mapped_column(
        Enum(HomeCallSourceEnum), nullable=False
    )
    category: Mapped[HomeCallCategoryEnum] = mapped_column(
        Enum(HomeCallCategoryEnum), nullable=False
    )
    reason: Mapped[HomeCallReasonEnum] = mapped_column(
        Enum(HomeCallReasonEnum), nullable=False
    )
    call_type: Mapped[HomeCallTypeEnum] = mapped_column(
        Enum(HomeCallTypeEnum), nullable=False
    )
    reason_patient_words: Mapped[str] = mapped_column(Text, nullable=True)
    visit_type: Mapped[HomeCallVisitTypeEnum] = mapped_column(
        Enum(HomeCallVisitTypeEnum), nullable=False, default=HomeCallVisitTypeEnum.PRIMARY
    )

    # Статус и примечания
    status: Mapped[HomeCallStatusEnum] = mapped_column(
        Enum(HomeCallStatusEnum), nullable=False, default=HomeCallStatusEnum.REGISTERED
    )
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Связи
    patient = relationship(
        "SQLAlchemyPatient",
        foreign_keys=[patient_id],
        lazy="joined",
    )