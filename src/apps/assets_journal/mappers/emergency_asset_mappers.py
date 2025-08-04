from datetime import datetime, time
from typing import Optional, List
from uuid import UUID

from src.apps.assets_journal.domain.models.emergency_asset import EmergencyAssetDomain, EmergencyDiagnosis
from src.apps.assets_journal.domain.enums import DiagnosisTypeEnum
from src.apps.assets_journal.infrastructure.api.schemas.requests.emergency_asset_schemas import (
    CreateEmergencyAssetSchema,
    EmergencyDiagnosisSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.emergency_asset_schemas import (
    EmergencyAssetResponseSchema,
    EmergencyAssetListItemSchema,
    EmergencyDiagnosisResponseSchema,
)
from src.apps.assets_journal.infrastructure.db_models.emergency_models import EmergencyAsset


def map_emergency_diagnosis_domain_to_dict(diagnosis: EmergencyDiagnosis) -> dict:
    """Маппинг доменной модели диагноза в словарь для JSON"""
    return {
        "diagnosis_type": diagnosis.diagnosis_type.value,
        "diagnosis_code": diagnosis.diagnosis_code,
        "diagnosis_name": diagnosis.diagnosis_name,
        "note": diagnosis.note,
    }


def map_emergency_diagnosis_dict_to_domain(diagnosis_dict: dict) -> EmergencyDiagnosis:
    """Маппинг словаря из JSON в доменную модель диагноза"""
    return EmergencyDiagnosis(
        diagnosis_type=DiagnosisTypeEnum(diagnosis_dict.get("diagnosis_type", "primary")),
        diagnosis_code=diagnosis_dict.get("diagnosis_code", ""),
        diagnosis_name=diagnosis_dict.get("diagnosis_name", ""),
        note=diagnosis_dict.get("note"),
    )


def map_emergency_diagnosis_schema_to_domain(diagnosis_schema: EmergencyDiagnosisSchema) -> EmergencyDiagnosis:
    """Маппинг схемы диагноза в доменную модель"""

    return EmergencyDiagnosis(
        diagnosis_type=diagnosis_schema.get('diagnosis_type', DiagnosisTypeEnum.PRIMARY),
        diagnosis_code=diagnosis_schema.get('diagnosis_code', ''),
        diagnosis_name=diagnosis_schema.get('diagnosis_name', ''),
        note=diagnosis_schema.get('note', None)
    )


def map_emergency_diagnosis_domain_to_response(diagnosis: EmergencyDiagnosis) -> EmergencyDiagnosisResponseSchema:
    """Маппинг доменной модели диагноза в схему ответа"""
    return EmergencyDiagnosisResponseSchema(
        diagnosis_type=diagnosis.diagnosis_type,
        diagnosis_code=diagnosis.diagnosis_code,
        diagnosis_name=diagnosis.diagnosis_name,
        note=diagnosis.note,
    )


def map_emergency_asset_domain_to_db(domain: EmergencyAssetDomain) -> EmergencyAsset:
    """Маппинг доменной модели в DB модель"""
    # Преобразуем диагнозы в JSON
    diagnoses_json = [map_emergency_diagnosis_domain_to_dict(d) for d in domain.diagnoses] if domain.diagnoses else []

    return EmergencyAsset(
        id=domain.id,
        bg_asset_id=domain.bg_asset_id,
        patient_id=domain.patient_id,
        patient_location_address=domain.patient_location_address,
        is_not_attached_to_mo=domain.is_not_attached_to_mo,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        actual_datetime=domain.actual_datetime,
        received_from=domain.received_from,
        is_repeat=domain.is_repeat,
        outcome=domain.outcome,
        diagnoses=diagnoses_json,
        diagnosis_note=domain.diagnosis_note,
        status=domain.status,
        delivery_status=domain.delivery_status,
        has_confirm=domain.has_confirm,
        has_files=domain.has_files,
        has_refusal=domain.has_refusal,
    )


def map_emergency_asset_db_to_domain(db_asset: EmergencyAsset) -> EmergencyAssetDomain:
    """Маппинг DB модели в доменную модель"""

    patient_data = None
    if db_asset.patient:
        patient_data = {
            'id': str(db_asset.patient.id),
            'iin': db_asset.patient.iin,
            'first_name': db_asset.patient.first_name,
            'last_name': db_asset.patient.last_name,
            'middle_name': db_asset.patient.middle_name,
            'date_of_birth': db_asset.patient.date_of_birth,
            'gender': db_asset.patient.gender.value if db_asset.patient.gender else None,
            'attachment_data': db_asset.patient.attachment_data,
        }

    # Преобразуем диагнозы из JSON
    diagnoses = []
    if db_asset.diagnoses:
        for diagnosis_dict in db_asset.diagnoses:
            diagnoses.append(map_emergency_diagnosis_dict_to_domain(diagnosis_dict))

    return EmergencyAssetDomain(
        id=db_asset.id,
        bg_asset_id=db_asset.bg_asset_id,
        patient_id=db_asset.patient_id,
        patient_location_address=db_asset.patient_location_address,
        is_not_attached_to_mo=db_asset.is_not_attached_to_mo,
        receive_date=db_asset.receive_date,
        receive_time=db_asset.receive_time,
        actual_datetime=db_asset.actual_datetime,
        received_from=db_asset.received_from,
        is_repeat=db_asset.is_repeat,
        outcome=db_asset.outcome,
        diagnoses=diagnoses,
        diagnosis_note=db_asset.diagnosis_note,
        status=db_asset.status,
        delivery_status=db_asset.delivery_status,
        has_confirm=db_asset.has_confirm,
        has_files=db_asset.has_files,
        has_refusal=db_asset.has_refusal,
        created_at=db_asset.created_at,
        updated_at=db_asset.changed_at,
        patient_data=patient_data,
    )


def map_emergency_asset_domain_to_full_response(domain: EmergencyAssetDomain) -> EmergencyAssetResponseSchema:
    """Маппинг доменной модели в полную схему ответа"""
    diagnoses_response = [map_emergency_diagnosis_domain_to_response(d) for d in domain.diagnoses]

    return EmergencyAssetResponseSchema(
        id=domain.id,
        bg_asset_id=domain.bg_asset_id,
        organization_id=domain.organization_id,
        patient_id=domain.patient_id,
        patient_full_name=domain.patient_full_name,
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        patient_location_address=domain.patient_location_address,
        is_not_attached_to_mo=domain.is_not_attached_to_mo,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        actual_datetime=domain.actual_datetime,
        received_from=domain.received_from,
        is_repeat=domain.is_repeat,
        outcome=domain.outcome,
        diagnoses=diagnoses_response,
        diagnosis_note=domain.diagnosis_note,
        status=domain.status,
        delivery_status=domain.delivery_status,
        has_confirm=domain.has_confirm,
        has_files=domain.has_files,
        has_refusal=domain.has_refusal,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
        organization_data=domain.organization_data,
        patient_data=domain.patient_data,
    )


def map_emergency_asset_domain_to_list_item(domain: EmergencyAssetDomain) -> EmergencyAssetListItemSchema:
    """Маппинг доменной модели в схему для списка"""
    # Получаем данные организации если они загружены
    organization_name = None
    if domain.organization_data:
        organization_name = domain.organization_data.get('name')

    return EmergencyAssetListItemSchema(
        id=domain.id,
        organization_id=domain.organization_id,
        organization_name=organization_name,
        patient_id=domain.patient_id,
        patient_full_name=domain.patient_full_name,
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        diagnoses_summary=domain.diagnoses_summary,
        outcome=domain.outcome,
        status=domain.status,
        delivery_status=domain.delivery_status,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
    )


def map_create_schema_to_domain(create_schema: CreateEmergencyAssetSchema, patient_id: UUID) -> EmergencyAssetDomain:
    """Маппинг схемы создания в доменную модель"""

    # Преобразуем диагнозы
    diagnoses = [map_emergency_diagnosis_schema_to_domain(d) for d in create_schema.diagnoses]

    return EmergencyAssetDomain(
        bg_asset_id=create_schema.bg_asset_id,
        patient_id=patient_id,
        patient_location_address=create_schema.patient_location_address,
        is_not_attached_to_mo=create_schema.is_not_attached_to_mo,
        receive_date=create_schema.receive_date,
        receive_time=create_schema.receive_time,
        actual_datetime=create_schema.actual_datetime or create_schema.receive_date,
        received_from=create_schema.received_from,
        is_repeat=create_schema.is_repeat,
        outcome=create_schema.outcome,
        diagnoses=diagnoses,
        diagnosis_note=create_schema.diagnosis_note,
    )


def map_bg_response_to_emergency_domain(bg_data: dict, patient_id: UUID) -> EmergencyAssetDomain:
    """Маппинг ответа BG в доменную модель активов скорой помощи"""

    # Парсинг дат из строк
    def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('T', ' ').replace('Z', ''))
        except:
            return None

    # Парсинг времени
    def parse_time(date_str: Optional[str]) -> Optional[time]:
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str.replace('T', ' ').replace('Z', ''))
            return dt.time()
        except:
            return None

    # Получаем дату регистрации
    reg_datetime = parse_datetime(bg_data.get("regDate")) or datetime.utcnow()
    reg_time = parse_time(bg_data.get("regDate")) or time(9, 0)

    # Парсим диагнозы из BG данных (если есть)
    diagnoses = []
    if bg_data.get("sick"):
        primary_diagnosis = EmergencyDiagnosis(
            diagnosis_type=DiagnosisTypeEnum.PRIMARY,
            diagnosis_code=bg_data["sick"].get("code", ""),
            diagnosis_name=bg_data["sick"].get("name", ""),
        )
        diagnoses.append(primary_diagnosis)

    return EmergencyAssetDomain(
        bg_asset_id=bg_data.get("id", ""),
        patient_id=patient_id,
        patient_location_address=bg_data.get("address", ""),
        is_not_attached_to_mo=False,  # По умолчанию предполагаем, что прикреплен
        receive_date=reg_datetime,
        receive_time=reg_time,
        actual_datetime=parse_datetime(bg_data.get("emergencyDate")) or reg_datetime,
        received_from=bg_data.get("orgHealthCareRequest", {}).get("name", ""),
        is_repeat=False,
        outcome=None,  # В BG может не быть информации об исходе
        diagnoses=diagnoses,
        diagnosis_note=bg_data.get("additionalInformation"),
        has_confirm=bg_data.get("hasConfirm", "false").lower() == "true",
        has_files=bg_data.get("hasFiles", "false").lower() == "true",
        has_refusal=bg_data.get("hasRefusal", "false").lower() == "true",
    )