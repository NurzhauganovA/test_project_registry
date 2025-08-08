from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from src.apps.assets_journal.domain.enums import (
    StaffAssignmentStatusEnum,
    MedicalSpecializationEnum,
    MedicalDepartmentEnum,
    AreaTypeEnum,
)


class CreateStaffAssignmentSchema(BaseModel):
    """Схема для создания назначения медперсонала"""

    # Данные специалиста
    specialist_name: str = Field(..., description="ФИО специалиста")
    specialization: MedicalSpecializationEnum = Field(..., description="Специализация")

    # Назначение
    area_number: str = Field(..., description="Номер участка")
    area_type: AreaTypeEnum = Field(..., description="Тип участка")
    department: MedicalDepartmentEnum = Field(..., description="Отделение")

    # Период работы
    start_date: date = Field(..., description="Дата начала")
    end_date: Optional[date] = Field(default=None, description="Дата окончания")

    # Время работы
    reception_hours_per_day: int = Field(default=0, ge=0, le=23, description="Часов на приёме в день")
    reception_minutes_per_day: int = Field(default=0, ge=0, le=59, description="Минут на приёме в день")
    area_hours_per_day: int = Field(default=0, ge=0, le=23, description="Часов на участке в день")
    area_minutes_per_day: int = Field(default=0, ge=0, le=59, description="Минут на участке в день")

    # Дополнительная информация
    notes: Optional[str] = Field(default=None, description="Примечания")

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('Дата окончания не может быть раньше даты начала')
        return v

    @validator('specialist_name')
    def validate_specialist_name(cls, v):
        if not v or not v.strip():
            raise ValueError('ФИО специалиста обязательно для заполнения')
        return v.strip()

    @validator('area_number')
    def validate_area_number(cls, v):
        if not v or not v.strip():
            raise ValueError('Номер участка обязателен для заполнения')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "specialist_name": "Михайлов Александр Евгеньевич",
                "specialization": "therapist",
                "area_number": "14",
                "area_type": "therapeutic",
                "department": "therapeutic",
                "start_date": "2025-03-01",
                "end_date": "2025-04-30",
                "reception_hours_per_day": 4,
                "reception_minutes_per_day": 30,
                "area_hours_per_day": 3,
                "area_minutes_per_day": 0,
                "notes": "Временное назначение на период отпуска основного врача"
            }
        }


class UpdateStaffAssignmentSchema(BaseModel):
    """Схема для обновления назначения медперсонала"""

    # Данные специалиста
    specialist_name: Optional[str] = Field(default=None, description="ФИО специалиста")
    specialization: Optional[MedicalSpecializationEnum] = Field(default=None, description="Специализация")

    # Назначение
    area_number: Optional[str] = Field(default=None, description="Номер участка")
    area_type: Optional[AreaTypeEnum] = Field(default=None, description="Тип участка")
    department: Optional[MedicalDepartmentEnum] = Field(default=None, description="Отделение")

    # Период работы
    start_date: Optional[date] = Field(default=None, description="Дата начала")
    end_date: Optional[date] = Field(default=None, description="Дата окончания")

    # Время работы
    reception_hours_per_day: Optional[int] = Field(default=None, ge=0, le=23, description="Часов на приёме в день")
    reception_minutes_per_day: Optional[int] = Field(default=None, ge=0, le=59, description="Минут на приёме в день")
    area_hours_per_day: Optional[int] = Field(default=None, ge=0, le=23, description="Часов на участке в день")
    area_minutes_per_day: Optional[int] = Field(default=None, ge=0, le=59, description="Минут на участке в день")

    # Статус и примечания
    status: Optional[StaffAssignmentStatusEnum] = Field(default=None, description="Статус назначения")
    notes: Optional[str] = Field(default=None, description="Примечания")

    @validator('specialist_name')
    def validate_specialist_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('ФИО специалиста не может быть пустым')
        return v.strip() if v else v

    @validator('area_number')
    def validate_area_number(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Номер участка не может быть пустым')
        return v.strip() if v else v


class CompleteStaffAssignmentSchema(BaseModel):
    """Схема для завершения назначения медперсонала"""

    end_date: date = Field(..., description="Дата окончания назначения")
    notes: Optional[str] = Field(default=None, description="Примечания к завершению")

    class Config:
        json_schema_extra = {
            "example": {
                "end_date": "2025-04-30",
                "notes": "Назначение завершено в связи с окончанием контракта"
            }
        }


class ExtendStaffAssignmentSchema(BaseModel):
    """Схема для продления назначения медперсонала"""

    new_end_date: date = Field(..., description="Новая дата окончания")
    reason: Optional[str] = Field(default=None, description="Причина продления")

    class Config:
        json_schema_extra = {
            "example": {
                "new_end_date": "2025-06-30",
                "reason": "Продление в связи с нехваткой персонала"
            }
        }


class StaffAssignmentFilterParams:
    """Параметры фильтрации назначений медперсонала"""

    def __init__(
            self,
            # Поиск по специалисту
            specialist_search: Optional[str] = None,

            # Период назначения
            start_date_from: Optional[date] = None,
            start_date_to: Optional[date] = None,
            end_date_from: Optional[date] = None,
            end_date_to: Optional[date] = None,

            # Специализация и отделение
            specialization: Optional[MedicalSpecializationEnum] = None,
            department: Optional[MedicalDepartmentEnum] = None,

            # Участок
            area_number: Optional[str] = None,
            area_type: Optional[AreaTypeEnum] = None,

            # Статус
            status: Optional[StaffAssignmentStatusEnum] = None,

            # Только активные назначения
            only_active: Optional[bool] = None,

            # Только текущие назначения (активные на сегодня)
            only_current: Optional[bool] = None,
    ):
        self.specialist_search = specialist_search
        self.start_date_from = start_date_from
        self.start_date_to = start_date_to
        self.end_date_from = end_date_from
        self.end_date_to = end_date_to
        self.specialization = specialization
        self.department = department
        self.area_number = area_number
        self.area_type = area_type
        self.status = status
        self.only_active = only_active
        self.only_current = only_current

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }