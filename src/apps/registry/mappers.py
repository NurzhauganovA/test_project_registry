from datetime import date, time
from decimal import Decimal
from typing import Optional
from uuid import UUID

from src.apps.patients.infrastructure.api.schemas.responses.patient_response_schemas import (
    ResponsePatientSchema,
)
from src.apps.registry.domain.models.appointment import AppointmentDomain
from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.infrastructure.api.schemas.requests.appointment_schemas import (
    AdditionalServiceSchema,
    CreateAppointmentSchema,
    UpdateAppointmentSchema,
)
from src.apps.registry.infrastructure.api.schemas.responses.appointment_schemas import (
    ResponseAppointmentSchema,
)
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    ResponseScheduleDaySchema,
)
from src.apps.registry.infrastructure.db_models.models import (
    Appointment,
    Schedule,
    ScheduleDay,
)
from src.apps.users.infrastructure.schemas.user_schemas import UserSchema


def map_appointment_create_schema_to_domain(
    schema: CreateAppointmentSchema,
    schedule_day_id: UUID,
) -> AppointmentDomain:
    return AppointmentDomain(
        schedule_day_id=schedule_day_id,
        time=schema.time,
        patient_id=schema.patient_id,
        phone_number=schema.phone_number,
        address=schema.address,
        status=schema.status,
        type=schema.type,
        financing_sources_ids=schema.financing_sources_ids or [],
        reason=schema.reason,
        additional_services=(
            [
                additional_service.model_dump()
                for additional_service in schema.additional_services
            ]
            if schema.additional_services
            else []
        ),
    )


def map_appointment_update_schema_to_domain(
    appointment: AppointmentDomain, schema: UpdateAppointmentSchema
) -> AppointmentDomain:
    update_data = schema.model_dump(exclude_unset=True)
    for attr, val in update_data.items():
        if attr in (
            "status",
            "cancelled_at",
        ):  # Supposed to be controlled via service layer
            continue
        setattr(appointment, attr, val)

    return appointment


def map_appointment_domain_to_db_entity(appointment: AppointmentDomain) -> Appointment:
    def prepare_additional_services(additional_services):
        result = []
        for service in additional_services or []:
            svc = service.copy()
            price = svc.get("price")
            # JSONB is not working with Decimal so we convert to str
            if isinstance(price, Decimal):
                svc["price"] = str(price)  # Save to string for accuracy
            result.append(svc)
        return result

    return Appointment(
        schedule_day_id=appointment.schedule_day_id,
        time=appointment.time,
        patient_id=appointment.patient_id,
        phone_number=appointment.phone_number,
        address=appointment.address,
        status=appointment.status,
        type=appointment.type,
        financing_sources_ids=appointment.financing_sources_ids,
        reason=appointment.reason,
        additional_services=prepare_additional_services(
            appointment.additional_services
        ),
        cancelled_at=appointment.cancelled_at,
    )


def map_appointment_db_entity_to_domain(
    appointment_from_db: Appointment,
) -> AppointmentDomain:
    additional_services = []
    for service in appointment_from_db.additional_services or []:
        service_copy = service.copy()
        price_str = service_copy.get("price")
        if isinstance(price_str, str):
            try:
                service_copy["price"] = Decimal(price_str)
            except Exception:
                service_copy["price"] = Decimal(0)

        additional_services.append(service_copy)

    return AppointmentDomain(
        id=appointment_from_db.id,
        schedule_day_id=appointment_from_db.schedule_day_id,
        time=appointment_from_db.time,
        patient_id=appointment_from_db.patient_id,
        phone_number=appointment_from_db.phone_number,
        address=appointment_from_db.address,
        status=appointment_from_db.status,
        type=appointment_from_db.type,
        financing_sources_ids=appointment_from_db.financing_sources_ids,
        reason=appointment_from_db.reason,
        additional_services=additional_services,
        cancelled_at=appointment_from_db.cancelled_at,
    )


def map_appointment_domain_to_response_schema(
    appointment: AppointmentDomain,
    appointment_end_time: time,
    appointment_date: date,
    patient_schema: Optional[ResponsePatientSchema],
    doctor_schema: UserSchema,
) -> ResponseAppointmentSchema:
    return ResponseAppointmentSchema(
        id=appointment.id,
        schedule_day_id=appointment.schedule_day_id,
        start_time=appointment.time,
        end_time=appointment_end_time,
        date=appointment_date,
        patient=patient_schema,
        doctor=doctor_schema,
        phone_number=appointment.phone_number,
        address=appointment.address,
        status=appointment.status,
        type=appointment.type,
        financing_sources_ids=appointment.financing_sources_ids,
        reason=appointment.reason,
        additional_services=[
            AdditionalServiceSchema(
                name=additional_service["name"],
                financing_source_id=additional_service["financing_source_id"],
                price=additional_service.get("price", Decimal(0)),
            )
            for additional_service in appointment.additional_services
        ],
        cancelled_at=appointment.cancelled_at,
    )


def map_schedule_domain_to_db_entity(schedule_domain: ScheduleDomain) -> Schedule:
    return Schedule(
        doctor_id=schedule_domain.doctor_id,
        schedule_name=schedule_domain.schedule_name,
        period_start=schedule_domain.period_start,
        period_end=schedule_domain.period_end,
        appointment_interval=schedule_domain.appointment_interval,
        description=schedule_domain.description,
    )


def map_schedule_db_entity_to_domain(schedule_from_db: Schedule) -> ScheduleDomain:
    return ScheduleDomain(
        id=schedule_from_db.id,
        doctor_id=schedule_from_db.doctor_id,
        schedule_name=schedule_from_db.schedule_name,
        period_start=schedule_from_db.period_start,
        period_end=schedule_from_db.period_end,
        is_active=schedule_from_db.is_active,
        appointment_interval=schedule_from_db.appointment_interval,
        description=schedule_from_db.description,
    )


def map_schedule_day_db_entity_to_schema(
    schedule_day: ScheduleDay,
) -> ResponseScheduleDaySchema:
    return ResponseScheduleDaySchema(
        id=schedule_day.id,
        schedule_id=schedule_day.schedule_id,
        day_of_week=schedule_day.day_of_week,
        is_active=schedule_day.is_active,
        work_start_time=schedule_day.work_start_time,
        work_end_time=schedule_day.work_end_time,
        break_start_time=schedule_day.break_start_time,
        break_end_time=schedule_day.break_end_time,
        date=schedule_day.date,
    )
