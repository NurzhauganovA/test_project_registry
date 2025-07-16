from datetime import datetime, time
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
    EmergencyOutcomeEnum,
    DiagnosisTypeEnum,
)


class EmergencyDiagnosisSchema(BaseModel):
    """Схема диагноза для скорой помощи"""

    diagnosis_type: DiagnosisTypeEnum = Field(..., description="Тип диагноза")
    diagnosis_code: str = Field(..., description="Код диагноза")
    diagnosis_name: str = Field(..., description="Название диагноза")
    note: Optional[str] = Field(default=None, description="Примечание к диагнозу")

    class Config:
        json_schema_extra = {
            "example": {
                "diagnosis_type": "primary",
                "diagnosis_code": "J06.9",
                "diagnosis_name": "Острая инфекция верхних дыхательных путей неуточненная",
                "note": "Дополнительная информация"
            }
        }


class CreateEmergencyAssetSchema(BaseModel):
    """Схема для создания актива скорой помощи"""

    # Данные из BG
    bg_asset_id: Optional[str] = Field(default=None, description="ID из BG системы")

    # Связь с пациентом
    patient_iin: str = Field(..., description="ИИН пациента")

    # Данные о местонахождении пациента
    patient_location_address: Optional[str] = Field(default=None, description="Адрес местонахождения пациента")
    is_not_attached_to_mo: bool = Field(default=False, description="Не прикреплен к МО")

    # Данные о получении актива
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Исход обращения
    outcome: Optional[EmergencyOutcomeEnum] = Field(default=None, description="Исход обращения")

    # Диагнозы
    diagnoses: List[EmergencyDiagnosisSchema] = Field(default_factory=list, description="Список диагнозов")

    # Примечание к диагнозу
    diagnosis_note: Optional[str] = Field(default=None, description="Примечание к диагнозу")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671310",
                "patient_iin": "030611550511",
                "patient_location_address": "г. Астана, ул. Абая 150",
                "is_not_attached_to_mo": False,
                "receive_date": "2025-03-22T10:55:00",
                "receive_time": "10:55:00",
                "actual_datetime": "2025-03-22T10:55:00",
                "received_from": "Служба скорой помощи №3",
                "is_repeat": False,
                "outcome": "hospitalized",
                "diagnoses": [
                    {
                        "diagnosis_type": "primary",
                        "diagnosis_code": "J06.9",
                        "diagnosis_name": "Острая инфекция верхних дыхательных путей неуточненная",
                        "note": None
                    }
                ],
                "diagnosis_note": "Пациент направлен в стационар для дальнейшего лечения"
            }
        }


class UpdateEmergencyAssetSchema(BaseModel):
    """Схема для обновления актива скорой помощи"""

    # Данные о местонахождении пациента
    patient_location_address: Optional[str] = Field(default=None, description="Адрес местонахождения пациента")
    is_not_attached_to_mo: Optional[bool] = Field(default=None, description="Не прикреплен к МО")

    # Данные о получении актива
    receive_date: Optional[datetime] = Field(default=None, description="Дата получения")
    receive_time: Optional[time] = Field(default=None, description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: Optional[str] = Field(default=None, description="Получено от")
    is_repeat: Optional[bool] = Field(default=None, description="Повторный")

    # Исход обращения
    outcome: Optional[EmergencyOutcomeEnum] = Field(default=None, description="Исход обращения")

    # Диагнозы
    diagnoses: Optional[List[EmergencyDiagnosisSchema]] = Field(default=None, description="Список диагнозов")

    # Примечание к диагнозу
    diagnosis_note: Optional[str] = Field(default=None, description="Примечание к диагнозу")

    # Статусы (для внутреннего использования)
    status: Optional[AssetStatusEnum] = Field(default=None, description="Статус актива")
    delivery_status: Optional[AssetDeliveryStatusEnum] = Field(default=None, description="Статус доставки")


class CreateEmergencyAssetByPatientIdSchema(BaseModel):
    """Схема для создания актива скорой помощи по ID пациента"""

    # Данные из BG
    bg_asset_id: Optional[str] = Field(default=None, description="ID из BG системы")

    # Связь с пациентом
    patient_id: UUID = Field(..., description="ID существующего пациента")

    # Данные о местонахождении пациента
    patient_location_address: Optional[str] = Field(default=None, description="Адрес местонахождения пациента")
    is_not_attached_to_mo: bool = Field(default=False, description="Не прикреплен к МО")

    # Данные о получении актива
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Исход обращения
    outcome: Optional[EmergencyOutcomeEnum] = Field(default=None, description="Исход обращения")

    # Диагнозы
    diagnoses: List[EmergencyDiagnosisSchema] = Field(default_factory=list, description="Список диагнозов")

    # Примечание к диагнозу
    diagnosis_note: Optional[str] = Field(default=None, description="Примечание к диагнозу")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671310",
                "patient_id": "43524a25-869c-4564-afcc-ddb27b8752f0",
                "patient_location_address": "г. Астана, ул. Абая 150",
                "is_not_attached_to_mo": False,
                "receive_date": "2025-03-22T10:55:00",
                "receive_time": "10:55:00",
                "actual_datetime": "2025-03-22T10:55:00",
                "received_from": "Служба скорой помощи №3",
                "is_repeat": False,
                "outcome": "hospitalized",
                "diagnoses": [
                    {
                        "diagnosis_type": "primary",
                        "diagnosis_code": "J06.9",
                        "diagnosis_name": "Острая инфекция верхних дыхательных путей неуточненная",
                        "note": None
                    }
                ],
                "diagnosis_note": "Пациент направлен в стационар для дальнейшего лечения"
            }
        }


class EmergencyAssetFilterParams:
    """Параметры фильтрации активов скорой помощи"""

    def __init__(
            self,
            organization_id: Optional[int] = None,

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

            # Исход обращения
            outcome: Optional[EmergencyOutcomeEnum] = None,

            # Диагноз
            diagnosis_code: Optional[str] = None,
    ):
        self.organization_id = organization_id
        self.patient_search = patient_search
        self.patient_id = patient_id
        self.patient_iin = patient_iin
        self.date_from = date_from
        self.date_to = date_to
        self.status = status
        self.delivery_status = delivery_status
        self.outcome = outcome
        self.diagnosis_code = diagnosis_code

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }