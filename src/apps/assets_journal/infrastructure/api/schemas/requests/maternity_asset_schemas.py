from datetime import datetime, time
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum, MaternityDiagnosisTypeEnum, MaternityOutcomeEnum, MaternityAdmissionTypeEnum,
    MaternityStayTypeEnum, MaternityStatusEnum,
)


class MaternityDiagnosisSchema(BaseModel):
    """Схема диагноза для роддома"""

    diagnosis_type: str = Field(..., description="Тип диагноза")
    diagnosis_code: str = Field(..., description="Код диагноза")
    diagnosis_name: str = Field(..., description="Название диагноза")
    note: Optional[str] = Field(default=None, description="Примечание к диагнозу")

    class Config:
        json_schema_extra = {
            "example": {
                "diagnosis_type": "primary",
                "diagnosis_code": "O80.0",
                "diagnosis_name": "Спонтанные роды в затылочном предлежании",
                "note": "Нормальные роды"
            }
        }


class CreateMaternityAssetSchema(BaseModel):
    """Схема для создания актива роддома"""

    # Данные из BG
    bg_asset_id: Optional[str] = Field(default=None, description="ID из BG системы")

    # Связь с пациентом
    patient_iin: str = Field(..., description="ИИН пациента")

    # Данные о получении актива
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Данные о пребывании в роддоме
    stay_period_start: datetime = Field(..., description="Начало пребывания")
    stay_period_end: Optional[datetime] = Field(default=None, description="Окончание пребывания")
    stay_outcome: Optional[str] = Field(default=None, description="Исход пребывания")
    admission_type: Optional[str] = Field(default=None, description="Тип госпитализации")
    stay_type: Optional[str] = Field(default=None, description="Тип пребывания")
    patient_status: Optional[str] = Field(default=None, description="Статус пациентки")

    # Диагнозы
    diagnoses: List[MaternityDiagnosisSchema] = Field(default_factory=list, description="Список диагнозов")

    # Участок и специалист
    area: str = Field(..., description="Участок")
    specialization: Optional[str] = Field(default=None, description="Специализация")
    specialist: str = Field(..., description="Специалист")

    # Примечание
    note: Optional[str] = Field(default=None, description="Примечание")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671320",
                "patient_iin": "850315450234",
                "receive_date": "2025-07-14T10:30:00",
                "receive_time": "10:30:00",
                "actual_datetime": "2025-07-14T10:30:00",
                "received_from": "Роддом №1",
                "is_repeat": False,
                "stay_period_start": "2025-07-14T10:30:00",
                "stay_period_end": None,
                "stay_outcome": None,
                "admission_type": "emergency",
                "stay_type": "delivery",
                "patient_status": "in_labor",
                "diagnoses": [
                    {
                        "diagnosis_type": "primary",
                        "diagnosis_code": "O80.0",
                        "diagnosis_name": "Спонтанные роды в затылочном предлежании",
                        "note": "Нормальные роды"
                    }
                ],
                "area": "Родильное отделение",
                "specialization": "Акушер-гинеколог",
                "specialist": "Иванова А.С.",
                "note": "Поступила с началом родовой деятельности"
            }
        }


class CreateMaternityAssetByPatientIdSchema(BaseModel):
    """Схема для создания актива роддома по ID пациента"""

    # Данные из BG
    bg_asset_id: Optional[str] = Field(default=None, description="ID из BG системы")

    # Связь с пациентом
    patient_id: UUID = Field(..., description="ID существующего пациента")

    # Данные о получении актива
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Данные о пребывании в роддоме
    stay_period_start: datetime = Field(..., description="Начало пребывания")
    stay_period_end: Optional[datetime] = Field(default=None, description="Окончание пребывания")
    stay_outcome: Optional[str] = Field(default=None, description="Исход пребывания")
    admission_type: Optional[str] = Field(default=None, description="Тип госпитализации")
    stay_type: Optional[str] = Field(default=None, description="Тип пребывания")
    patient_status: Optional[str] = Field(default=None, description="Статус пациентки")

    # Диагнозы
    diagnoses: List[MaternityDiagnosisSchema] = Field(default_factory=list, description="Список диагнозов")

    # Участок и специалист
    area: str = Field(..., description="Участок")
    specialization: Optional[str] = Field(default=None, description="Специализация")
    specialist: str = Field(..., description="Специалист")

    # Примечание
    note: Optional[str] = Field(default=None, description="Примечание")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671320",
                "patient_id": "43524a25-869c-4564-afcc-ddb27b8752f0",
                "receive_date": "2025-07-14T10:30:00",
                "receive_time": "10:30:00",
                "actual_datetime": "2025-07-14T10:30:00",
                "received_from": "Роддом №1",
                "is_repeat": False,
                "stay_period_start": "2025-07-14T10:30:00",
                "admission_type": "emergency",
                "stay_type": "delivery",
                "patient_status": "in_labor",
                "diagnoses": [
                    {
                        "diagnosis_type": "primary",
                        "diagnosis_code": "O80.0",
                        "diagnosis_name": "Спонтанные роды в затылочном предлежании"
                    }
                ],
                "area": "Родильное отделение",
                "specialization": "Акушер-гинеколог",
                "specialist": "Иванова А.С.",
                "note": "Поступила с началом родовой деятельности"
            }
        }


class UpdateMaternityAssetSchema(BaseModel):
    """Схема для обновления актива роддома"""

    # Данные о получении актива
    receive_date: Optional[datetime] = Field(default=None, description="Дата получения")
    receive_time: Optional[time] = Field(default=None, description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: Optional[str] = Field(default=None, description="Получено от")
    is_repeat: Optional[bool] = Field(default=None, description="Повторный")

    # Данные о пребывании в роддоме
    stay_period_start: Optional[datetime] = Field(default=None, description="Начало пребывания")
    stay_period_end: Optional[datetime] = Field(default=None, description="Окончание пребывания")
    stay_outcome: Optional[str] = Field(default=None, description="Исход пребывания")
    admission_type: Optional[str] = Field(default=None, description="Тип госпитализации")
    stay_type: Optional[str] = Field(default=None, description="Тип пребывания")
    patient_status: Optional[str] = Field(default=None, description="Статус пациентки")

    # Диагнозы
    diagnoses: Optional[List[MaternityDiagnosisSchema]] = Field(default=None, description="Список диагнозов")

    # Участок и специалист
    area: Optional[str] = Field(default=None, description="Участок")
    specialization: Optional[str] = Field(default=None, description="Специализация")
    specialist: Optional[str] = Field(default=None, description="Специалист")

    # Примечание
    note: Optional[str] = Field(default=None, description="Примечание")

    # Статусы (для внутреннего использования)
    status: Optional[AssetStatusEnum] = Field(default=None, description="Статус актива")
    delivery_status: Optional[AssetDeliveryStatusEnum] = Field(default=None, description="Статус доставки")


class MaternityAssetFilterParams:
    """Параметры фильтрации активов роддома"""

    def __init__(
            self,
            # Поиск по пациенту
            patient_search: Optional[str] = None,
            patient_id: Optional[UUID] = None,
            patient_iin: Optional[str] = None,

            # Период
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,

            # Статус актива
            status: Optional[AssetStatusEnum] = None,

            # Статус доставки
            delivery_status: Optional[AssetDeliveryStatusEnum] = None,

            # Медицинские данные
            stay_outcome: Optional[MaternityOutcomeEnum] = None,
            admission_type: Optional[MaternityAdmissionTypeEnum] = None,
            stay_type: Optional[MaternityStayTypeEnum] = None,
            patient_status: Optional[MaternityStatusEnum] = None,

            # Участок и специализация
            area: Optional[str] = None,
            specialization: Optional[str] = None,
            specialist: Optional[str] = None,

            # Диагноз
            diagnosis_code: Optional[str] = None,

            # ID организации (может быть передан вручную для фильтрации)
            organization_id: Optional[int] = None,
    ):
        self.patient_search = patient_search
        self.patient_id = patient_id
        self.patient_iin = patient_iin
        self.date_from = date_from
        self.date_to = date_to
        self.status = status
        self.delivery_status = delivery_status
        self.stay_outcome = stay_outcome
        self.admission_type = admission_type
        self.stay_type = stay_type
        self.patient_status = patient_status
        self.area = area
        self.specialization = specialization
        self.specialist = specialist
        self.diagnosis_code = diagnosis_code
        self.organization_id = organization_id

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = {}
        for key, value in vars(self).items():
            if not exclude_none or value is not None:
                # Преобразуем enum в его значение
                if hasattr(value, 'value'):
                    data[key] = value.value
                else:
                    data[key] = value
        return data