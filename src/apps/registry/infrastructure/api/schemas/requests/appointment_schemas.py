from datetime import time as time_from_library
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.apps.registry.domain.enums import (
    AppointmentReferralOriginTypeEnum,
    AppointmentReferralTypeEnum,
    AppointmentStatusEnum,
    AppointmentTypeEnum,
)
from src.apps.registry.infrastructure.api.schemas.appointment_schemas import (
    AdditionalServiceSchema,
)


class CreateAppointmentSchema(BaseModel):
    time: time_from_library
    patient_id: Optional[UUID] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    status: AppointmentStatusEnum
    type: AppointmentTypeEnum
    financing_sources_ids: Optional[List[int]] = None
    referral_type: AppointmentReferralTypeEnum
    referral_origin: AppointmentReferralOriginTypeEnum
    reason: Optional[str] = None
    additional_services: Optional[List[AdditionalServiceSchema]] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "time": "08:00:00",
                "patient_id": "ad92cfe1-dea6-4362-a2ce-8cea40e42cfd",
                "phone_number": "77083531318",
                "address": None,
                "status": "appointment",
                "type": "consultation",
                "financing_sources_ids": [1],
                "referral_type": "with_referral",
                "referral_origin": "from_external_organization",
                "reason": "Плановый осмотр",
                "additional_services": [
                    {"name": "Услуга №1", "financing_source_id": 1, "price": 0},
                    {"name": "Услуга №2", "financing_source_id": 1, "price": 0},
                ],
            }
        }
    )


class UpdateAppointmentSchema(BaseModel):
    schedule_day_id: Optional[UUID] = None
    time: Optional[time_from_library] = None
    patient_id: Optional[UUID] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    status: Optional[AppointmentStatusEnum] = None
    type: Optional[AppointmentTypeEnum] = None
    financing_sources_ids: Optional[List[int]] = None
    referral_type: Optional[AppointmentReferralTypeEnum] = None
    referral_origin: Optional[AppointmentReferralOriginTypeEnum] = None
    reason: Optional[str] = None
    additional_services: Optional[List[AdditionalServiceSchema]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "schedule_day_id": "bd32cfe1-dea6-4362-a2ce-8cea40e42cdc",
                "time": "08:00:00",
                "patient_id": "ad92cfe1-dea6-4362-a2ce-8cea40e42cfd",
                "phone_number": None,
                "address": "Ул. Пушкина, дом Калатушкина 53",
                "status": "booked",
                "type": "consultation",
                "financing_sources_ids": [],
                "referral_type": "with_referral",
                "referral_origin": "from_external_organization",
                "reason": "Плановый осмотр",
                "additional_services": [
                    {"name": "Услуга №1", "financing_source_id": 1, "price": 0},
                    {"name": "Услуга №2", "financing_source_id": 1, "price": 0},
                ],
            }
        }
    )
