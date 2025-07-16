from datetime import datetime, time
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
    EmergencyOutcomeEnum,
    DiagnosisTypeEnum,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class EmergencyDiagnosisResponseSchema(BaseModel):
    """Схема ответа для диагноза скорой помощи"""

    diagnosis_type: DiagnosisTypeEnum
    diagnosis_code: str
    diagnosis_name: str
    note: Optional[str] = None

    class Config:
        from_attributes = True


class EmergencyAssetResponseSchema(BaseModel):
    """Схема ответа для актива скорой помощи"""

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

    # Данные о местонахождении пациента
    patient_location_address: Optional[str] = None
    is_not_attached_to_mo: bool = False

    # Данные о получении актива
    receive_date: datetime
    receive_time: time
    actual_datetime: datetime
    received_from: str
    is_repeat: bool

    # Исход обращения
    outcome: Optional[EmergencyOutcomeEnum] = None

    # Диагнозы
    diagnoses: List[EmergencyDiagnosisResponseSchema] = Field(default_factory=list)

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

    def _get_outcome_display(self) -> str:
        """Получить отображаемое название исхода"""
        outcome_map = {
            EmergencyOutcomeEnum.HOSPITALIZED: "Госпитализирован",
            EmergencyOutcomeEnum.TREATED_AT_HOME: "Лечение на дому",
            EmergencyOutcomeEnum.REFUSED_TREATMENT: "Отказ от лечения",
            EmergencyOutcomeEnum.DEATH: "Смерть",
            EmergencyOutcomeEnum.TRANSFERRED: "Передан другой службе",
        }
        return outcome_map.get(self.outcome, "Не указан") if self.outcome else "Не указан"

    class Config:
        from_attributes = True
        extra = 'allow'


class EmergencyAssetListItemSchema(BaseModel):
    """Схема для элемента списка активов скорой помощи"""

    id: UUID  # ID актива

    organization_id: Optional[int]  # ID организации
    organization_name: Optional[str] = None  # Название организации

    patient_id: UUID  # ID пациента
    patient_full_name: str  # ФИО пациента
    patient_iin: str  # ИИН пациента
    patient_birth_date: datetime  # Дата рождения пациента

    diagnoses_summary: str  # Сводка диагнозов
    outcome: Optional[EmergencyOutcomeEnum] = None  # Исход обращения

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

    def _get_outcome_display(self) -> str:
        """Получить отображаемое название исхода"""
        outcome_map = {
            EmergencyOutcomeEnum.HOSPITALIZED: "Госпитализирован",
            EmergencyOutcomeEnum.TREATED_AT_HOME: "Лечение на дому",
            EmergencyOutcomeEnum.REFUSED_TREATMENT: "Отказ от лечения",
            EmergencyOutcomeEnum.DEATH: "Смерть",
            EmergencyOutcomeEnum.TRANSFERRED: "Передан другой службе",
        }
        return outcome_map.get(self.outcome, "Не указан") if self.outcome else "Не указан"

    class Config:
        from_attributes = True
        extra = 'allow'


class MultipleEmergencyAssetsResponseSchema(BaseModel):
    """Схема ответа для списка активов скорой помощи"""

    items: List[EmergencyAssetListItemSchema]
    pagination: PaginationMetaDataSchema


class EmergencyAssetDetailResponseSchema(BaseModel):
    """Схема ответа для детального просмотра актива скорой помощи"""

    item: EmergencyAssetResponseSchema


class EmergencyAssetStatisticsSchema(BaseModel):
    """Схема статистики активов скорой помощи"""

    total_assets: int
    confirmed_assets: int
    refused_assets: int
    pending_assets: int
    assets_with_files: int

    # Статистика по исходам
    hospitalized_count: int = 0
    treated_at_home_count: int = 0
    refused_treatment_count: int = 0
    death_count: int = 0
    transferred_count: int = 0


class EmergencyAssetsByOrganizationResponseSchema(BaseModel):
    """Схема ответа для активов скорой помощи по организации"""

    organization_id: int
    organization_name: str
    organization_code: str
    total_assets: int
    items: List[EmergencyAssetListItemSchema]
    pagination: PaginationMetaDataSchema


class PatientEmergencyAssetsResponseSchema(BaseModel):
    """Схема ответа для активов скорой помощи пациента"""

    patient_id: UUID
    patient_full_name: str
    patient_iin: str
    total_assets: int
    items: List[EmergencyAssetListItemSchema]
    pagination: PaginationMetaDataSchema