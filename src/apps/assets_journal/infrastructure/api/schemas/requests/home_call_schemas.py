from datetime import datetime, time
from typing import Optional
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


class CreateHomeCallSchema(BaseModel):
    """Схема для создания вызова на дом"""

    # Связь с пациентом
    patient_iin: str = Field(..., description="ИИН пациента")

    # Адрес и телефон пациента
    patient_address: Optional[str] = Field(default=None, description="Адрес пациента")
    patient_phone: Optional[str] = Field(default=None, description="Телефон пациента")

    # Данные о регистрации вызова
    registration_date: datetime = Field(..., description="Дата регистрации")
    registration_time: time = Field(..., description="Время регистрации")
    registration_datetime: Optional[datetime] = Field(default=None, description="Объединенная дата-время регистрации")

    # Исполнение вызова
    execution_date: Optional[datetime] = Field(default=None, description="Дата выполнения")
    execution_time: Optional[time] = Field(default=None, description="Время выполнения")

    # Медицинские данные
    area: str = Field(..., description="Участок")
    specialization: str = Field(..., description="Специализация")
    specialist: str = Field(..., description="Специалист")

    # Страхование
    is_insured: bool = Field(default=False, description="Застрахован")
    has_oms: bool = Field(default=False, description="ОСМС")

    # Данные о вызове
    source: HomeCallSourceEnum = Field(..., description="Источник вызова")
    category: HomeCallCategoryEnum = Field(..., description="Категория вызова")
    reason: HomeCallReasonEnum = Field(..., description="Повод вызова")
    call_type: HomeCallTypeEnum = Field(..., description="Тип вызова")
    reason_patient_words: Optional[str] = Field(default=None, description="Повод вызова (со слов пациента)")
    visit_type: HomeCallVisitTypeEnum = Field(default=HomeCallVisitTypeEnum.PRIMARY, description="Вид посещения")

    # Примечания
    notes: Optional[str] = Field(default=None, description="Примечания")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_iin": "030611550511",
                "patient_address": "г. Астана, ул. Абая 150, кв. 25",
                "patient_phone": "+7 (777) 123-45-67",
                "registration_date": "2025-03-22T10:55:00",
                "registration_time": "10:55:00",
                "registration_datetime": "2025-03-22T10:55:00",
                "execution_date": "2025-03-22T14:30:00",
                "execution_time": "14:30:00",
                "area": "Терапевтический",
                "specialization": "Терапевт",
                "specialist": "Михайлов Александр Евгеньевич",
                "is_insured": True,
                "has_oms": True,
                "source": "egov",
                "category": "urgent",
                "reason": "illness",
                "call_type": "therapeutic",
                "reason_patient_words": "Высокая температура, слабость",
                "visit_type": "primary",
                "notes": "Пациент просит прийти во второй половине дня"
            }
        }


class CreateHomeCallByPatientIdSchema(BaseModel):
    """Схема для создания вызова на дом по ID пациента"""

    # Связь с пациентом
    patient_id: UUID = Field(..., description="ID существующего пациента")

    # Адрес и телефон пациента
    patient_address: Optional[str] = Field(default=None, description="Адрес пациента")
    patient_phone: Optional[str] = Field(default=None, description="Телефон пациента")

    # Данные о регистрации вызова
    registration_date: datetime = Field(..., description="Дата регистрации")
    registration_time: time = Field(..., description="Время регистрации")
    registration_datetime: Optional[datetime] = Field(default=None, description="Объединенная дата-время регистрации")

    # Исполнение вызова
    execution_date: Optional[datetime] = Field(default=None, description="Дата выполнения")
    execution_time: Optional[time] = Field(default=None, description="Время выполнения")

    # Медицинские данные
    area: str = Field(..., description="Участок")
    specialization: str = Field(..., description="Специализация")
    specialist: str = Field(..., description="Специалист")

    # Страхование
    is_insured: bool = Field(default=False, description="Застрахован")
    has_oms: bool = Field(default=False, description="ОСМС")

    # Данные о вызове
    source: HomeCallSourceEnum = Field(..., description="Источник вызова")
    category: HomeCallCategoryEnum = Field(..., description="Категория вызова")
    reason: HomeCallReasonEnum = Field(..., description="Повод вызова")
    call_type: HomeCallTypeEnum = Field(..., description="Тип вызова")
    reason_patient_words: Optional[str] = Field(default=None, description="Повод вызова (со слов пациента)")
    visit_type: HomeCallVisitTypeEnum = Field(default=HomeCallVisitTypeEnum.PRIMARY, description="Вид посещения")

    # Примечания
    notes: Optional[str] = Field(default=None, description="Примечания")


class UpdateHomeCallSchema(BaseModel):
    """Схема для обновления вызова на дом"""

    # Адрес и телефон пациента
    patient_address: Optional[str] = Field(default=None, description="Адрес пациента")
    patient_phone: Optional[str] = Field(default=None, description="Телефон пациента")

    # Данные о регистрации вызова
    registration_date: Optional[datetime] = Field(default=None, description="Дата регистрации")
    registration_time: Optional[time] = Field(default=None, description="Время регистрации")
    registration_datetime: Optional[datetime] = Field(default=None, description="Объединенная дата-время регистрации")

    # Исполнение вызова
    execution_date: Optional[datetime] = Field(default=None, description="Дата выполнения")
    execution_time: Optional[time] = Field(default=None, description="Время выполнения")

    # Медицинские данные
    area: Optional[str] = Field(default=None, description="Участок")
    specialization: Optional[str] = Field(default=None, description="Специализация")
    specialist: Optional[str] = Field(default=None, description="Специалист")

    # Страхование
    is_insured: Optional[bool] = Field(default=None, description="Застрахован")
    has_oms: Optional[bool] = Field(default=None, description="ОСМС")

    # Данные о вызове
    source: Optional[HomeCallSourceEnum] = Field(default=None, description="Источник вызова")
    category: Optional[HomeCallCategoryEnum] = Field(default=None, description="Категория вызова")
    reason: Optional[HomeCallReasonEnum] = Field(default=None, description="Повод вызова")
    call_type: Optional[HomeCallTypeEnum] = Field(default=None, description="Тип вызова")
    reason_patient_words: Optional[str] = Field(default=None, description="Повод вызова (со слов пациента)")
    visit_type: Optional[HomeCallVisitTypeEnum] = Field(default=None, description="Вид посещения")

    # Статус и примечания
    status: Optional[HomeCallStatusEnum] = Field(default=None, description="Статус вызова")
    notes: Optional[str] = Field(default=None, description="Примечания")


class CompleteHomeCallSchema(BaseModel):
    """Схема для завершения вызова на дом"""

    execution_date: datetime = Field(..., description="Дата выполнения")
    execution_time: time = Field(..., description="Время выполнения")
    notes: Optional[str] = Field(default=None, description="Примечания к выполнению")

    class Config:
        json_schema_extra = {
            "example": {
                "execution_date": "2025-03-22T14:30:00",
                "execution_time": "14:30:00",
                "notes": "Вызов выполнен, пациент осмотрен, рекомендации даны"
            }
        }


class HomeCallFilterParams:
    """Параметры фильтрации вызовов на дом"""

    def __init__(
            self,
            # Поиск по пациенту
            patient_search: Optional[str] = None,
            patient_id: Optional[UUID] = None,
            patient_iin: Optional[str] = None,

            # Период по дате регистрации
            registration_date_from: Optional[datetime] = None,
            registration_date_to: Optional[datetime] = None,

            # Период по дате выполнения
            execution_date_from: Optional[datetime] = None,
            execution_date_to: Optional[datetime] = None,

            # Статус и категория
            status: Optional[HomeCallStatusEnum] = None,
            category: Optional[HomeCallCategoryEnum] = None,

            # Источник и тип
            source: Optional[HomeCallSourceEnum] = None,
            call_type: Optional[HomeCallTypeEnum] = None,

            # Врач
            specialist: Optional[str] = None,
            specialization: Optional[str] = None,

            # Участок
            area: Optional[str] = None,

            # Только активные вызовы
            is_active: Optional[bool] = None,

            # ID организации
            organization_id: Optional[int] = None,

            # Номер вызова
            call_number: Optional[str] = None,
    ):
        self.patient_search = patient_search
        self.patient_id = patient_id
        self.patient_iin = patient_iin
        self.registration_date_from = registration_date_from
        self.registration_date_to = registration_date_to
        self.execution_date_from = execution_date_from
        self.execution_date_to = execution_date_to
        self.status = status
        self.category = category
        self.source = source
        self.call_type = call_type
        self.specialist = specialist
        self.specialization = specialization
        self.area = area
        self.is_active = is_active
        self.organization_id = organization_id
        self.call_number = call_number

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }