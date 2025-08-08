from datetime import datetime, date
from typing import Optional
from uuid import UUID

from src.apps.assets_journal.domain.models.sick_leave import SickLeaveDomain, SickLeaveListItemDomain
from src.apps.assets_journal.infrastructure.db_models.sick_leave_models import SickLeave
from src.apps.assets_journal.infrastructure.api.schemas.responses.sick_leave_schemas import (
    SickLeaveResponseSchema,
    SickLeaveListItemSchema,
)


def map_sick_leave_domain_to_db(domain: SickLeaveDomain) -> SickLeave:
    """Маппинг доменной модели в DB модель"""
    return SickLeave(
        id=domain.id,
        patient_id=domain.patient_id,
        patient_location_address=domain.patient_location_address,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        actual_datetime=domain.actual_datetime,
        received_from=domain.received_from,
        is_repeat=domain.is_repeat,
        workplace_name=domain.workplace_name,
        disability_start_date=domain.disability_start_date,
        disability_end_date=domain.disability_end_date,
        status=domain.status,
        sick_leave_reason=domain.sick_leave_reason,
        work_capacity=domain.work_capacity,
        area=domain.area,
        specialization=domain.specialization,
        specialist=domain.specialist,
        notes=domain.notes,
        is_primary=domain.is_primary,
        parent_sick_leave_id=domain.parent_sick_leave_id,
    )


def map_sick_leave_db_to_domain(db_sick_leave: SickLeave) -> SickLeaveDomain:
    """Маппинг DB модели в доменную модель"""

    patient_data = None
    if db_sick_leave.patient:
        patient_data = {
            'id': str(db_sick_leave.patient.id),
            'iin': db_sick_leave.patient.iin,
            'first_name': db_sick_leave.patient.first_name,
            'last_name': db_sick_leave.patient.last_name,
            'middle_name': db_sick_leave.patient.middle_name,
            'date_of_birth': db_sick_leave.patient.date_of_birth,
            'gender': db_sick_leave.patient.gender.value if db_sick_leave.patient.gender else None,
            'attachment_data': db_sick_leave.patient.attachment_data,
        }

    return SickLeaveDomain(
        id=db_sick_leave.id,
        patient_id=db_sick_leave.patient_id,
        patient_location_address=db_sick_leave.patient_location_address,
        receive_date=db_sick_leave.receive_date,
        receive_time=db_sick_leave.receive_time,
        actual_datetime=db_sick_leave.actual_datetime,
        received_from=db_sick_leave.received_from,
        is_repeat=db_sick_leave.is_repeat,
        workplace_name=db_sick_leave.workplace_name,
        disability_start_date=db_sick_leave.disability_start_date,
        disability_end_date=db_sick_leave.disability_end_date,
        status=db_sick_leave.status,
        sick_leave_reason=db_sick_leave.sick_leave_reason,
        work_capacity=db_sick_leave.work_capacity,
        area=db_sick_leave.area,
        specialization=db_sick_leave.specialization,
        specialist=db_sick_leave.specialist,
        notes=db_sick_leave.notes,
        is_primary=db_sick_leave.is_primary,
        parent_sick_leave_id=db_sick_leave.parent_sick_leave_id,
        created_at=db_sick_leave.created_at,
        updated_at=db_sick_leave.changed_at,
        patient_data=patient_data,
    )


def map_sick_leave_db_to_list_item(db_sick_leave: SickLeave) -> SickLeaveListItemDomain:
    """Маппинг DB модели в доменную модель для списка"""

    # Получаем ФИО пациента
    patient_full_name = ""
    patient_iin = ""
    patient_birth_date = None
    organization_id = None

    if db_sick_leave.patient:
        last_name = db_sick_leave.patient.last_name or ""
        first_name = db_sick_leave.patient.first_name or ""
        middle_name = db_sick_leave.patient.middle_name or ""
        patient_full_name = f"{last_name} {first_name} {middle_name}".strip()
        patient_iin = db_sick_leave.patient.iin or ""
        patient_birth_date = db_sick_leave.patient.date_of_birth

        # Получаем ID организации из attachment_data
        if db_sick_leave.patient.attachment_data:
            organization_id = db_sick_leave.patient.attachment_data.get('attached_clinic_id')

    # Вычисляем продолжительность в днях
    duration_days = None
    if db_sick_leave.disability_end_date:
        duration_days = (db_sick_leave.disability_end_date - db_sick_leave.disability_start_date).days + 1

    return SickLeaveListItemDomain(
        id=db_sick_leave.id,
        patient_id=db_sick_leave.patient_id,
        patient_full_name=patient_full_name,
        patient_iin=patient_iin,
        patient_birth_date=patient_birth_date,
        disability_start_date=db_sick_leave.disability_start_date,
        disability_end_date=db_sick_leave.disability_end_date,
        specialist=db_sick_leave.specialist,
        specialization=db_sick_leave.specialization,
        area=db_sick_leave.area,
        status=db_sick_leave.status,
        duration_days=duration_days,
        created_at=db_sick_leave.created_at,
        updated_at=db_sick_leave.changed_at,
        organization_id=organization_id,
    )


def map_sick_leave_domain_to_full_response(domain: SickLeaveDomain) -> SickLeaveResponseSchema:
    """Маппинг доменной модели в полную схему ответа"""
    return SickLeaveResponseSchema(
        id=domain.id,
        organization_id=domain.organization_id,
        patient_id=domain.patient_id,
        patient_full_name=domain.patient_full_name,
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        patient_location_address=domain.patient_location_address,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        actual_datetime=domain.actual_datetime,
        received_from=domain.received_from,
        is_repeat=domain.is_repeat,
        workplace_name=domain.workplace_name,
        disability_start_date=domain.disability_start_date,
        disability_end_date=domain.disability_end_date,
        status=domain.status,
        sick_leave_reason=domain.sick_leave_reason,
        work_capacity=domain.work_capacity,
        area=domain.area,
        specialization=domain.specialization,
        specialist=domain.specialist,
        notes=domain.notes,
        is_primary=domain.is_primary,
        parent_sick_leave_id=domain.parent_sick_leave_id,
        duration_days=domain.duration_days,
        is_active=domain.is_active,
        is_expired=domain.is_expired,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
        organization_data=domain.organization_data,
        patient_data=domain.patient_data,
    )


def map_sick_leave_domain_to_list_item(domain: SickLeaveDomain) -> SickLeaveListItemSchema:
    """Маппинг доменной модели в схему для списка"""
    # Получаем данные организации если они загружены
    organization_name = None
    if domain.organization_data:
        organization_name = domain.organization_data.get('name')

    return SickLeaveListItemSchema(
        id=domain.id,
        organization_id=domain.organization_id,
        organization_name=organization_name,
        patient_id=domain.patient_id,
        patient_full_name=domain.patient_full_name or "",
        patient_iin=domain.patient_iin or "",
        patient_birth_date=domain.patient_birth_date or datetime.now(),
        disability_start_date=domain.disability_start_date,
        disability_end_date=domain.disability_end_date,
        specialist=domain.specialist,
        specialization=domain.specialization,
        area=domain.area,
        status=domain.status,
        duration_days=domain.duration_days,
        created_at=domain.created_at or datetime.now(),
        updated_at=domain.updated_at or datetime.now(),
    )


def map_create_schema_to_domain(create_schema, patient_id: UUID) -> SickLeaveDomain:
    """Маппинг схемы создания в доменную модель"""
    return SickLeaveDomain(
        patient_id=patient_id,
        patient_location_address=create_schema.patient_location_address,
        receive_date=create_schema.receive_date,
        receive_time=create_schema.receive_time,
        actual_datetime=create_schema.actual_datetime or create_schema.receive_date,
        received_from=create_schema.received_from,
        is_repeat=create_schema.is_repeat,
        workplace_name=create_schema.workplace_name,
        disability_start_date=create_schema.disability_start_date,
        disability_end_date=create_schema.disability_end_date,
        sick_leave_reason=create_schema.sick_leave_reason,
        work_capacity=create_schema.work_capacity,
        area=create_schema.area,
        specialization=create_schema.specialization,
        specialist=create_schema.specialist,
        notes=create_schema.notes,
        is_primary=create_schema.is_primary,
        parent_sick_leave_id=create_schema.parent_sick_leave_id,
    )