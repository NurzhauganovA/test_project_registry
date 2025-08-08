from datetime import datetime, date, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    SickLeaveStatusEnum,
    SickLeaveReasonEnum,
    WorkCapacityEnum,
)


class CreateSickLeaveSchema(BaseModel):
    """Схема для создания больничного листа"""

    # Связь с пациентом
    patient_iin: str = Field(..., description="ИИН пациента")

    # Адрес проживания пациента
    patient_location_address: Optional[str] = Field(default=None, description="Адрес проживания пациента")

    # Данные о получении
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Наименование места работы
    workplace_name: Optional[str] = Field(default=None, description="Наименование места работы")

    # Период нетрудоспособности
    disability_start_date: date = Field(..., description="Начало нетрудоспособности")
    disability_end_date: Optional[date] = Field(default=None, description="Окончание нетрудоспособности")

    # Медицинские данные
    sick_leave_reason: Optional[SickLeaveReasonEnum] = Field(default=None, description="Причина выдачи больничного листа")
    work_capacity: WorkCapacityEnum = Field(default=WorkCapacityEnum.TEMPORARILY_DISABLED, description="Трудоспособность")

    # Участок и специалист
    area: str = Field(..., description="Участок")
    specialization: str = Field(..., description="Специализация")
    specialist: str = Field(..., description="Специалист")

    # Дополнительная информация
    notes: Optional[str] = Field(default=None, description="Примечания")
    is_primary: bool = Field(default=True, description="Первичный или продление")
    parent_sick_leave_id: Optional[UUID] = Field(default=None, description="ID родительского больничного листа")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_iin": "030611550511",
                "patient_location_address": "г. Астана, ул. Абая 150",
                "receive_date": "2025-03-22T10:55:00",
                "receive_time": "10:55:00",
                "actual_datetime": "2025-03-22T10:55:00",
                "received_from": "Поликлиника №1",
                "is_repeat": False,
                "workplace_name": "ТОО 'Астана Энерго'",
                "disability_start_date": "2025-03-22",
                "disability_end_date": "2025-03-29",
                "sick_leave_reason": "acute_illness",
                "work_capacity": "temporarily_disabled",
                "area": "Терапевтический",
                "specialization": "Терапевт",
                "specialist": "Михайлов Александр Евгеньевич",
                "notes": "Рекомендован постельный режим",
                "is_primary": True
            }
        }


class UpdateSickLeaveSchema(BaseModel):
    """Схема для обновления больничного листа"""

    # Адрес проживания пациента
    patient_location_address: Optional[str] = Field(default=None, description="Адрес проживания пациента")

    # Данные о получении
    receive_date: Optional[datetime] = Field(default=None, description="Дата получения")
    receive_time: Optional[time] = Field(default=None, description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: Optional[str] = Field(default=None, description="Получено от")
    is_repeat: Optional[bool] = Field(default=None, description="Повторный")

    # Наименование места работы
    workplace_name: Optional[str] = Field(default=None, description="Наименование места работы")

    # Период нетрудоспособности
    disability_start_date: Optional[date] = Field(default=None, description="Начало нетрудоспособности")
    disability_end_date: Optional[date] = Field(default=None, description="Окончание нетрудоспособности")

    # Медицинские данные
    sick_leave_reason: Optional[SickLeaveReasonEnum] = Field(default=None, description="Причина выдачи больничного листа")
    work_capacity: Optional[WorkCapacityEnum] = Field(default=None, description="Трудоспособность")

    # Участок и специалист
    area: Optional[str] = Field(default=None, description="Участок")
    specialization: Optional[str] = Field(default=None, description="Специализация")
    specialist: Optional[str] = Field(default=None, description="Специалист")

    # Дополнительная информация
    notes: Optional[str] = Field(default=None, description="Примечания")

    # Статус
    status: Optional[SickLeaveStatusEnum] = Field(default=None, description="Статус больничного листа")


class CreateSickLeaveByPatientIdSchema(BaseModel):
    """Схема для создания больничного листа по ID пациента"""

    # Связь с пациентом
    patient_id: UUID = Field(..., description="ID существующего пациента")

    # Адрес проживания пациента
    patient_location_address: Optional[str] = Field(default=None, description="Адрес проживания пациента")

    # Данные о получении
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Наименование места работы
    workplace_name: Optional[str] = Field(default=None, description="Наименование места работы")

    # Период нетрудоспособности
    disability_start_date: date = Field(..., description="Начало нетрудоспособности")
    disability_end_date: Optional[date] = Field(default=None, description="Окончание нетрудоспособности")

    # Медицинские данные
    sick_leave_reason: Optional[SickLeaveReasonEnum] = Field(default=None, description="Причина выдачи больничного листа")
    work_capacity: WorkCapacityEnum = Field(default=WorkCapacityEnum.TEMPORARILY_DISABLED, description="Трудоспособность")

    # Участок и специалист
    area: str = Field(..., description="Участок")
    specialization: str = Field(..., description="Специализация")
    specialist: str = Field(..., description="Специалист")

    # Дополнительная информация
    notes: Optional[str] = Field(default=None, description="Примечания")
    is_primary: bool = Field(default=True, description="Первичный или продление")
    parent_sick_leave_id: Optional[UUID] = Field(default=None, description="ID родительского больничного листа")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "43524a25-869c-4564-afcc-ddb27b8752f0",
                "patient_location_address": "г. Астана, ул. Абая 150",
                "receive_date": "2025-03-22T10:55:00",
                "receive_time": "10:55:00",
                "actual_datetime": "2025-03-22T10:55:00",
                "received_from": "Поликлиника №1",
                "is_repeat": False,
                "workplace_name": "ТОО 'Астана Энерго'",
                "disability_start_date": "2025-03-22",
                "disability_end_date": "2025-03-29",
                "sick_leave_reason": "acute_illness",
                "work_capacity": "temporarily_disabled",
                "area": "Терапевтический",
                "specialization": "Терапевт",
                "specialist": "Михайлов Александр Евгеньевич",
                "notes": "Рекомендован постельный режим",
                "is_primary": True
            }
        }


class CloseSickLeaveSchema(BaseModel):
    """Схема для закрытия больничного листа"""

    disability_end_date: date = Field(..., description="Дата окончания нетрудоспособности")
    notes: Optional[str] = Field(default=None, description="Дополнительные примечания")

    class Config:
        json_schema_extra = {
            "example": {
                "disability_end_date": "2025-03-29",
                "notes": "Пациент выздоровел, возвращается к работе"
            }
        }


class ExtendSickLeaveSchema(BaseModel):
    """Схема для продления больничного листа"""

    new_end_date: date = Field(..., description="Новая дата окончания нетрудоспособности")
    reason: Optional[str] = Field(default=None, description="Причина продления")

    class Config:
        json_schema_extra = {
            "example": {
                "new_end_date": "2025-04-05",
                "reason": "Осложнения заболевания"
            }
        }


class SickLeaveFilterParams:
    """Параметры фильтрации больничных листов"""

    def __init__(
            self,
            # Поиск по пациенту
            patient_search: Optional[str] = None,
            patient_id: Optional[UUID] = None,
            patient_iin: Optional[str] = None,

            # Период по дате получения
            receive_date_from: Optional[datetime] = None,
            receive_date_to: Optional[datetime] = None,

            # Период нетрудоспособности
            disability_start_date_from: Optional[date] = None,
            disability_start_date_to: Optional[date] = None,

            # Статус
            status: Optional[SickLeaveStatusEnum] = None,

            # Причина
            sick_leave_reason: Optional[SickLeaveReasonEnum] = None,

            # Врач
            specialist: Optional[str] = None,
            specialization: Optional[str] = None,

            # Участок
            area: Optional[str] = None,

            # Место работы
            workplace_name: Optional[str] = None,

            # Только первичные или продления
            is_primary: Optional[bool] = None,

            # Активные больничные листы
            is_active: Optional[bool] = None,

            # ID организации (может быть передан вручную для фильтрации)
            organization_id: Optional[int] = None,
    ):
        self.patient_search = patient_search
        self.patient_id = patient_id
        self.patient_iin = patient_iin
        self.receive_date_from = receive_date_from
        self.receive_date_to = receive_date_to
        self.disability_start_date_from = disability_start_date_from
        self.disability_start_date_to = disability_start_date_to
        self.status = status
        self.sick_leave_reason = sick_leave_reason
        self.specialist = specialist
        self.specialization = specialization
        self.area = area
        self.workplace_name = workplace_name
        self.is_primary = is_primary
        self.is_active = is_active
        self.organization_id = organization_id

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }