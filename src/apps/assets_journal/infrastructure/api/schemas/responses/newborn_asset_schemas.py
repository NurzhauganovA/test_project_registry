from datetime import datetime, time
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
    DiagnosisTypeEnum,
    DeliveryTypeEnum,
    PregnancyWeekEnum,
    NewbornConditionEnum,
    TransferDestinationEnum,
    MedicalServiceTypeEnum,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class NewbornDiagnosisResponseSchema(BaseModel):
    """Схема ответа для диагноза новорожденного"""

    diagnosis_type: DiagnosisTypeEnum
    diagnosis_code: str
    diagnosis_name: str
    note: Optional[str] = None

    class Config:
        from_attributes = True


class MotherDataResponseSchema(BaseModel):
    """Схема ответа для данных о матери"""

    iin: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[datetime] = None
    birth_time: Optional[time] = None
    delivery_type: Optional[DeliveryTypeEnum] = None
    pregnancy_weeks: Optional[PregnancyWeekEnum] = None
    discharge_date: Optional[datetime] = None
    discharge_time: Optional[time] = None

    class Config:
        from_attributes = True


class NewbornDataResponseSchema(BaseModel):
    """Схема ответа для данных о новорожденном"""

    birth_date: Optional[datetime] = None
    birth_time: Optional[time] = None
    weight_grams: Optional[Decimal] = None
    height_cm: Optional[Decimal] = None
    transfer_destination: Optional[TransferDestinationEnum] = None
    condition: Optional[NewbornConditionEnum] = None
    medical_services: List[MedicalServiceTypeEnum] = Field(default_factory=list)

    class Config:
        from_attributes = True


class NewbornAssetResponseSchema(BaseModel):
    """Схема ответа для актива новорожденного"""

    # Основные поля
    id: UUID
    bg_asset_id: Optional[str] = None

    # Связь с организацией
    organization_id: Optional[int]

    # Связь с пациентом
    patient_id: Optional[UUID]
    patient_full_name: Optional[str] = None
    patient_iin: Optional[str] = None
    patient_birth_date: Optional[datetime] = None
    patient_full_name_if_not_registered: Optional[str] = None

    # Данные о получении актива
    receive_date: datetime
    receive_time: time
    actual_datetime: datetime
    received_from: str
    is_repeat: bool

    # Данные о матери
    mother_data: Optional[MotherDataResponseSchema] = None

    # Данные о новорожденном
    newborn_data: Optional[NewbornDataResponseSchema] = None

    # Диагнозы
    diagnoses: List[NewbornDiagnosisResponseSchema] = Field(default_factory=list)

    # Примечание к диагнозу
    diagnosis_note: Optional[str] = None

    # Статусы
    status: AssetStatusEnum = AssetStatusEnum.REGISTERED
    delivery_status: AssetDeliveryStatusEnum = AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY

    # Флаги
    has_confirm: bool = False
    has_files: bool = False
    has_refusal: bool = False

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

    class Config:
        from_attributes = True
        extra = 'allow'


class NewbornAssetListItemSchema(BaseModel):
    """Схема для элемента списка активов новорожденных"""

    id: UUID  # ID актива

    organization_id: Optional[int]  # ID организации
    organization_name: Optional[str] = None  # Название организации

    patient_id: Optional[UUID]  # ID пациента
    patient_full_name: str  # ФИО пациента (новорожденного)
    patient_iin: Optional[str] = None  # ИИН пациента
    patient_birth_date: Optional[datetime] = None  # Дата рождения пациента

    mother_full_name: Optional[str] = None  # ФИО матери
    newborn_summary: str  # Краткие данные о новорожденном
    diagnoses_summary: str  # Сводка диагнозов

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

    class Config:
        from_attributes = True
        extra = 'allow'


class MultipleNewbornAssetsResponseSchema(BaseModel):
    """Схема ответа для списка активов новорожденных"""

    items: List[NewbornAssetListItemSchema]
    pagination: PaginationMetaDataSchema


class NewbornAssetDetailResponseSchema(BaseModel):
    """Схема ответа для детального просмотра актива новорожденного"""

    item: NewbornAssetResponseSchema


class NewbornAssetStatisticsSchema(BaseModel):
    """Схема статистики активов новорожденных"""

    total_assets: int
    confirmed_assets: int
    refused_assets: int
    pending_assets: int
    assets_with_files: int

    # Статистика по состоянию новорожденных
    excellent_condition_count: int = 0
    good_condition_count: int = 0
    satisfactory_condition_count: int = 0
    severe_condition_count: int = 0
    critical_condition_count: int = 0

    # Статистика по типу родов
    natural_delivery_count: int = 0
    cesarean_delivery_count: int = 0
    forceps_delivery_count: int = 0
    vacuum_delivery_count: int = 0


class NewbornAssetsByOrganizationResponseSchema(BaseModel):
    """Схема ответа для активов новорожденных по организации"""

    organization_id: int
    organization_name: str
    organization_code: str
    total_assets: int
    items: List[NewbornAssetListItemSchema]
    pagination: PaginationMetaDataSchema


class PatientNewbornAssetsResponseSchema(BaseModel):
    """Схема ответа для активов новорожденных пациента"""

    patient_id: UUID
    patient_full_name: str
    patient_iin: Optional[str]
    total_assets: int
    items: List[NewbornAssetListItemSchema]
    pagination: PaginationMetaDataSchema