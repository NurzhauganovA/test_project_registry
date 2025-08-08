from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    StaffAssignmentStatusEnum,
    MedicalSpecializationEnum,
    MedicalDepartmentEnum,
    AreaTypeEnum,
)
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class StaffAssignmentResponseSchema(BaseModel):
    """Схема ответа для назначения медперсонала"""

    # Основные поля
    id: UUID

    # Данные специалиста
    specialist_name: str
    specialization: MedicalSpecializationEnum

    # Назначение
    area_number: str
    area_type: AreaTypeEnum
    department: MedicalDepartmentEnum

    # Период работы
    start_date: date
    end_date: Optional[date] = None

    # Время работы
    reception_hours_per_day: int
    reception_minutes_per_day: int
    area_hours_per_day: int
    area_minutes_per_day: int

    # Вычисляемые поля времени
    reception_time_formatted: str
    area_time_formatted: str
    total_work_minutes_per_day: int

    # Статус
    status: StaffAssignmentStatusEnum

    # Дополнительная информация
    notes: Optional[str] = None

    # Вычисляемые поля
    is_active: bool = False
    is_current: bool = False
    days_assigned: Optional[int] = None

    # Метаданные
    created_at: datetime
    updated_at: datetime

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            StaffAssignmentStatusEnum.ACTIVE: "Активен",
            StaffAssignmentStatusEnum.INACTIVE: "Неактивен",
            StaffAssignmentStatusEnum.SUSPENDED: "Приостановлен",
            StaffAssignmentStatusEnum.COMPLETED: "Завершен",
        }
        return status_map.get(self.status, "Неизвестно")

    def _get_specialization_display(self) -> str:
        """Получить отображаемое название специализации"""
        specialization_map = {
            MedicalSpecializationEnum.THERAPIST: "Терапевт",
            MedicalSpecializationEnum.PEDIATRICIAN: "Педиатр",
            MedicalSpecializationEnum.CARDIOLOGIST: "Кардиолог",
            MedicalSpecializationEnum.NEUROLOGIST: "Невролог",
            MedicalSpecializationEnum.SURGEON: "Хирург",
            MedicalSpecializationEnum.GYNECOLOGIST: "Гинеколог",
            MedicalSpecializationEnum.UROLOGIST: "Уролог",
            MedicalSpecializationEnum.DERMATOLOGIST: "Дерматолог",
            MedicalSpecializationEnum.OPHTHALMOLOGIST: "Офтальмолог",
            MedicalSpecializationEnum.OTOLARYNGOLOGIST: "ЛОР",
            MedicalSpecializationEnum.PSYCHIATRIST: "Психиатр",
            MedicalSpecializationEnum.PSYCHOLOGIST: "Психолог",
            MedicalSpecializationEnum.PSYCHOTHERAPIST: "Психотерапевт",
            MedicalSpecializationEnum.GENERAL_PRACTITIONER: "Врач общей практики",
            MedicalSpecializationEnum.NURSE: "Медсестра",
            MedicalSpecializationEnum.PARAMEDIC: "Фельдшер",
        }
        return specialization_map.get(self.specialization, "Неизвестно")

    def _get_department_display(self) -> str:
        """Получить отображаемое название отделения"""
        department_map = {
            MedicalDepartmentEnum.THERAPEUTIC: "Терапевтическое",
            MedicalDepartmentEnum.PEDIATRIC: "Педиатрическое",
            MedicalDepartmentEnum.SURGICAL: "Хирургическое",
            MedicalDepartmentEnum.GYNECOLOGICAL: "Гинекологическое",
            MedicalDepartmentEnum.NEUROLOGICAL: "Неврологическое",
            MedicalDepartmentEnum.CARDIOLOGICAL: "Кардиологическое",
            MedicalDepartmentEnum.PSYCHIATRIC: "Психиатрическое",
            MedicalDepartmentEnum.DERMATOLOGICAL: "Дерматологическое",
            MedicalDepartmentEnum.OPHTHALMOLOGICAL: "Офтальмологическое",
            MedicalDepartmentEnum.OTOLARYNGOLOGICAL: "ЛОР",
            MedicalDepartmentEnum.EMERGENCY: "Скорая помощь",
            MedicalDepartmentEnum.OUTPATIENT: "Поликлиническое",
            MedicalDepartmentEnum.GENERAL_PRACTICE: "Общая практика",
        }
        return department_map.get(self.department, "Неизвестно")

    class Config:
        from_attributes = True
        extra = 'allow'


class StaffAssignmentListItemSchema(BaseModel):
    """Схема для элемента списка назначений медперсонала"""

    id: UUID
    specialist_name: str
    specialization: MedicalSpecializationEnum
    area_number: str
    department: MedicalDepartmentEnum
    start_date: date
    end_date: Optional[date] = None
    status: StaffAssignmentStatusEnum
    reception_time_formatted: str
    area_time_formatted: str
    created_at: datetime
    updated_at: datetime

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            StaffAssignmentStatusEnum.ACTIVE: "Активен",
            StaffAssignmentStatusEnum.INACTIVE: "Неактивен",
            StaffAssignmentStatusEnum.SUSPENDED: "Приостановлен",
            StaffAssignmentStatusEnum.COMPLETED: "Завершен",
        }
        return status_map.get(self.status, "Неизвестно")

    def _get_specialization_display(self) -> str:
        """Получить отображаемое название специализации"""
        specialization_map = {
            MedicalSpecializationEnum.THERAPIST: "Терапевт",
            MedicalSpecializationEnum.PEDIATRICIAN: "Педиатр",
            MedicalSpecializationEnum.CARDIOLOGIST: "Кардиолог",
            MedicalSpecializationEnum.NEUROLOGIST: "Невролог",
            MedicalSpecializationEnum.SURGEON: "Хирург",
            MedicalSpecializationEnum.GYNECOLOGIST: "Гинеколог",
            MedicalSpecializationEnum.UROLOGIST: "Уролог",
            MedicalSpecializationEnum.DERMATOLOGIST: "Дерматолог",
            MedicalSpecializationEnum.OPHTHALMOLOGIST: "Офтальмолог",
            MedicalSpecializationEnum.OTOLARYNGOLOGIST: "ЛОР",
            MedicalSpecializationEnum.PSYCHIATRIST: "Психиатр",
            MedicalSpecializationEnum.PSYCHOLOGIST: "Психолог",
            MedicalSpecializationEnum.PSYCHOTHERAPIST: "Психотерапевт",
            MedicalSpecializationEnum.GENERAL_PRACTITIONER: "Врач общей практики",
            MedicalSpecializationEnum.NURSE: "Медсестра",
            MedicalSpecializationEnum.PARAMEDIC: "Фельдшер",
        }
        return specialization_map.get(self.specialization, "Неизвестно")

    class Config:
        from_attributes = True
        extra = 'allow'


class MultipleStaffAssignmentsResponseSchema(BaseModel):
    """Схема ответа для списка назначений медперсонала"""

    items: List[StaffAssignmentListItemSchema]
    pagination: PaginationMetaDataSchema


class StaffAssignmentDetailResponseSchema(BaseModel):
    """Схема ответа для детального просмотра назначения медперсонала"""

    item: StaffAssignmentResponseSchema


class StaffAssignmentStatisticsSchema(BaseModel):
    """Схема статистики назначений медперсонала"""

    total_assignments: int
    active_assignments: int
    inactive_assignments: int
    suspended_assignments: int
    completed_assignments: int

    # Статистика по специализациям
    therapists_count: int = 0
    pediatricians_count: int = 0
    surgeons_count: int = 0
    cardiologists_count: int = 0
    neurologists_count: int = 0
    other_specialists_count: int = 0

    # Статистика по отделениям
    therapeutic_department_count: int = 0
    pediatric_department_count: int = 0
    surgical_department_count: int = 0
    other_departments_count: int = 0

    # Статистика по участкам
    total_areas_covered: int = 0
    therapeutic_areas_count: int = 0
    pediatric_areas_count: int = 0
    general_practice_areas_count: int = 0


class SpecialistAssignmentsResponseSchema(BaseModel):
    """Схема ответа для назначений конкретного специалиста"""

    specialist_name: str
    total_assignments: int
    active_assignments: int
    items: List[StaffAssignmentListItemSchema]
    pagination: PaginationMetaDataSchema


class AreaAssignmentsResponseSchema(BaseModel):
    """Схема ответа для назначений на конкретный участок"""

    area_number: str
    area_type: AreaTypeEnum
    total_assignments: int
    current_assignments: int
    items: List[StaffAssignmentListItemSchema]
    pagination: PaginationMetaDataSchema


class DepartmentAssignmentsResponseSchema(BaseModel):
    """Схема ответа для назначений по отделению"""

    department: MedicalDepartmentEnum
    department_name: str
    total_assignments: int
    active_assignments: int
    items: List[StaffAssignmentListItemSchema]
    pagination: PaginationMetaDataSchema