from datetime import datetime, time
from typing import List, Optional, Dict, Any
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
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class WeeklyScheduleResponseSchema(BaseModel):
    """Схема ответа для недельного расписания"""

    monday_enabled: bool = False
    monday_start_time: Optional[time] = None
    monday_end_time: Optional[time] = None

    tuesday_enabled: bool = False
    tuesday_start_time: Optional[time] = None
    tuesday_end_time: Optional[time] = None

    wednesday_enabled: bool = False
    wednesday_start_time: Optional[time] = None
    wednesday_end_time: Optional[time] = None

    thursday_enabled: bool = False
    thursday_start_time: Optional[time] = None
    thursday_end_time: Optional[time] = None

    friday_enabled: bool = False
    friday_start_time: Optional[time] = None
    friday_end_time: Optional[time] = None

    saturday_enabled: bool = False
    saturday_start_time: Optional[time] = None
    saturday_end_time: Optional[time] = None

    sunday_enabled: bool = False
    sunday_start_time: Optional[time] = None
    sunday_end_time: Optional[time] = None

    class Config:
        from_attributes = True


class PolyclinicAssetResponseSchema(BaseModel):
    """Схема ответа для актива поликлиники"""

    # Основные поля
    id: UUID
    bg_asset_id: Optional[str] = None

    # Связь с организацией
    organization_id: Optional[int]

    # Связь с пациентом
    patient_id: UUID
    patient_full_name: Optional[str] = None
    patient_iin: Optional[str] = None
    patient_birth_date: Optional[datetime] = None

    # Данные о получении актива
    receive_date: datetime
    receive_time: time
    actual_datetime: datetime
    received_from: str
    is_repeat: bool

    # Данные о посещении поликлиники
    visit_type: PolyclinicVisitTypeEnum = PolyclinicVisitTypeEnum.FIRST_VISIT
    visit_outcome: Optional[PolyclinicOutcomeEnum] = None

    # Расписание активов
    schedule_enabled: bool = False
    schedule_period_start: Optional[datetime] = None
    schedule_period_end: Optional[datetime] = None
    weekly_schedule: Optional[WeeklyScheduleResponseSchema] = None

    # Участок и специалист
    area: str
    specialization: str
    specialist: str
    service: PolyclinicServiceTypeEnum = PolyclinicServiceTypeEnum.CONSULTATION
    reason_appeal: PolyclinicReasonAppeal = PolyclinicReasonAppeal.PATRONAGE
    type_active_visit: PolyclinicTypeActiveVisit = PolyclinicTypeActiveVisit.FIRST_APPEAL

    # Примечание
    note: Optional[str] = None

    # Статусы
    status: AssetStatusEnum = AssetStatusEnum.REGISTERED
    delivery_status: AssetDeliveryStatusEnum = AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY

    # Флаги
    has_confirm: bool = False
    has_files: bool = False
    has_refusal: bool = False

    # Данные об отклонении
    rejection_reason_by: Optional[RejectionReasonByEnum] = None
    rejection_reason: Optional[str] = None

    # Метаданные
    created_at: datetime
    updated_at: datetime

    organization_data: Optional[Dict[str, Any]] = None
    patient_data: Optional[Dict[str, Any]] = None

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            AssetStatusEnum.REGISTERED: "Зарегистрирован",
            AssetStatusEnum.CONFIRMED: "Подтвержден",
            AssetStatusEnum.REFUSED: "Отказан",
            AssetStatusEnum.CANCELLED: "Отменен",
        }
        return status_map.get(self.status, "Неизвестно")

    def _get_delivery_status_display(self) -> str:
        """Получить отображаемое название статуса доставки"""
        status_map = {
            AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY: "Получен автоматически",
            AssetDeliveryStatusEnum.PENDING_DELIVERY: "Ожидает доставки",
            AssetDeliveryStatusEnum.DELIVERED: "Доставлен",
        }
        return status_map.get(self.delivery_status, "Неизвестно")

    def _get_visit_type_display(self) -> str:
        """Получить отображаемое название типа посещения"""
        type_map = {
            PolyclinicVisitTypeEnum.FIRST_VISIT: "Первичное обращение",
            PolyclinicVisitTypeEnum.REPEAT_VISIT: "Повторное обращение"
        }
        return type_map.get(self.visit_type, "Неизвестно")

    class Config:
        from_attributes = True
        extra = 'allow'


class PolyclinicAssetListItemSchema(BaseModel):
    """Схема для элемента списка активов поликлиники"""

    id: UUID  # ID актива

    organization_id: Optional[int]  # ID организации
    organization_name: Optional[str] = None  # Название организации

    patient_id: UUID  # ID пациента
    patient_full_name: str  # ФИО пациента
    patient_iin: str  # ИИН пациента
    patient_birth_date: datetime  # Дата рождения пациента

    area: str  # Участок
    specialization: str  # Специализация
    specialist: str  # Специалист
    service: PolyclinicServiceTypeEnum  # Услуга
    reason_appeal: PolyclinicReasonAppeal  # Повод обращения
    type_active_visit: PolyclinicTypeActiveVisit  # Тип активного посещения

    visit_type: PolyclinicVisitTypeEnum  # Тип посещения
    status: AssetStatusEnum  # Статус актива
    delivery_status: AssetDeliveryStatusEnum  # Статус доставки
    receive_date: datetime  # Дата получения
    receive_time: time  # Время получения

    created_at: datetime  # Дата создания
    updated_at: datetime  # Дата обновления

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            AssetStatusEnum.REGISTERED: "Зарегистрирован",
            AssetStatusEnum.CONFIRMED: "Подтвержден",
            AssetStatusEnum.REFUSED: "Отказан",
            AssetStatusEnum.CANCELLED: "Отменен",
        }
        return status_map.get(self.status, "Неизвестно")

    def _get_delivery_status_display(self) -> str:
        """Получить отображаемое название статуса доставки"""
        status_map = {
            AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY: "Получен автоматически",
            AssetDeliveryStatusEnum.PENDING_DELIVERY: "Ожидает доставки",
            AssetDeliveryStatusEnum.DELIVERED: "Доставлен",
        }
        return status_map.get(self.delivery_status, "Неизвестно")

    def _get_visit_type_display(self) -> str:
        """Получить отображаемое название типа посещения"""
        type_map = {
            PolyclinicVisitTypeEnum.FIRST_VISIT: "Первичное обращение",
            PolyclinicVisitTypeEnum.REPEAT_VISIT: "Повторное обращение",
        }
        return type_map.get(self.visit_type, "Неизвестно")

    class Config:
        from_attributes = True
        extra = 'allow'


class MultiplePolyclinicAssetsResponseSchema(BaseModel):
    """Схема ответа для списка активов поликлиники"""

    items: List[PolyclinicAssetListItemSchema]
    pagination: PaginationMetaDataSchema


class PolyclinicAssetDetailResponseSchema(BaseModel):
    """Схема ответа для детального просмотра актива поликлиники"""

    item: PolyclinicAssetResponseSchema


class PolyclinicAssetStatisticsSchema(BaseModel):
    """Схема статистики активов поликлиники"""

    total_assets: int
    confirmed_assets: int
    refused_assets: int
    pending_assets: int
    assets_with_files: int

    # Статистика по типу посещения
    first_visit_count: int = 0
    repeat_visit_count: int = 0
    preventive_count: int = 0
    follow_up_count: int = 0

    # Статистика по типу услуги
    consultation_count: int = 0
    procedure_count: int = 0
    diagnostic_count: int = 0
    vaccination_count: int = 0
    laboratory_count: int = 0

    # Статистика по исходу посещения
    recovered_count: int = 0
    improved_count: int = 0
    without_changes_count: int = 0
    worsened_count: int = 0
    referred_count: int = 0
    hospitalized_count: int = 0


class PolyclinicAssetsByOrganizationResponseSchema(BaseModel):
    """Схема ответа для активов поликлиники по организации"""

    organization_id: int
    organization_name: str
    organization_code: str
    total_assets: int
    items: List[PolyclinicAssetListItemSchema]
    pagination: PaginationMetaDataSchema


class PatientPolyclinicAssetsResponseSchema(BaseModel):
    """Схема ответа для активов поликлиники пациента"""

    patient_id: UUID
    patient_full_name: str
    patient_iin: str
    total_assets: int
    items: List[PolyclinicAssetListItemSchema]
    pagination: PaginationMetaDataSchema