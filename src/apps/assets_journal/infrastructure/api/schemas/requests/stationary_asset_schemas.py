from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)


class CreateStationaryAssetSchema(BaseModel):
    """Схема для создания актива стационара"""

    # Данные из BG
    bg_asset_id: Optional[str] = Field(default=None, description="ID из BG системы")
    card_number: str = Field(..., description="Номер стационарной карты пациента")

    # Связь с пациентом
    patient_iin: str = Field(..., description="ИИН пациента")

    # Данные о получении актива
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Данные пребывания в стационаре
    stay_period_start: datetime = Field(..., description="В стационаре находился с")
    stay_period_end: Optional[datetime] = Field(default=None, description="до")
    stay_outcome: Optional[str] = Field(default=None, description="Исход пребывания")
    diagnosis: str = Field(..., description="Диагноз")

    # Участок и специалист
    area: str = Field(..., description="Участок")
    specialization: Optional[str] = Field(default=None, description="Специализация")
    specialist: str = Field(..., description="Специалист")

    # Примечание
    note: Optional[str] = Field(default=None, description="Примечание")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671309",
                "card_number": "123456789012",
                "patient_iin": "030611550511",
                "receive_date": "2025-03-22T10:55:00",
                "receive_time": "10:55:00",
                "actual_datetime": "2025-03-22T10:55:00",
                "received_from": "Поликлиника №1",
                "is_repeat": False,
                "stay_period_start": "2025-03-20T08:00:00",
                "stay_period_end": "2025-03-25T14:00:00",
                "stay_outcome": "Выздоровление",
                "diagnosis": "J06.9 Острая инфекция верхних дыхательных путей неуточненная",
                "area": "Педиатрический",
                "specialization": "Педиатрия",
                "specialist": "Малышева А.О.",
                "note": "Пациент направлен для дальнейшего наблюдения"
            }
        }


class UpdateStationaryAssetSchema(BaseModel):
    """Схема для обновления актива стационара"""

    # Данные о получении актива
    receive_date: Optional[datetime] = Field(default=None, description="Дата получения")
    receive_time: Optional[time] = Field(default=None, description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: Optional[str] = Field(default=None, description="Получено от")
    is_repeat: Optional[bool] = Field(default=None, description="Повторный")

    # Данные пребывания в стационаре
    stay_period_start: Optional[datetime] = Field(default=None, description="В стационаре находился с")
    stay_period_end: Optional[datetime] = Field(default=None, description="до")
    stay_outcome: Optional[str] = Field(default=None, description="Исход пребывания")
    diagnosis: Optional[str] = Field(default=None, description="Диагноз")

    # Участок и специалист
    area: Optional[str] = Field(default=None, description="Участок")
    specialization: Optional[str] = Field(default=None, description="Специализация")
    specialist: Optional[str] = Field(default=None, description="Специалист")

    # Примечание
    note: Optional[str] = Field(default=None, description="Примечание")

    # Статусы (для внутреннего использования)
    status: Optional[AssetStatusEnum] = Field(default=None, description="Статус актива")
    delivery_status: Optional[AssetDeliveryStatusEnum] = Field(default=None, description="Статус доставки")


class CreateStationaryAssetByPatientIdSchema(BaseModel):
    """Схема для создания актива стационара по ID пациента"""

    # Данные из BG
    bg_asset_id: Optional[str] = Field(default=None, description="ID из BG системы")
    card_number: Optional[str] = Field(default=None, description="Номер стационарной карты пациента")

    # Связь с пациентом
    patient_id: UUID = Field(..., description="ID существующего пациента")

    # Данные о получении актива
    receive_date: datetime = Field(..., description="Дата получения")
    receive_time: time = Field(..., description="Время получения")
    actual_datetime: Optional[datetime] = Field(default=None, description="Фактическая дата и время")
    received_from: str = Field(..., description="Получено от")
    is_repeat: bool = Field(default=False, description="Повторный")

    # Данные пребывания в стационаре
    stay_period_start: datetime = Field(..., description="В стационаре находился с")
    stay_period_end: Optional[datetime] = Field(default=None, description="до")
    stay_outcome: Optional[str] = Field(default=None, description="Исход пребывания")
    diagnosis: str = Field(..., description="Диагноз")

    # Участок и специалист
    area: str = Field(..., description="Участок")
    specialization: Optional[str] = Field(default=None, description="Специализация")
    specialist: str = Field(..., description="Специалист")

    # Примечание
    note: Optional[str] = Field(default=None, description="Примечание")

    class Config:
        json_schema_extra = {
            "example": {
                "bg_asset_id": "6800000006671309",
                "card_number": "123456789012",
                "patient_id": "43524a25-869c-4564-afcc-ddb27b8752f0",
                "receive_date": "2025-03-22T10:55:00",
                "receive_time": "10:55:00",
                "actual_datetime": "2025-03-22T10:55:00",
                "received_from": "Поликлиника №1",
                "is_repeat": False,
                "stay_period_start": "2025-03-20T08:00:00",
                "stay_period_end": "2025-03-25T14:00:00",
                "stay_outcome": "Выздоровление",
                "diagnosis": "J06.9 Острая инфекция верхних дыхательных путей неуточненная",
                "area": "Педиатрический",
                "specialization": "Педиатрия",
                "specialist": "Малышева А.О.",
                "note": "Пациент направлен для дальнейшего наблюдения"
            }
        }


class TransferStationaryAssetSchema(BaseModel):
    """Схема для передачи актива стационара другой организации"""

    new_organization_id: int = Field(..., description="ID новой организации")
    transfer_reason: Optional[str] = Field(default=None, description="Причина передачи")
    update_patient_attachment: bool = Field(
        default=True,
        description="Обновить attachment_data пациента с новой организацией"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "new_organization_id": 1,
                "transfer_reason": "Перенаправление в специализированное отделение",
                "update_patient_attachment": True
            }
        }