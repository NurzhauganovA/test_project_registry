from datetime import time as time_from_library
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.apps.registry.domain.enums import (
    AppointmentInsuranceType,
    AppointmentPatientTypeEnum,
    AppointmentReferralOriginTypeEnum,
    AppointmentReferralTypeEnum,
    AppointmentStatusEnum,
    AppointmentTypeEnum,
)


class CreateAppointmentSchema(BaseModel):
    time: time_from_library
    patient_id: Optional[UUID] = None
    type: AppointmentTypeEnum
    insurance_type: AppointmentInsuranceType
    patient_type: AppointmentPatientTypeEnum
    referral_type: AppointmentReferralTypeEnum
    referral_origin: AppointmentReferralOriginTypeEnum
    reason: Optional[str] = None
    additional_services: Optional[Dict[str, bool]] = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "time": "08:00:00",
                "patient_id": "ad92cfe1-dea6-4362-a2ce-8cea40e42cfd",
                "status": "booked",
                "type": "consultation",
                "insurance_type": "OSMS",
                "patient_type": "adult",
                "referral_type": "with_referral",
                "referral_origin": "from_external_organization",
                "reason": "Плановый осмотр",
                "additional_services": {"service_1": True, "service_2": False},
            }
        }
    )


class UpdateAppointmentSchema(BaseModel):
    schedule_day_id: Optional[UUID] = None
    time: Optional[time_from_library] = None
    patient_id: Optional[UUID] = None
    status: Optional[AppointmentStatusEnum] = None
    type: Optional[AppointmentTypeEnum] = None
    insurance_type: Optional[AppointmentInsuranceType] = None
    patient_type: Optional[AppointmentPatientTypeEnum] = None
    referral_type: Optional[AppointmentReferralTypeEnum] = None
    referral_origin: Optional[AppointmentReferralOriginTypeEnum] = None
    reason: Optional[str] = None
    additional_services: Optional[Dict[str, bool]] = None

    @model_validator(mode="before")
    @classmethod
    def remove_empty_additional_services(cls, data: Any) -> Any:
        if isinstance(data, dict) and data.get("additional_services") == {}:
            data.pop("additional_services")
        return data

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "schedule_day_id": "bd32cfe1-dea6-4362-a2ce-8cea40e42cdc",
                "time": "08:00:00",
                "patient_id": "ad92cfe1-dea6-4362-a2ce-8cea40e42cfd",
                "status": "booked",
                "type": "consultation",
                "insurance_type": "OSMS",
                "patient_type": "adult",
                "referral_type": "with_referral",
                "referral_origin": "from_external_organization",
                "reason": "Плановый осмотр",
                "additional_services": {"service_1": True, "service_2": False},
            }
        }
    )
