from datetime import datetime, time
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from src.apps.assets_journal.domain.models.newborn_asset import (
    NewbornAssetDomain,
    NewbornDiagnosis,
    MotherData,
    NewbornData
)
from src.apps.assets_journal.domain.enums import (
    DiagnosisTypeEnum,
    DeliveryTypeEnum,
    PregnancyWeekEnum,
    NewbornConditionEnum,
    TransferDestinationEnum,
    MedicalServiceTypeEnum,
)
from src.apps.assets_journal.infrastructure.api.schemas.requests.newborn_asset_schemas import (
    CreateNewbornAssetSchema,
    NewbornDiagnosisSchema,
    MotherDataSchema,
    NewbornDataSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.newborn_asset_schemas import (
    NewbornAssetResponseSchema,
    NewbornAssetListItemSchema,
    NewbornDiagnosisResponseSchema,
    MotherDataResponseSchema,
    NewbornDataResponseSchema,
)
from src.apps.assets_journal.infrastructure.db_models.newborn_models import NewbornAsset


def map_newborn_diagnosis_domain_to_dict(diagnosis: NewbornDiagnosis) -> dict:
    """Маппинг доменной модели диагноза в словарь для JSON"""
    return {
        "diagnosis_type": diagnosis.diagnosis_type.value,
        "diagnosis_code": diagnosis.diagnosis_code,
        "diagnosis_name": diagnosis.diagnosis_name,
        "note": diagnosis.note,
    }


def map_newborn_diagnosis_dict_to_domain(diagnosis_dict: dict) -> NewbornDiagnosis:
    """Маппинг словаря из JSON в доменную модель диагноза"""
    return NewbornDiagnosis(
        diagnosis_type=DiagnosisTypeEnum(diagnosis_dict.get("diagnosis_type", "primary")),
        diagnosis_code=diagnosis_dict.get("diagnosis_code", ""),
        diagnosis_name=diagnosis_dict.get("diagnosis_name", ""),
        note=diagnosis_dict.get("note"),
    )


def map_mother_data_domain_to_dict(mother_data: MotherData) -> dict:
    """Маппинг доменной модели данных матери в словарь для JSON"""
    return {
        "iin": mother_data.iin,
        "full_name": mother_data.full_name,
        "address": mother_data.address,
        "birth_date": mother_data.birth_date.isoformat() if mother_data.birth_date else None,
        "birth_time": mother_data.birth_time.isoformat() if mother_data.birth_time else None,
        "delivery_type": mother_data.delivery_type.value if mother_data.delivery_type else None,
        "pregnancy_weeks": mother_data.pregnancy_weeks.value if mother_data.pregnancy_weeks else None,
        "discharge_date": mother_data.discharge_date.isoformat() if mother_data.discharge_date else None,
        "discharge_time": mother_data.discharge_time.isoformat() if mother_data.discharge_time else None,
    }


def map_mother_data_dict_to_domain(mother_dict: dict) -> MotherData:
    """Маппинг словаря из JSON в доменную модель данных матери"""

    def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str)
        except:
            return None

    def parse_time(time_str: Optional[str]) -> Optional[time]:
        if not time_str:
            return None
        try:
            if 'T' in time_str:
                return datetime.fromisoformat(time_str).time()
            else:
                return time.fromisoformat(time_str)
        except:
            return None

    return MotherData(
        iin=mother_dict.get("iin"),
        full_name=mother_dict.get("full_name"),
        address=mother_dict.get("address"),
        birth_date=parse_datetime(mother_dict.get("birth_date")),
        birth_time=parse_time(mother_dict.get("birth_time")),
        delivery_type=DeliveryTypeEnum(mother_dict["delivery_type"]) if mother_dict.get("delivery_type") else None,
        pregnancy_weeks=PregnancyWeekEnum(mother_dict["pregnancy_weeks"]) if mother_dict.get(
            "pregnancy_weeks") else None,
        discharge_date=parse_datetime(mother_dict.get("discharge_date")),
        discharge_time=parse_time(mother_dict.get("discharge_time")),
    )


def map_newborn_data_domain_to_dict(newborn_data: NewbornData) -> dict:
    """Маппинг доменной модели данных новорожденного в словарь для JSON"""
    return {
        "birth_date": newborn_data.birth_date.isoformat() if newborn_data.birth_date else None,
        "birth_time": newborn_data.birth_time.isoformat() if newborn_data.birth_time else None,
        "weight_grams": str(newborn_data.weight_grams) if newborn_data.weight_grams else None,
        "height_cm": str(newborn_data.height_cm) if newborn_data.height_cm else None,
        "transfer_destination": newborn_data.transfer_destination.value if newborn_data.transfer_destination else None,
        "condition": newborn_data.condition.value if newborn_data.condition else None,
        "medical_services": [service.value for service in
                             newborn_data.medical_services] if newborn_data.medical_services else [],
    }


def map_newborn_data_dict_to_domain(newborn_dict: dict) -> NewbornData:
    """Маппинг словаря из JSON в доменную модель данных новорожденного"""

    def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str)
        except:
            return None

    def parse_time(time_str: Optional[str]) -> Optional[time]:
        if not time_str:
            return None
        try:
            if 'T' in time_str:
                return datetime.fromisoformat(time_str).time()
            else:
                return time.fromisoformat(time_str)
        except:
            return None

    def parse_decimal(value: Optional[str]) -> Optional[Decimal]:
        if not value:
            return None
        try:
            return Decimal(str(value))
        except:
            return None

    medical_services = []
    if newborn_dict.get("medical_services"):
        for service in newborn_dict["medical_services"]:
            try:
                medical_services.append(MedicalServiceTypeEnum(service))
            except ValueError:
                pass

    return NewbornData(
        birth_date=parse_datetime(newborn_dict.get("birth_date")),
        birth_time=parse_time(newborn_dict.get("birth_time")),
        weight_grams=parse_decimal(newborn_dict.get("weight_grams")),
        height_cm=parse_decimal(newborn_dict.get("height_cm")),
        transfer_destination=TransferDestinationEnum(newborn_dict["transfer_destination"]) if newborn_dict.get(
            "transfer_destination") else None,
        condition=NewbornConditionEnum(newborn_dict["condition"]) if newborn_dict.get("condition") else None,
        medical_services=medical_services,
    )


def map_newborn_diagnosis_schema_to_domain(diagnosis_schema: NewbornDiagnosisSchema) -> NewbornDiagnosis:
    """Маппинг схемы диагноза в доменную модель"""
    return NewbornDiagnosis(
        diagnosis_type=diagnosis_schema.diagnosis_type,
        diagnosis_code=diagnosis_schema.diagnosis_code,
        diagnosis_name=diagnosis_schema.diagnosis_name,
        note=diagnosis_schema.note,
    )


def map_mother_data_schema_to_domain(mother_schema: MotherDataSchema) -> MotherData:
    """Маппинг схемы данных матери в доменную модель"""
    return MotherData(
        iin=mother_schema.iin,
        full_name=mother_schema.full_name,
        address=mother_schema.address,
        birth_date=mother_schema.birth_date,
        birth_time=mother_schema.birth_time,
        delivery_type=mother_schema.delivery_type,
        pregnancy_weeks=mother_schema.pregnancy_weeks,
        discharge_date=mother_schema.discharge_date,
        discharge_time=mother_schema.discharge_time,
    )


def map_newborn_data_schema_to_domain(newborn_schema: NewbornDataSchema) -> NewbornData:
    """Маппинг схемы данных новорожденного в доменную модель"""
    return NewbornData(
        birth_date=newborn_schema.birth_date,
        birth_time=newborn_schema.birth_time,
        weight_grams=newborn_schema.weight_grams,
        height_cm=newborn_schema.height_cm,
        transfer_destination=newborn_schema.transfer_destination,
        condition=newborn_schema.condition,
        medical_services=newborn_schema.medical_services or [],
    )


def map_newborn_diagnosis_domain_to_response(diagnosis: NewbornDiagnosis) -> NewbornDiagnosisResponseSchema:
    """Маппинг доменной модели диагноза в схему ответа"""
    return NewbornDiagnosisResponseSchema(
        diagnosis_type=diagnosis.diagnosis_type,
        diagnosis_code=diagnosis.diagnosis_code,
        diagnosis_name=diagnosis.diagnosis_name,
        note=diagnosis.note,
    )


def map_mother_data_domain_to_response(mother_data: MotherData) -> MotherDataResponseSchema:
    """Маппинг доменной модели данных матери в схему ответа"""
    return MotherDataResponseSchema(
        iin=mother_data.iin,
        full_name=mother_data.full_name,
        address=mother_data.address,
        birth_date=mother_data.birth_date,
        birth_time=mother_data.birth_time,
        delivery_type=mother_data.delivery_type,
        pregnancy_weeks=mother_data.pregnancy_weeks,
        discharge_date=mother_data.discharge_date,
        discharge_time=mother_data.discharge_time,
    )


def map_newborn_data_domain_to_response(newborn_data: NewbornData) -> NewbornDataResponseSchema:
    """Маппинг доменной модели данных новорожденного в схему ответа"""
    return NewbornDataResponseSchema(
        birth_date=newborn_data.birth_date,
        birth_time=newborn_data.birth_time,
        weight_grams=newborn_data.weight_grams,
        height_cm=newborn_data.height_cm,
        transfer_destination=newborn_data.transfer_destination,
        condition=newborn_data.condition,
        medical_services=newborn_data.medical_services or [],
    )


def map_newborn_asset_domain_to_db(domain: NewbornAssetDomain) -> NewbornAsset:
    """Маппинг доменной модели в DB модель"""
    # Преобразуем диагнозы в JSON
    diagnoses_json = [map_newborn_diagnosis_domain_to_dict(d) for d in domain.diagnoses] if domain.diagnoses else []

    # Преобразуем данные матери в JSON
    mother_data_json = map_mother_data_domain_to_dict(domain.mother_data) if domain.mother_data else {}

    # Преобразуем данные новорожденного в JSON
    newborn_data_json = map_newborn_data_domain_to_dict(domain.newborn_data) if domain.newborn_data else {}

    # Если patient_id равен специальному UUID для незарегистрированных, сохраняем как None
    db_patient_id = None if str(domain.patient_id) == '00000000-0000-0000-0000-000000000000' else domain.patient_id

    return NewbornAsset(
        id=domain.id,
        bg_asset_id=domain.bg_asset_id,
        patient_id=db_patient_id,
        patient_full_name_if_not_registered=domain.patient_full_name_if_not_registered,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        actual_datetime=domain.actual_datetime,
        received_from=domain.received_from,
        is_repeat=domain.is_repeat,
        mother_data=mother_data_json,
        newborn_data=newborn_data_json,
        diagnoses=diagnoses_json,
        diagnosis_note=domain.diagnosis_note,
        status=domain.status,
        delivery_status=domain.delivery_status,
        has_confirm=domain.has_confirm,
        has_files=domain.has_files,
        has_refusal=domain.has_refusal,
    )


def map_newborn_asset_db_to_domain(db_asset: NewbornAsset) -> NewbornAssetDomain:
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
            diagnoses.append(map_newborn_diagnosis_dict_to_domain(diagnosis_dict))

    # Преобразуем данные матери из JSON
    mother_data = None
    if db_asset.mother_data:
        mother_data = map_mother_data_dict_to_domain(db_asset.mother_data)

    # Преобразуем данные новорожденного из JSON
    newborn_data = None
    if db_asset.newborn_data:
        newborn_data = map_newborn_data_dict_to_domain(db_asset.newborn_data)

    return NewbornAssetDomain(
        id=db_asset.id,
        bg_asset_id=db_asset.bg_asset_id,
        patient_id=db_asset.patient_id,
        patient_full_name_if_not_registered=db_asset.patient_full_name_if_not_registered,
        receive_date=db_asset.receive_date,
        receive_time=db_asset.receive_time,
        actual_datetime=db_asset.actual_datetime,
        received_from=db_asset.received_from,
        is_repeat=db_asset.is_repeat,
        mother_data=mother_data,
        newborn_data=newborn_data,
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


def map_newborn_asset_domain_to_full_response(domain: NewbornAssetDomain) -> NewbornAssetResponseSchema:
    """Маппинг доменной модели в полную схему ответа"""
    diagnoses_response = [map_newborn_diagnosis_domain_to_response(d) for d in domain.diagnoses]
    mother_data_response = map_mother_data_domain_to_response(domain.mother_data) if domain.mother_data else None
    newborn_data_response = map_newborn_data_domain_to_response(domain.newborn_data) if domain.newborn_data else None

    return NewbornAssetResponseSchema(
        id=domain.id,
        bg_asset_id=domain.bg_asset_id,
        organization_id=domain.organization_id,
        patient_id=domain.patient_id,
        patient_full_name=domain.patient_full_name,
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        patient_full_name_if_not_registered=domain.patient_full_name_if_not_registered,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        actual_datetime=domain.actual_datetime,
        received_from=domain.received_from,
        is_repeat=domain.is_repeat,
        mother_data=mother_data_response,
        newborn_data=newborn_data_response,
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


def map_newborn_asset_domain_to_list_item(domain: NewbornAssetDomain) -> NewbornAssetListItemSchema:
    """Маппинг доменной модели в схему для списка"""
    # Получаем данные организации если они загружены
    organization_name = None
    if domain.organization_data:
        organization_name = domain.organization_data.get('name')

    # Получаем ФИО матери
    mother_full_name = None
    if domain.mother_data and domain.mother_data.full_name:
        mother_full_name = domain.mother_data.full_name

    return NewbornAssetListItemSchema(
        id=domain.id,
        organization_id=domain.organization_id,
        organization_name=organization_name,
        patient_id=domain.patient_id,
        patient_full_name=domain.patient_full_name or "Новорожденный",
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        mother_full_name=mother_full_name,
        newborn_summary=domain.newborn_summary,
        diagnoses_summary=domain.diagnoses_summary,
        status=domain.status,
        delivery_status=domain.delivery_status,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
    )


def map_create_schema_to_domain(create_schema: CreateNewbornAssetSchema,
                                patient_id: Optional[UUID]) -> NewbornAssetDomain:
    """Маппинг схемы создания в доменную модель"""

    # Преобразуем диагнозы
    diagnoses = [map_newborn_diagnosis_schema_to_domain(d) for d in create_schema.diagnoses]

    # Преобразуем данные матери
    mother_data = None
    if create_schema.mother_data:
        mother_data = map_mother_data_schema_to_domain(create_schema.mother_data)

    # Преобразуем данные новорожденного
    newborn_data = None
    if create_schema.newborn_data:
        newborn_data = map_newborn_data_schema_to_domain(create_schema.newborn_data)

    # Если patient_id is None, создаем временный UUID для доменной модели
    # но в БД он будет сохранен как NULL благодаря nullable=True
    domain_patient_id = patient_id or UUID('00000000-0000-0000-0000-000000000000')

    return NewbornAssetDomain(
        bg_asset_id=create_schema.bg_asset_id,
        patient_id=domain_patient_id,
        patient_full_name_if_not_registered=create_schema.patient_full_name_if_not_registered,
        receive_date=create_schema.receive_date,
        receive_time=create_schema.receive_time,
        actual_datetime=create_schema.actual_datetime or create_schema.receive_date,
        received_from=create_schema.received_from,
        is_repeat=create_schema.is_repeat,
        mother_data=mother_data,
        newborn_data=newborn_data,
        diagnoses=diagnoses,
        diagnosis_note=create_schema.diagnosis_note,
    )


def map_bg_response_to_newborn_domain(bg_data: dict, patient_id: UUID) -> NewbornAssetDomain:
    """Маппинг ответа BG в доменную модель активов новорожденных"""

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
        primary_diagnosis = NewbornDiagnosis(
            diagnosis_type=DiagnosisTypeEnum.PRIMARY,
            diagnosis_code=bg_data["sick"].get("code", ""),
            diagnosis_name=bg_data["sick"].get("name", ""),
        )
        diagnoses.append(primary_diagnosis)

    # Парсим данные о матери из BG
    mother_data = None
    if bg_data.get("mother"):
        mother_info = bg_data["mother"]
        mother_data = MotherData(
            iin=mother_info.get("iin"),
            full_name=mother_info.get("full_name"),
            address=mother_info.get("address"),
            birth_date=parse_datetime(mother_info.get("birth_date")),
            birth_time=parse_time(mother_info.get("birth_time")),
        )

    # Парсим данные о новорожденном из BG
    newborn_data = None
    if bg_data.get("newborn"):
        newborn_info = bg_data["newborn"]
        newborn_data = NewbornData(
            birth_date=parse_datetime(newborn_info.get("birth_date")),
            birth_time=parse_time(newborn_info.get("birth_time")),
            weight_grams=Decimal(str(newborn_info["weight_grams"])) if newborn_info.get("weight_grams") else None,
            height_cm=Decimal(str(newborn_info["height_cm"])) if newborn_info.get("height_cm") else None,
        )

    return NewbornAssetDomain(
        bg_asset_id=bg_data.get("id", ""),
        patient_id=patient_id,
        patient_full_name_if_not_registered=bg_data.get("patient_name"),
        receive_date=reg_datetime,
        receive_time=reg_time,
        actual_datetime=parse_datetime(bg_data.get("birth_date")) or reg_datetime,
        received_from=bg_data.get("orgHealthCareRequest", {}).get("name", ""),
        is_repeat=False,
        mother_data=mother_data,
        newborn_data=newborn_data,
        diagnoses=diagnoses,
        diagnosis_note=bg_data.get("additionalInformation"),
        has_confirm=bg_data.get("hasConfirm", "false").lower() == "true",
        has_files=bg_data.get("hasFiles", "false").lower() == "true",
        has_refusal=bg_data.get("hasRefusal", "false").lower() == "true",
    )