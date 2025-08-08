from datetime import datetime, time
from uuid import UUID

from src.apps.assets_journal.domain.models.home_call import HomeCallDomain, HomeCallListItemDomain
from src.apps.assets_journal.infrastructure.db_models.home_call_models import HomeCall
from src.apps.assets_journal.infrastructure.api.schemas.responses.home_call_schemas import (
    HomeCallResponseSchema,
    HomeCallListItemSchema,
)


def map_home_call_domain_to_db(domain: HomeCallDomain) -> HomeCall:
    """Маппинг доменной модели в DB модель"""
    return HomeCall(
        id=domain.id,
        call_number=domain.call_number,
        patient_id=domain.patient_id,
        patient_address=domain.patient_address,
        patient_phone=domain.patient_phone,
        registration_date=domain.registration_date,
        registration_time=domain.registration_time,
        registration_datetime=domain.registration_datetime,
        execution_date=domain.execution_date,
        execution_time=domain.execution_time,
        area=domain.area,
        specialization=domain.specialization,
        specialist=domain.specialist,
        is_insured=domain.is_insured,
        has_oms=domain.has_oms,
        source=domain.source,
        category=domain.category,
        reason=domain.reason,
        call_type=domain.call_type,
        reason_patient_words=domain.reason_patient_words,
        visit_type=domain.visit_type,
        status=domain.status,
        notes=domain.notes,
    )


def map_home_call_db_to_domain(db_home_call: HomeCall) -> HomeCallDomain:
    """Маппинг DB модели в доменную модель"""

    patient_data = None
    if db_home_call.patient:
        patient_data = {
            'id': str(db_home_call.patient.id),
            'iin': db_home_call.patient.iin,
            'first_name': db_home_call.patient.first_name,
            'last_name': db_home_call.patient.last_name,
            'middle_name': db_home_call.patient.middle_name,
            'date_of_birth': db_home_call.patient.date_of_birth,
            'gender': db_home_call.patient.gender.value if db_home_call.patient.gender else None,
            'attachment_data': db_home_call.patient.attachment_data,
        }

    return HomeCallDomain(
        id=db_home_call.id,
        call_number=db_home_call.call_number,
        patient_id=db_home_call.patient_id,
        patient_address=db_home_call.patient_address,
        patient_phone=db_home_call.patient_phone,
        registration_date=db_home_call.registration_date,
        registration_time=db_home_call.registration_time,
        registration_datetime=db_home_call.registration_datetime,
        execution_date=db_home_call.execution_date,
        execution_time=db_home_call.execution_time,
        area=db_home_call.area,
        specialization=db_home_call.specialization,
        specialist=db_home_call.specialist,
        is_insured=db_home_call.is_insured,
        has_oms=db_home_call.has_oms,
        source=db_home_call.source,
        category=db_home_call.category,
        reason=db_home_call.reason,
        call_type=db_home_call.call_type,
        reason_patient_words=db_home_call.reason_patient_words,
        visit_type=db_home_call.visit_type,
        status=db_home_call.status,
        notes=db_home_call.notes,
        created_at=db_home_call.created_at,
        updated_at=db_home_call.changed_at,
        patient_data=patient_data,
    )


def map_home_call_db_to_list_item(db_home_call: HomeCall) -> HomeCallListItemDomain:
    """Маппинг DB модели в доменную модель для списка"""

    # Получаем ФИО пациента
    patient_full_name = ""
    patient_iin = ""
    patient_birth_date = None
    organization_id = None

    if db_home_call.patient:
        last_name = db_home_call.patient.last_name or ""
        first_name = db_home_call.patient.first_name or ""
        middle_name = db_home_call.patient.middle_name or ""
        patient_full_name = f"{last_name} {first_name} {middle_name}".strip()
        patient_iin = db_home_call.patient.iin or ""
        patient_birth_date = db_home_call.patient.date_of_birth

        # Получаем ID организации из attachment_data
        if db_home_call.patient.attachment_data:
            organization_id = db_home_call.patient.attachment_data.get('attached_clinic_id')

    return HomeCallListItemDomain(
        id=db_home_call.id,
        call_number=db_home_call.call_number,
        patient_id=db_home_call.patient_id,
        patient_full_name=patient_full_name,
        patient_iin=patient_iin,
        patient_birth_date=patient_birth_date,
        registration_date=db_home_call.registration_date,
        registration_time=db_home_call.registration_time,
        category=db_home_call.category,
        status=db_home_call.status,
        source=db_home_call.source,
        specialist=db_home_call.specialist,
        specialization=db_home_call.specialization,
        area=db_home_call.area,
        created_at=db_home_call.created_at,
        updated_at=db_home_call.changed_at,
        organization_id=organization_id,
    )


def map_home_call_domain_to_full_response(domain: HomeCallDomain) -> HomeCallResponseSchema:
    """Маппинг доменной модели в полную схему ответа"""
    return HomeCallResponseSchema(
        id=domain.id,
        call_number=domain.call_number,
        organization_id=domain.organization_id,
        patient_id=domain.patient_id,
        patient_full_name=domain.patient_full_name,
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        patient_address=domain.patient_address,
        patient_phone=domain.patient_phone,
        registration_date=domain.registration_date,
        registration_time=domain.registration_time,
        registration_datetime=domain.registration_datetime,
        execution_date=domain.execution_date,
        execution_time=domain.execution_time,
        area=domain.area,
        specialization=domain.specialization,
        specialist=domain.specialist,
        is_insured=domain.is_insured,
        has_oms=domain.has_oms,
        source=domain.source,
        category=domain.category,
        reason=domain.reason,
        call_type=domain.call_type,
        reason_patient_words=domain.reason_patient_words,
        visit_type=domain.visit_type,
        status=domain.status,
        notes=domain.notes,
        is_active=domain.is_active,
        is_completed=domain.is_completed,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
        organization_data=domain.organization_data,
        patient_data=domain.patient_data,
    )


def map_home_call_domain_to_list_item(domain: HomeCallDomain) -> HomeCallListItemSchema:
    """Маппинг доменной модели в схему для списка"""
    # Получаем данные организации если они загружены
    organization_name = None
    if domain.organization_data:
        organization_name = domain.organization_data.get('name')

    return HomeCallListItemSchema(
        id=domain.id,
        call_number=domain.call_number,
        organization_id=domain.organization_id,
        organization_name=organization_name,
        patient_id=domain.patient_id,
        patient_full_name=domain.patient_full_name or "",
        patient_iin=domain.patient_iin or "",
        patient_birth_date=domain.patient_birth_date or datetime.now(),
        registration_date=domain.registration_date,
        registration_time=domain.registration_time,
        category=domain.category,
        status=domain.status,
        source=domain.source,
        specialist=domain.specialist,
        specialization=domain.specialization,
        area=domain.area,
        created_at=domain.created_at or datetime.now(),
        updated_at=domain.updated_at or datetime.now(),
    )


def map_create_schema_to_domain(create_schema, patient_id: UUID) -> HomeCallDomain:
    """Маппинг схемы создания в доменную модель"""
    return HomeCallDomain(
        patient_id=patient_id,
        patient_address=create_schema.patient_address,
        patient_phone=create_schema.patient_phone,
        registration_date=create_schema.registration_date,
        registration_time=create_schema.registration_time,
        registration_datetime=create_schema.registration_datetime or create_schema.registration_date,
        execution_date=create_schema.execution_date,
        execution_time=create_schema.execution_time,
        area=create_schema.area,
        specialization=create_schema.specialization,
        specialist=create_schema.specialist,
        is_insured=create_schema.is_insured,
        has_oms=create_schema.has_oms,
        source=create_schema.source,
        category=create_schema.category,
        reason=create_schema.reason,
        call_type=create_schema.call_type,
        reason_patient_words=create_schema.reason_patient_words,
        visit_type=create_schema.visit_type,
        notes=create_schema.notes,
    )