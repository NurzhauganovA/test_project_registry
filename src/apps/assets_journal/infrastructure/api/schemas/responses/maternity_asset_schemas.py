from datetime import datetime, time
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum, MaternityDiagnosisTypeEnum, MaternityOutcomeEnum, MaternityAdmissionTypeEnum,
    MaternityStayTypeEnum, MaternityStatusEnum,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class MaternityDiagnosisResponseSchema(BaseModel):
    """Схема ответа для диагноза роддома"""

    diagnosis_type: str
    diagnosis_code: str
    diagnosis_name: str
    note: Optional[str] = None

    class Config:
        from_attributes = True


class MaternityAssetResponseSchema(BaseModel):
    """Схема ответа для актива роддома"""

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

    # Данные о пребывании в роддоме
    stay_period_start: datetime
    stay_period_end: Optional[datetime] = None
    stay_outcome: Optional[str] = None
    admission_type: Optional[str] = None
    stay_type: Optional[str] = None
    patient_status: Optional[str] = None

    # Диагнозы
    diagnoses: List[MaternityDiagnosisResponseSchema] = Field(default_factory=list)

    # Участок и специалист
    area: str
    specialization: Optional[str] = None
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


class MaternityAssetListItemSchema(BaseModel):
    """Схема для элемента списка активов роддома"""

    id: UUID  # ID актива

    organization_id: Optional[int]  # ID организации
    organization_name: Optional[str] = None  # Название организации

    patient_id: UUID  # ID пациента
    patient_full_name: str  # ФИО пациента
    patient_iin: str  # ИИН пациента
    patient_birth_date: datetime  # Дата рождения пациента

    area: str  # Участок
    specialization: Optional[str] = None  # Специализация
    specialist: str  # Специалист
    stay_type: Optional[str] = None  # Тип пребывания
    patient_status: Optional[str] = None  # Статус пациентки
    diagnoses_summary: str  # Сводка диагнозов

    status: AssetStatusEnum  # Статус актива
    delivery_status: AssetDeliveryStatusEnum  # Статус доставки
    receive_date: datetime  # Дата получения
    receive_time: time  # Время получения
    stay_period_start: datetime  # Начало пребывания
    stay_period_end: Optional[datetime] = None  # Окончание пребывания

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

    def _get_stay_type_display(self) -> str:
        """Получить отображаемое название типа пребывания"""
        if not self.stay_type:
            return "Не указан"

        type_map = {
            MaternityStayTypeEnum.DELIVERY: "Роды",
            MaternityStayTypeEnum.GYNECOLOGY: "Гинекология",
            MaternityStayTypeEnum.PATHOLOGY: "Патология беременности",
            MaternityStayTypeEnum.OBSERVATION: "Наблюдение",
        }
        return type_map.get(self.stay_type, "Не указан")

    def _get_patient_status_display(self) -> str:
        """Получить отображаемое название статуса пациентки"""
        if not self.patient_status:
            return "Не указан"

        status_map = {
            MaternityStatusEnum.PREGNANT: "Беременная",
            MaternityStatusEnum.IN_LABOR: "В родах",
            MaternityStatusEnum.POSTPARTUM: "Послеродовая",
            MaternityStatusEnum.GYNECOLOGICAL: "Гинекологическая",
        }
        return status_map.get(self.patient_status, "Не указан")

    class Config:
        from_attributes = True
        extra = 'allow'


class MultipleMaternityAssetsResponseSchema(BaseModel):
    """Схема ответа для списка активов роддома"""

    items: List[MaternityAssetListItemSchema]
    pagination: PaginationMetaDataSchema


class MaternityAssetDetailResponseSchema(BaseModel):
    """Схема ответа для детального просмотра актива роддома"""

    item: MaternityAssetResponseSchema


class MaternityAssetsByOrganizationResponseSchema(BaseModel):
    """Схема ответа для активов роддома по организации"""

    organization_id: int
    organization_name: str
    organization_code: str
    total_assets: int
    items: List[MaternityAssetListItemSchema]
    pagination: PaginationMetaDataSchema


class PatientMaternityAssetsResponseSchema(BaseModel):
    """Схема ответа для активов роддома пациента"""

    patient_id: UUID
    patient_full_name: str
    patient_iin: str
    total_assets: int
    items: List[MaternityAssetListItemSchema]
    pagination: PaginationMetaDataSchema