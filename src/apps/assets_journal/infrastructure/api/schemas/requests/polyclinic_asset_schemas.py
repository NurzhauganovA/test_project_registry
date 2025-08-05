from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
    PolyclinicVisitTypeEnum,
    PolyclinicServiceTypeEnum,
    PolyclinicOutcomeEnum,
    RejectionReasonByEnum, PolyclinicReasonAppeal, PolyclinicTypeActiveVisit,
)


class WeeklyScheduleSchema(BaseModel):
    """Схема недельного расписания"""

    monday_enabled: bool = Field(default=False, description="Понедельник включен")
    monday_start_time: Optional[time] = Field(default=None, description="Время начала в понедельник")
    monday_end_time: Optional[time] = Field(default=None, description="Время окончания в понедельник")

    tuesday_enabled: bool = Field(default=False, description="Вторник включен")
    tuesday_start_time: Optional[time] = Field(default=None, description="Время начала во вторник")
    tuesday_end_time: Optional[time] = Field(default=None, description="Время окончания во вторник")

    wednesday_enabled: bool = Field(default=False, description="Среда включена")
    wednesday_start_time: Optional[time] = Field(default=None, description="Время начала в среду")
    wednesday_end_time: Optional[time] = Field(default=None, description="Время окончания в среду")

    thursday_enabled: bool = Field(default=False, description="Четверг включен")
    thursday_start_time: Optional[time] = Field(default=None, description="Время начала в четверг")
    thursday_end_time: Optional[time] = Field(default=None, description="Время окончания в четверг")

    friday_enabled: bool = Field(default=False, description="Пятница включена")
    friday_start_time: Optional[time] = Field(default=None, description="Время начала в пятницу")
    friday_end_time: Optional[time] = Field(default=None, description="Время окончания в пятницу")

    saturday_enabled: bool = Field(default=False, description="Суббота включена")
    saturday_start_time: Optional[time] = Field(default=None, description="Время начала в субботу")
    saturday_end_time: Optional[time] = Field(default=None, description="Время окончания в субботу")

    sunday_enabled: bool = Field(default=False, description="Воскресенье включено")
    sunday_start_time: Optional[time] = Field(default=None, description="Время начала в воскресенье")
    sunday_end_time: Optional[time] = Field(default=None, description="Время окончания в воскресенье")

    class Config:
        json_schema_extra = {
            "example": {
                "monday_enabled": True,
                "monday_start_time": "08:00:00",
                "monday_end_time": "17:00:00",
                "tuesday_enabled": True,
                "tuesday_start_time": "08:00:00",
                "tuesday_end_time": "17:00:00",
                "wednesday_enabled": False,
                "thursday_enabled": True,
                "thursday_start_time": "09:00:00",
                "thursday_end_time": "18:00:00",
                "friday_enabled": True,
                "friday_start_time": "08:00:00",
                "friday_end_time": "16:00:00",
                "saturday_enabled": False,
                "sunday_enabled": False
            }
        }


class CreatePolyclinicAssetSchema(BaseModel):
    """Схема для создания актива поликлиники"""

    # Данные из BG
    bg_asset_id: Optional[str] = Field(default=None, description="ID из BG системы")

    # Связь с пациентом
    patient_iin: str = Field(..., description="ИИН пациента")

    # Данные о получении актива
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Данные о посещении поликлиники
    visit_type: PolyclinicVisitTypeEnum = Field(
        default=PolyclinicVisitTypeEnum.FIRST_VISIT,
        description="Тип посещения"
    )
    visit_outcome: Optional[PolyclinicOutcomeEnum] = Field(default=None, description="Исход посещения")

    # Расписание активов
    schedule_enabled: Optional[bool] = Field(default=None, description="Запланировать несколько активов на будущий период")
    schedule_period_start: Optional[datetime] = Field(default=None, description="Период планирования активов с")
    schedule_period_end: Optional[datetime] = Field(default=None, description="Период планирования активов по")
    weekly_schedule: Optional[WeeklyScheduleSchema] = Field(default=None, description="Недельное расписание")

    # Участок и специалист
    area: Optional[str] = Field(default=None, description="Участок")
    specialization: Optional[str] = Field(default=None, description="Специализация")
    specialist: Optional[str] = Field(default=None, description="Специалист")
    service: PolyclinicServiceTypeEnum = Field(
        default=PolyclinicServiceTypeEnum.CONSULTATION,
        description="Услуга"
    )
    reason_appeal: PolyclinicReasonAppeal = Field(
        default=PolyclinicReasonAppeal.PATRONAGE,
        description="Причина обращения"
    )
    type_active_visit: PolyclinicTypeActiveVisit = Field(
        default=PolyclinicTypeActiveVisit.FIRST_APPEAL,
        description="Тип активного посещения"
    )

    # Примечание
    note: Optional[str] = Field(default=None, description="Примечание")

    # Статусы (для внутреннего использования)
    status: Optional[AssetStatusEnum] = Field(default=None, description="Статус актива")
    delivery_status: Optional[AssetDeliveryStatusEnum] = Field(default=None, description="Статус доставки")


class CreatePolyclinicAssetByPatientIdSchema(BaseModel):
    """Схема для создания актива поликлиники по ID пациента"""

    # Данные из BG
    bg_asset_id: Optional[str] = Field(default=None, description="ID из BG системы")

    # Связь с пациентом
    patient_id: UUID = Field(..., description="ID существующего пациента")

    # Данные о получении актива
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Данные о посещении поликлиники
    visit_type: PolyclinicVisitTypeEnum = Field(
        default=PolyclinicVisitTypeEnum.FIRST_VISIT,
        description="Тип посещения"
    )
    visit_outcome: Optional[PolyclinicOutcomeEnum] = Field(default=None, description="Исход посещения")

    # Расписание активов
    schedule_enabled: bool = Field(default=False, description="Запланировать несколько активов на будущий период")
    schedule_period_start: Optional[datetime] = Field(default=None, description="Период планирования активов с")
    schedule_period_end: Optional[datetime] = Field(default=None, description="Период планирования активов по")
    weekly_schedule: Optional[WeeklyScheduleSchema] = Field(default=None, description="Недельное расписание")

    # Участок и специалист
    area: str = Field(..., description="Участок")
    specialization: str = Field(..., description="Специализация")
    specialist: str = Field(..., description="Специалист")
    service: PolyclinicServiceTypeEnum = Field(
        default=PolyclinicServiceTypeEnum.CONSULTATION,
        description="Услуга"
    )
    reason_appeal: PolyclinicReasonAppeal = Field(
        default=PolyclinicReasonAppeal.PATRONAGE,
        description="Причина обращения"
    )
    type_active_visit: PolyclinicTypeActiveVisit = Field(
        default=PolyclinicTypeActiveVisit.FIRST_APPEAL,
        description="Тип активного посещения"
    )

    # Примечание
    note: Optional[str] = Field(default=None, description="Примечание")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671309",
                "patient_id": "43524a25-869c-4564-afcc-ddb27b8752f0",
                "receive_date": "2025-03-22T10:55:00",
                "receive_time": "10:55:00",
                "actual_datetime": "2025-03-22T10:55:00",
                "received_from": "Поликлиника №1",
                "is_repeat": False,
                "visit_type": "first_visit",
                "schedule_enabled": False,
                "area": "Терапевтический",
                "specialization": "Терапевт",
                "specialist": "Малышева А.О.",
                "service": "consultation",
                "reason_appeal": "patronage",
                "type_active_visit": "first_appeal",
                "note": "Плановый осмотр"
            }
        }


class RejectPolyclinicAssetSchema(BaseModel):
    """Схема для отклонения актива поликлиники"""

    rejection_reason_by: RejectionReasonByEnum = Field(..., description="Кто отклонил актив")
    rejection_reason: str = Field(..., description="Причина отклонения")

    class Config:
        json_schema_extra = {
            "example": {
                "rejection_reason_by": "patient",
                "rejection_reason": "Пациент не может прийти на прием"
            }
        }


class TransferPolyclinicAssetSchema(BaseModel):
    """Схема для передачи актива поликлиники другой организации"""

    new_organization_id: int = Field(..., description="ID новой организации")
    transfer_reason: Optional[str] = Field(default=None, description="Причина передачи")
    update_patient_attachment: bool = Field(
        default=True,
        description="Обновить attachment_data пациента с новой организацией"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "new_organization_id": 1,
                "transfer_reason": "Перенаправление к узкому специалисту",
                "update_patient_attachment": True
            }
        }


class PolyclinicAssetFilterParams:
    """Параметры фильтрации активов поликлиники"""

    def __init__(
            self,
            # Поиск по пациенту
            patient_search: Optional[str] = None,
            patient_id: Optional[UUID] = None,
            patient_iin: Optional[str] = None,

            # Период
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,

            # Статус актива
            status: Optional[AssetStatusEnum] = None,

            # Статус доставки
            delivery_status: Optional[AssetDeliveryStatusEnum] = None,

            # Участок
            area: Optional[str] = None,

            # Специализация
            specialization: Optional[str] = None,

            # Специалист
            specialist: Optional[str] = None,

            # Тип посещения
            visit_type: Optional[PolyclinicVisitTypeEnum] = None,

            # Услуга
            service: Optional[PolyclinicServiceTypeEnum] = None,

            # Повод посещения
            reason_appeal: Optional[PolyclinicReasonAppeal] = None,

            # Тип активного посещения
            type_active_visit: Optional[PolyclinicTypeActiveVisit] = None,

            # Исход посещения
            visit_outcome: Optional[PolyclinicOutcomeEnum] = None,

            # ID организации (может быть передан вручную для фильтрации)
            organization_id: Optional[int] = None,
    ):
        self.patient_search = patient_search
        self.patient_id = patient_id
        self.patient_iin = patient_iin
        self.date_from = date_from
        self.date_to = date_to
        self.status = status
        self.delivery_status = delivery_status
        self.area = area
        self.specialization = specialization
        self.specialist = specialist
        self.service = service
        self.reason_appeal = reason_appeal
        self.type_active_visit = type_active_visit
        self.visit_type = visit_type
        self.visit_outcome = visit_outcome
        self.organization_id = organization_id

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = {}
        for key, value in vars(self).items():
            if not exclude_none or value is not None:
                # Преобразуем enum в его значение
                if isinstance(value, (
                    AssetStatusEnum,
                    AssetDeliveryStatusEnum,
                    PolyclinicVisitTypeEnum,
                    PolyclinicServiceTypeEnum,
                    PolyclinicOutcomeEnum,
                    PolyclinicReasonAppeal,
                    PolyclinicTypeActiveVisit
                )):
                    data[key] = value.value
                else:
                    data[key] = value
        return data
    schedule_enabled: bool = Field(default=False, description="Запланировать несколько активов на будущий период")
    schedule_period_start: Optional[datetime] = Field(default=None, description="Период планирования активов с")
    schedule_period_end: Optional[datetime] = Field(default=None, description="Период планирования активов по")
    weekly_schedule: Optional[WeeklyScheduleSchema] = Field(default=None, description="Недельное расписание")

    # Участок и специалист
    area: str = Field(..., description="Участок")
    specialization: str = Field(..., description="Специализация")
    specialist: str = Field(..., description="Специалист")
    service: Optional[PolyclinicServiceTypeEnum] = Field(
        default=PolyclinicServiceTypeEnum.CONSULTATION,
        description="Услуга"
    )
    reason_appeal: Optional[PolyclinicReasonAppeal] = Field(
        default=PolyclinicReasonAppeal.PATRONAGE,
        description="Причина обращения"
    )
    type_active_visit: Optional[PolyclinicTypeActiveVisit] = Field(
        default=PolyclinicTypeActiveVisit.FIRST_APPEAL,
        description="Тип активного посещения"
    )

    # Примечание
    note: Optional[str] = Field(default=None, description="Примечание")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671309",
                "patient_iin": "030611550511",
                "receive_date": "2025-03-22T10:55:00",
                "receive_time": "10:55:00",
                "actual_datetime": "2025-03-22T10:55:00",
                "received_from": "Поликлиника №1",
                "is_repeat": False,
                "visit_type": "first_visit",
                "service_type": "consultation",
                "schedule_enabled": True,
                "schedule_period_start": "2025-03-25T00:00:00",
                "schedule_period_end": "2025-04-25T23:59:59",
                "weekly_schedule": {
                    "monday_enabled": True,
                    "monday_start_time": "08:00:00",
                    "monday_end_time": "17:00:00",
                    "tuesday_enabled": True,
                    "tuesday_start_time": "08:00:00",
                    "tuesday_end_time": "17:00:00"
                },
                "area": "Терапевтический",
                "specialization": "Терапевт",
                "specialist": "Малышева А.О.",
                "service": "consultation",
                "reason_appeal": "patronage",
                "type_active_visit": "first_appeal",
                "note": "Плановый осмотр"
            }
        }


class UpdatePolyclinicAssetSchema(BaseModel):
    """Схема для обновления актива поликлиники"""

    # Данные о получении актива
    receive_date: Optional[datetime] = Field(default=None, description="Дата получения")
    receive_time: Optional[time] = Field(default=None, description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: Optional[str] = Field(default=None, description="Получено от")
    is_repeat: Optional[bool] = Field(default=None, description="Повторный")

    # Данные о посещении поликлиники
    visit_type: Optional[PolyclinicVisitTypeEnum] = Field(default=None, description="Тип посещения")
    service: Optional[PolyclinicServiceTypeEnum] = Field(default=None, description="Услуга")
    reason_appeal: Optional[PolyclinicReasonAppeal] = Field(default=None, description="Причина обращения")
    type_active_visit: Optional[PolyclinicTypeActiveVisit] = Field(default=None, description="Тип активного посещения")
    visit_outcome: Optional[PolyclinicOutcomeEnum] = Field(default=None, description="Исход посещения")

    # Расписание активов
    schedule_enabled: Optional[bool] = Field(default=None, description="Запланировать несколько активов на будущий период")
    schedule_period_start: Optional[datetime] = Field(default=None, description="Период планирования активов с")
    schedule_period_end: Optional[datetime] = Field(default=None, description="Период планирования активов по")
    weekly_schedule: Optional[WeeklyScheduleSchema] = Field(default=None, description="Недельное расписание")

    # Участок и специалист
    area: Optional[str] = Field(default=None, description="Участок")
    specialization: Optional[str] = Field(default=None, description="Специализация")
    specialist: Optional[str] = Field(default=None, description="Специалист")
    note: Optional[str] = Field(default=None, description="Примечание")
    status: Optional[AssetStatusEnum] = Field(default=None, description="Статус актива")
    delivery_status: Optional[AssetDeliveryStatusEnum] = Field(default=None, description="Статус доставки")