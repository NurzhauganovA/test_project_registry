from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    SickLeaveStatusEnum,
    SickLeaveReasonEnum,
    WorkCapacityEnum,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class SickLeaveResponseSchema(BaseModel):
    """Схема ответа для больничного листа"""

    # Основные поля
    id: UUID

    # Связь с организацией
    organization_id: Optional[int]

    # Связь с пациентом
    patient_id: UUID
    patient_full_name: Optional[str] = None
    patient_iin: Optional[str] = None
    patient_birth_date: Optional[datetime] = None

    # Адрес проживания пациента
    patient_location_address: Optional[str] = None

    # Данные о получении
    receive_date: datetime
    receive_time: time
    actual_datetime: datetime
    received_from: str
    is_repeat: bool

    # Наименование места работы
    workplace_name: Optional[str] = None

    # Период нетрудоспособности
    disability_start_date: date
    disability_end_date: Optional[date] = None

    # Медицинские данные
    status: SickLeaveStatusEnum
    sick_leave_reason: Optional[SickLeaveReasonEnum] = None
    work_capacity: WorkCapacityEnum

    # Участок и специалист
    area: str
    specialization: str
    specialist: str

    # Дополнительная информация
    notes: Optional[str] = None
    is_primary: bool = True
    parent_sick_leave_id: Optional[UUID] = None

    # Вычисляемые поля
    duration_days: Optional[int] = None
    is_active: bool = False
    is_expired: bool = False

    # Метаданные
    created_at: datetime
    updated_at: datetime

    # Связанные данные
    organization_data: Optional[Dict[str, Any]] = None
    patient_data: Optional[Dict[str, Any]] = None

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            SickLeaveStatusEnum.OPEN: "Открыт",
            SickLeaveStatusEnum.CLOSED: "Закрыт",
            SickLeaveStatusEnum.CANCELLED: "Отменен",
            SickLeaveStatusEnum.EXTENSION: "Продление",
        }
        return status_map.get(self.status, "Неизвестно")

    class Config:
        from_attributes = True
        extra = 'allow'


class SickLeaveListItemSchema(BaseModel):
    """Схема для элемента списка больничных листов"""

    id: UUID

    organization_id: Optional[int] = None
    organization_name: Optional[str] = None

    patient_id: UUID
    patient_full_name: str
    patient_iin: str
    patient_birth_date: datetime

    disability_start_date: date
    disability_end_date: Optional[date] = None

    specialist: str
    specialization: str
    area: str

    status: SickLeaveStatusEnum
    duration_days: Optional[int] = None

    created_at: datetime
    updated_at: datetime

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            SickLeaveStatusEnum.OPEN: "Открыт",
            SickLeaveStatusEnum.CLOSED: "Закрыт",
            SickLeaveStatusEnum.CANCELLED: "Отменен",
            SickLeaveStatusEnum.EXTENSION: "Продление",
        }
        return status_map.get(self.status, "Неизвестно")

    class Config:
        from_attributes = True
        extra = 'allow'


class MultipleSickLeavesResponseSchema(BaseModel):
    """Схема ответа для списка больничных листов"""

    items: List[SickLeaveListItemSchema]
    pagination: PaginationMetaDataSchema


class SickLeaveDetailResponseSchema(BaseModel):
    """Схема ответа для детального просмотра больничного листа"""

    item: SickLeaveResponseSchema


class SickLeaveStatisticsSchema(BaseModel):
    """Схема статистики больничных листов"""

    total_sick_leaves: int
    open_sick_leaves: int
    closed_sick_leaves: int
    cancelled_sick_leaves: int
    extended_sick_leaves: int

    # Статистика по причинам
    acute_illness_count: int = 0
    chronic_illness_count: int = 0
    work_injury_count: int = 0
    domestic_injury_count: int = 0
    pregnancy_complications_count: int = 0
    child_care_count: int = 0
    family_member_care_count: int = 0

    # Средняя продолжительность
    average_duration_days: Optional[float] = None


class PatientSickLeavesResponseSchema(BaseModel):
    """Схема ответа для больничных листов пациента"""

    patient_id: UUID
    patient_full_name: str
    patient_iin: str
    total_sick_leaves: int
    active_sick_leaves: int
    items: List[SickLeaveListItemSchema]
    pagination: PaginationMetaDataSchema


class SickLeaveExtensionsResponseSchema(BaseModel):
    """Схема ответа для продлений больничного листа"""

    parent_sick_leave_id: UUID
    extensions: List[SickLeaveResponseSchema]
    total_extensions: int


class SickLeavesByOrganizationResponseSchema(BaseModel):
    """Схема ответа для больничных листов по организации"""

    organization_id: int
    organization_name: str
    organization_code: str
    total_sick_leaves: int
    items: List[SickLeaveListItemSchema]
    pagination: PaginationMetaDataSchema