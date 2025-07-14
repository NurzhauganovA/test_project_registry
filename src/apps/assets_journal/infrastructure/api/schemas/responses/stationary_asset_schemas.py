from datetime import datetime, time
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, computed_field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class StationaryAssetResponseSchema(BaseModel):
    """Схема ответа для актива стационара"""

    # Основные поля
    id: UUID
    bg_asset_id: Optional[str] = None
    card_number: Optional[str] = None

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

    # Данные пребывания в стационаре
    stay_period_start: datetime
    stay_period_end: Optional[datetime] = None
    stay_outcome: Optional[str] = None
    diagnosis: str

    # Участок и специалист
    area: str
    specialist: str

    # Примечание
    note: Optional[str] = None

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


class StationaryAssetListItemSchema(BaseModel):
    """Схема для элемента списка активов стационара"""

    id: UUID  # ID актива
    card_number: str  # Номер стационара

    organization_id: Optional[int]  # ID организации
    organization_name: Optional[str] = None  # Название организации

    patient_id: UUID  #ID пациента
    patient_full_name: str  # ФИО пациента
    patient_iin: str  # ИИН пациента
    patient_birth_date: datetime  # Дата рождения пациента
    specialization: Optional[str] = None  # Специализация
    specialist: str  # Специалист
    area: str  # Участок
    diagnosis: str  # Диагноз
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


class MultipleStationaryAssetsResponseSchema(BaseModel):
    """Схема ответа для списка активов стационара"""

    items: List[StationaryAssetListItemSchema]
    pagination: PaginationMetaDataSchema


class StationaryAssetDetailResponseSchema(BaseModel):
    """Схема ответа для детального просмотра актива стационара"""

    item: StationaryAssetResponseSchema


class StationaryAssetStatisticsSchema(BaseModel):
    """Схема статистики активов стационара"""

    total_assets: int
    confirmed_assets: int
    refused_assets: int
    pending_assets: int
    assets_with_files: int


class StationaryAssetsByOrganizationResponseSchema(BaseModel):
    """Схема ответа для активов по организации"""

    organization_id: int
    organization_name: str
    organization_code: str
    total_assets: int
    items: List[StationaryAssetListItemSchema]
    pagination: PaginationMetaDataSchema


class PatientStationaryAssetsResponseSchema(BaseModel):
    """Схема ответа для активов пациента"""

    patient_id: UUID
    patient_full_name: str
    patient_iin: str
    total_assets: int
    items: List[StationaryAssetListItemSchema]
    pagination: PaginationMetaDataSchema