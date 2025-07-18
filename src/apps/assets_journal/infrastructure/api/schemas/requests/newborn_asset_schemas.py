from datetime import datetime, time
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
    DiagnosisTypeEnum,
    DeliveryTypeEnum,
    PregnancyWeekEnum,
    NewbornConditionEnum,
    TransferDestinationEnum,
    MedicalServiceTypeEnum,
)


class NewbornDiagnosisSchema(BaseModel):
    """Схема диагноза для новорожденного"""

    diagnosis_type: DiagnosisTypeEnum = Field(..., description="Тип диагноза")
    diagnosis_code: str = Field(..., description="Код диагноза")
    diagnosis_name: str = Field(..., description="Название диагноза")
    note: Optional[str] = Field(default=None, description="Примечание к диагнозу")

    class Config:
        json_schema_extra = {
            "example": {
                "diagnosis_type": "primary",
                "diagnosis_code": "P07.3",
                "diagnosis_name": "Другие маловесные новорожденные",
                "note": "Дополнительная информация"
            }
        }


class MotherDataSchema(BaseModel):
    """Схема данных о матери"""

    iin: Optional[str] = Field(default=None, description="ИИН матери")
    full_name: Optional[str] = Field(default=None, description="ФИО матери")
    address: Optional[str] = Field(default=None, description="Адрес матери")
    birth_date: Optional[datetime] = Field(default=None, description="Дата родов")
    birth_time: Optional[time] = Field(default=None, description="Время родов")
    delivery_type: Optional[DeliveryTypeEnum] = Field(default=None, description="Вид родов")
    pregnancy_weeks: Optional[PregnancyWeekEnum] = Field(default=None, description="Срок беременности")
    discharge_date: Optional[datetime] = Field(default=None, description="Дата выписки матери")
    discharge_time: Optional[time] = Field(default=None, description="Время выписки матери")

    class Config:
        json_schema_extra = {
            "example": {
                "iin": "850315450234",
                "full_name": "Айгерим Серіккызы",
                "address": "г. Алматы, ул. Абая, 120",
                "birth_date": "2025-07-14T10:30:00",
                "birth_time": "10:30:00",
                "delivery_type": "natural",
                "pregnancy_weeks": "37-42",
                "discharge_date": "2025-07-17T12:00:00",
                "discharge_time": "12:00:00"
            }
        }


class NewbornDataSchema(BaseModel):
    """Схема данных о новорожденном"""

    birth_date: Optional[datetime] = Field(default=None, description="Дата выписки ребенка")
    birth_time: Optional[time] = Field(default=None, description="Время выписки ребенка")
    weight_grams: Optional[Decimal] = Field(default=None, description="Вес ребенка в граммах")
    height_cm: Optional[Decimal] = Field(default=None, description="Рост ребенка в см")
    transfer_destination: Optional[TransferDestinationEnum] = Field(default=None, description="Переведен в")
    condition: Optional[NewbornConditionEnum] = Field(default=None, description="Состояние новорожденного")
    medical_services: Optional[List[MedicalServiceTypeEnum]] = Field(default_factory=list,
                                                                     description="Медицинские услуги")

    class Config:
        json_schema_extra = {
            "example": {
                "birth_date": "2025-07-17T14:00:00",
                "birth_time": "14:00:00",
                "weight_grams": "3250",
                "height_cm": "52",
                "transfer_destination": "home",
                "condition": "good",
                "medical_services": ["pharmacy", "blood_test"]
            }
        }


class CreateNewbornAssetSchema(BaseModel):
    """Схема для создания актива новорожденного"""

    # Данные из BG
    bg_asset_id: Optional[str] = Field(default=None, description="ID из BG системы")

    # Связь с пациентом
    patient_full_name_if_not_registered: Optional[str] = Field(
        default=None,
        description="ФИО в случае отсутствии регистрации"
    )
    patient_iin: Optional[str] = Field(default=None, description="ИИН пациента")

    # Данные о получении актива
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Данные о матери
    mother_data: Optional[MotherDataSchema] = Field(default=None, description="Данные о матери")

    # Данные о новорожденном
    newborn_data: Optional[NewbornDataSchema] = Field(default=None, description="Данные о новорожденном")

    # Диагнозы
    diagnoses: List[NewbornDiagnosisSchema] = Field(default_factory=list, description="Список диагнозов")

    # Примечание к диагнозу
    diagnosis_note: Optional[str] = Field(default=None, description="Примечание к диагнозу")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671320",
                "patient_iin": "030611550511",
                "patient_full_name_if_not_registered": "Новорожденный Серіккызы",
                "receive_date": "2025-07-14T10:30:00",
                "receive_time": "10:30:00",
                "actual_datetime": "2025-07-14T10:30:00",
                "received_from": "Роддом №1",
                "is_repeat": False,
                "mother_data": {
                    "iin": "850315450234",
                    "full_name": "Айгерим Серіккызы",
                    "address": "г. Алматы, ул. Абая, 120",
                    "birth_date": "2025-07-14T10:30:00",
                    "birth_time": "10:30:00",
                    "delivery_type": "natural",
                    "pregnancy_weeks": "37-42"
                },
                "newborn_data": {
                    "birth_date": "2025-07-17T14:00:00",
                    "birth_time": "14:00:00",
                    "weight_grams": "3250",
                    "height_cm": "52",
                    "condition": "good"
                },
                "diagnoses": [
                    {
                        "diagnosis_type": "primary",
                        "diagnosis_code": "Z38.0",
                        "diagnosis_name": "Одноплодные роды в больнице",
                        "note": None
                    }
                ]
            }
        }


class UpdateNewbornAssetSchema(BaseModel):
    """Схема для обновления актива новорожденного"""

    # ФИО в случае отсутствии регистрации
    patient_full_name_if_not_registered: Optional[str] = Field(
        default=None,
        description="ФИО в случае отсутствии регистрации"
    )

    # Данные о получении актива
    receive_date: Optional[datetime] = Field(default=None, description="Дата получения")
    receive_time: Optional[time] = Field(default=None, description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: Optional[str] = Field(default=None, description="Получено от")
    is_repeat: Optional[bool] = Field(default=None, description="Повторный")

    # Данные о матери
    mother_data: Optional[MotherDataSchema] = Field(default=None, description="Данные о матери")

    # Данные о новорожденном
    newborn_data: Optional[NewbornDataSchema] = Field(default=None, description="Данные о новорожденном")

    # Диагнозы
    diagnoses: Optional[List[NewbornDiagnosisSchema]] = Field(default=None, description="Список диагнозов")

    # Примечание к диагнозу
    diagnosis_note: Optional[str] = Field(default=None, description="Примечание к диагнозу")

    # Статусы (для внутреннего использования)
    status: Optional[AssetStatusEnum] = Field(default=None, description="Статус актива")
    delivery_status: Optional[AssetDeliveryStatusEnum] = Field(default=None, description="Статус доставки")


class CreateNewbornAssetByPatientIdSchema(BaseModel):
    """Схема для создания актива новорожденного по ID пациента"""

    # Данные из BG
    bg_asset_id: Optional[str] = Field(default=None, description="ID из BG системы")

    # Связь с пациентом
    patient_id: UUID = Field(..., description="ID существующего пациента")

    # ФИО в случае отсутствии регистрации
    patient_full_name_if_not_registered: Optional[str] = Field(
        default=None,
        description="ФИО в случае отсутствии регистрации"
    )

    # Данные о получении актива
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Данные о матери
    mother_data: Optional[MotherDataSchema] = Field(default=None, description="Данные о матери")

    # Данные о новорожденном
    newborn_data: Optional[NewbornDataSchema] = Field(default=None, description="Данные о новорожденном")

    # Диагнозы
    diagnoses: List[NewbornDiagnosisSchema] = Field(default_factory=list, description="Список диагнозов")

    # Примечание к диагнозу
    diagnosis_note: Optional[str] = Field(default=None, description="Примечание к диагнозу")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671320",
                "patient_id": "43524a25-869c-4564-afcc-ddb27b8752f0",
                "patient_full_name_if_not_registered": "Новорожденный Серіккызы",
                "patient_iin": None,
                "receive_date": "2025-07-14T10:30:00",
                "receive_time": "10:30:00",
                "actual_datetime": "2025-07-14T10:30:00",
                "received_from": "Роддом №1",
                "is_repeat": False,
                "mother_data": {
                    "iin": "850315450234",
                    "full_name": "Айгерим Серіккызы",
                    "address": "г. Алматы, ул. Абая, 120",
                    "delivery_type": "natural",
                    "pregnancy_weeks": "37-42"
                },
                "newborn_data": {
                    "weight_grams": "3250",
                    "height_cm": "52",
                    "condition": "good"
                },
                "diagnoses": [
                    {
                        "diagnosis_type": "primary",
                        "diagnosis_code": "Z38.0",
                        "diagnosis_name": "Одноплодные роды в больнице"
                    }
                ]
            }
        }


class NewbornAssetFilterParams:
    """Параметры фильтрации активов новорожденных"""

    def __init__(
            self,
            organization_id: Optional[id] = None,

            # Поиск по пациенту
            patient_search: Optional[str] = None,
            patient_id: Optional[UUID] = None,
            patient_iin: Optional[str] = None,

            # Поиск по матери
            mother_search: Optional[str] = None,
            mother_iin: Optional[str] = None,

            # Период
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,

            # Статус актива
            status: Optional[AssetStatusEnum] = None,

            # Статус доставки
            delivery_status: Optional[AssetDeliveryStatusEnum] = None,

            # Состояние новорожденного
            newborn_condition: Optional[NewbornConditionEnum] = None,

            # Вид родов
            delivery_type: Optional[DeliveryTypeEnum] = None,

            # Диагноз
            diagnosis_code: Optional[str] = None,
    ):
        self.patient_search = patient_search
        self.patient_id = patient_id
        self.patient_iin = patient_iin
        self.mother_search = mother_search
        self.mother_iin = mother_iin
        self.date_from = date_from
        self.date_to = date_to
        self.status = status
        self.delivery_status = delivery_status
        self.newborn_condition = newborn_condition
        self.delivery_type = delivery_type
        self.diagnosis_code = diagnosis_code
        self.organization_id = organization_id

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }