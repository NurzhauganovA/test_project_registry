from datetime import datetime, time
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    HomeCallStatusEnum,
    HomeCallCategoryEnum,
    HomeCallSourceEnum,
    HomeCallReasonEnum,
    HomeCallTypeEnum,
    HomeCallVisitTypeEnum,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class HomeCallResponseSchema(BaseModel):
    """Схема ответа для вызова на дом"""

    # Основные поля
    id: UUID
    call_number: Optional[str] = None

    # Связь с организацией
    organization_id: Optional[int] = None

    # Связь с пациентом
    patient_id: UUID
    patient_full_name: Optional[str] = None
    patient_iin: Optional[str] = None
    patient_birth_date: Optional[datetime] = None

    # Адрес и телефон пациента
    patient_address: Optional[str] = None
    patient_phone: Optional[str] = None

    # Данные о регистрации вызова
    registration_date: datetime
    registration_time: time
    registration_datetime: datetime

    # Исполнение вызова
    execution_date: Optional[datetime] = None
    execution_time: Optional[time] = None

    # Медицинские данные
    area: str
    specialization: str
    specialist: str

    # Страхование
    is_insured: bool
    has_oms: bool

    # Данные о вызове
    source: HomeCallSourceEnum
    category: HomeCallCategoryEnum
    reason: HomeCallReasonEnum
    call_type: HomeCallTypeEnum
    reason_patient_words: Optional[str] = None
    visit_type: HomeCallVisitTypeEnum

    # Статус и примечания
    status: HomeCallStatusEnum
    notes: Optional[str] = None

    # Вычисляемые поля
    is_active: bool = False
    is_completed: bool = False

    # Метаданные
    created_at: datetime
    updated_at: datetime

    # Связанные данные
    organization_data: Optional[Dict[str, Any]] = None
    patient_data: Optional[Dict[str, Any]] = None

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            HomeCallStatusEnum.REGISTERED: "Зарегистрирован",
            HomeCallStatusEnum.IN_PROGRESS: "В работе",
            HomeCallStatusEnum.COMPLETED: "Выполнен",
            HomeCallStatusEnum.CANCELLED: "Отменен",
        }
        return status_map.get(self.status, "Неизвестно")

    def _get_category_display(self) -> str:
        """Получить отображаемое название категории"""
        category_map = {
            HomeCallCategoryEnum.EMERGENCY: "Экстренный",
            HomeCallCategoryEnum.URGENT: "Срочный",
            HomeCallCategoryEnum.PLANNED: "Плановый",
        }
        return category_map.get(self.category, "Неизвестно")

    class Config:
        from_attributes = True
        extra = 'allow'


class HomeCallListItemSchema(BaseModel):
    """Схема для элемента списка вызовов на дом"""

    id: UUID
    call_number: Optional[str] = None

    organization_id: Optional[int] = None
    organization_name: Optional[str] = None

    patient_id: UUID
    patient_full_name: str
    patient_iin: str
    patient_birth_date: datetime

    registration_date: datetime
    registration_time: time
    category: HomeCallCategoryEnum
    status: HomeCallStatusEnum
    source: HomeCallSourceEnum

    specialist: str
    specialization: str
    area: str

    created_at: datetime
    updated_at: datetime

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            HomeCallStatusEnum.REGISTERED: "Зарегистрирован",
            HomeCallStatusEnum.IN_PROGRESS: "В работе",
            HomeCallStatusEnum.COMPLETED: "Выполнен",
            HomeCallStatusEnum.CANCELLED: "Отменен",
        }
        return status_map.get(self.status, "Неизвестно")

    def _get_category_display(self) -> str:
        """Получить отображаемое название категории"""
        category_map = {
            HomeCallCategoryEnum.EMERGENCY: "Экстренный",
            HomeCallCategoryEnum.URGENT: "Срочный",
            HomeCallCategoryEnum.PLANNED: "Плановый",
        }
        return category_map.get(self.category, "Неизвестно")

    class Config:
        from_attributes = True
        extra = 'allow'


class MultipleHomeCallsResponseSchema(BaseModel):
    """Схема ответа для списка вызовов на дом"""

    items: List[HomeCallListItemSchema]
    pagination: PaginationMetaDataSchema


class HomeCallDetailResponseSchema(BaseModel):
    """Схема ответа для детального просмотра вызова на дом"""

    item: HomeCallResponseSchema


class HomeCallStatisticsSchema(BaseModel):
    """Схема статистики вызовов на дом"""

    total_calls: int
    registered_calls: int
    in_progress_calls: int
    completed_calls: int
    cancelled_calls: int

    # Статистика по категориям
    emergency_calls: int = 0
    urgent_calls: int = 0
    planned_calls: int = 0

    # Статистика по источникам
    patient_calls: int = 0
    relatives_calls: int = 0
    egov_calls: int = 0
    call_center_calls: int = 0
    other_source_calls: int = 0

    # Статистика по типам
    therapeutic_calls: int = 0
    pediatric_calls: int = 0
    specialist_calls: int = 0


class PatientHomeCallsResponseSchema(BaseModel):
    """Схема ответа для вызовов на дом пациента"""

    patient_id: UUID
    patient_full_name: str
    patient_iin: str
    total_calls: int
    active_calls: int
    items: List[HomeCallListItemSchema]
    pagination: PaginationMetaDataSchema


class HomeCallsByOrganizationResponseSchema(BaseModel):
    """Схема ответа для вызовов на дом по организации"""

    organization_id: int
    organization_name: str
    organization_code: str
    total_calls: int
    items: List[HomeCallListItemSchema]
    pagination: PaginationMetaDataSchema


class HomeCallsBySpecialistResponseSchema(BaseModel):
    """Схема ответа для вызовов на дом по специалисту"""

    specialist: str
    specialization: str
    area: str
    total_calls: int
    active_calls: int
    completed_calls: int
    items: List[HomeCallListItemSchema]
    pagination: PaginationMetaDataSchema