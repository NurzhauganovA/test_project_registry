from datetime import datetime, time
from typing import Optional, Dict, Any
from uuid import UUID

from src.apps.assets_journal.domain.models.polyclinic_asset import (
    PolyclinicAssetDomain,
    PolyclinicAssetListItemDomain,
    WeeklySchedule
)
from src.apps.assets_journal.domain.enums import (
    PolyclinicVisitTypeEnum,
    PolyclinicServiceTypeEnum,
    PolyclinicOutcomeEnum,
    RejectionReasonByEnum, PolyclinicReasonAppeal, PolyclinicTypeActiveVisit,
)
from src.apps.assets_journal.infrastructure.api.schemas.requests.polyclinic_asset_schemas import (
    CreatePolyclinicAssetSchema,
    WeeklyScheduleSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.polyclinic_asset_schemas import (
    PolyclinicAssetResponseSchema,
    PolyclinicAssetListItemSchema,
    WeeklyScheduleResponseSchema,
)
from src.apps.assets_journal.infrastructure.db_models.polyclinic_models import PolyclinicAsset


def map_weekly_schedule_domain_to_dict(schedule: WeeklySchedule) -> Dict[str, Any]:
    """Маппинг доменной модели расписания в словарь для JSON"""
    return {
        "monday_enabled": schedule.monday_enabled,
        "monday_start_time": schedule.monday_start_time.isoformat() if schedule.monday_start_time else None,
        "monday_end_time": schedule.monday_end_time.isoformat() if schedule.monday_end_time else None,
        "tuesday_enabled": schedule.tuesday_enabled,
        "tuesday_start_time": schedule.tuesday_start_time.isoformat() if schedule.tuesday_start_time else None,
        "tuesday_end_time": schedule.tuesday_end_time.isoformat() if schedule.tuesday_end_time else None,
        "wednesday_enabled": schedule.wednesday_enabled,
        "wednesday_start_time": schedule.wednesday_start_time.isoformat() if schedule.wednesday_start_time else None,
        "wednesday_end_time": schedule.wednesday_end_time.isoformat() if schedule.wednesday_end_time else None,
        "thursday_enabled": schedule.thursday_enabled,
        "thursday_start_time": schedule.thursday_start_time.isoformat() if schedule.thursday_start_time else None,
        "thursday_end_time": schedule.thursday_end_time.isoformat() if schedule.thursday_end_time else None,
        "friday_enabled": schedule.friday_enabled,
        "friday_start_time": schedule.friday_start_time.isoformat() if schedule.friday_start_time else None,
        "friday_end_time": schedule.friday_end_time.isoformat() if schedule.friday_end_time else None,
        "saturday_enabled": schedule.saturday_enabled,
        "saturday_start_time": schedule.saturday_start_time.isoformat() if schedule.saturday_start_time else None,
        "saturday_end_time": schedule.saturday_end_time.isoformat() if schedule.saturday_end_time else None,
        "sunday_enabled": schedule.sunday_enabled,
        "sunday_start_time": schedule.sunday_start_time.isoformat() if schedule.sunday_start_time else None,
        "sunday_end_time": schedule.sunday_end_time.isoformat() if schedule.sunday_end_time else None,
    }


def map_weekly_schedule_dict_to_domain(schedule_dict: Dict[str, Any]) -> WeeklySchedule:
    """Маппинг словаря из JSON в доменную модель расписания"""

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

    return WeeklySchedule(
        monday_enabled=schedule_dict.get("monday_enabled", False),
        monday_start_time=parse_time(schedule_dict.get("monday_start_time")),
        monday_end_time=parse_time(schedule_dict.get("monday_end_time")),
        tuesday_enabled=schedule_dict.get("tuesday_enabled", False),
        tuesday_start_time=parse_time(schedule_dict.get("tuesday_start_time")),
        tuesday_end_time=parse_time(schedule_dict.get("tuesday_end_time")),
        wednesday_enabled=schedule_dict.get("wednesday_enabled", False),
        wednesday_start_time=parse_time(schedule_dict.get("wednesday_start_time")),
        wednesday_end_time=parse_time(schedule_dict.get("wednesday_end_time")),
        thursday_enabled=schedule_dict.get("thursday_enabled", False),
        thursday_start_time=parse_time(schedule_dict.get("thursday_start_time")),
        thursday_end_time=parse_time(schedule_dict.get("thursday_end_time")),
        friday_enabled=schedule_dict.get("friday_enabled", False),
        friday_start_time=parse_time(schedule_dict.get("friday_start_time")),
        friday_end_time=parse_time(schedule_dict.get("friday_end_time")),
        saturday_enabled=schedule_dict.get("saturday_enabled", False),
        saturday_start_time=parse_time(schedule_dict.get("saturday_start_time")),
        saturday_end_time=parse_time(schedule_dict.get("saturday_end_time")),
        sunday_enabled=schedule_dict.get("sunday_enabled", False),
        sunday_start_time=parse_time(schedule_dict.get("sunday_start_time")),
        sunday_end_time=parse_time(schedule_dict.get("sunday_end_time")),
    )


def map_weekly_schedule_schema_to_domain(schedule_schema: WeeklyScheduleSchema) -> WeeklySchedule:
    """Маппинг схемы расписания в доменную модель"""
    return WeeklySchedule(
        monday_enabled=schedule_schema.monday_enabled,
        monday_start_time=schedule_schema.monday_start_time,
        monday_end_time=schedule_schema.monday_end_time,
        tuesday_enabled=schedule_schema.tuesday_enabled,
        tuesday_start_time=schedule_schema.tuesday_start_time,
        tuesday_end_time=schedule_schema.tuesday_end_time,
        wednesday_enabled=schedule_schema.wednesday_enabled,
        wednesday_start_time=schedule_schema.wednesday_start_time,
        wednesday_end_time=schedule_schema.wednesday_end_time,
        thursday_enabled=schedule_schema.thursday_enabled,
        thursday_start_time=schedule_schema.thursday_start_time,
        thursday_end_time=schedule_schema.thursday_end_time,
        friday_enabled=schedule_schema.friday_enabled,
        friday_start_time=schedule_schema.friday_start_time,
        friday_end_time=schedule_schema.friday_end_time,
        saturday_enabled=schedule_schema.saturday_enabled,
        saturday_start_time=schedule_schema.saturday_start_time,
        saturday_end_time=schedule_schema.saturday_end_time,
        sunday_enabled=schedule_schema.sunday_enabled,
        sunday_start_time=schedule_schema.sunday_start_time,
        sunday_end_time=schedule_schema.sunday_end_time,
    )


def map_weekly_schedule_domain_to_response(schedule: WeeklySchedule) -> WeeklyScheduleResponseSchema:
    """Маппинг доменной модели расписания в схему ответа"""
    return WeeklyScheduleResponseSchema(
        monday_enabled=schedule.monday_enabled,
        monday_start_time=schedule.monday_start_time,
        monday_end_time=schedule.monday_end_time,
        tuesday_enabled=schedule.tuesday_enabled,
        tuesday_start_time=schedule.tuesday_start_time,
        tuesday_end_time=schedule.tuesday_end_time,
        wednesday_enabled=schedule.wednesday_enabled,
        wednesday_start_time=schedule.wednesday_start_time,
        wednesday_end_time=schedule.wednesday_end_time,
        thursday_enabled=schedule.thursday_enabled,
        thursday_start_time=schedule.thursday_start_time,
        thursday_end_time=schedule.thursday_end_time,
        friday_enabled=schedule.friday_enabled,
        friday_start_time=schedule.friday_start_time,
        friday_end_time=schedule.friday_end_time,
        saturday_enabled=schedule.saturday_enabled,
        saturday_start_time=schedule.saturday_start_time,
        saturday_end_time=schedule.saturday_end_time,
        sunday_enabled=schedule.sunday_enabled,
        sunday_start_time=schedule.sunday_start_time,
        sunday_end_time=schedule.sunday_end_time,
    )


def map_polyclinic_asset_domain_to_db(domain: PolyclinicAssetDomain) -> PolyclinicAsset:
    """Маппинг доменной модели в DB модель"""
    # Преобразуем недельное расписание в JSON
    weekly_schedule_json = map_weekly_schedule_domain_to_dict(domain.weekly_schedule) if domain.weekly_schedule else {}

    return PolyclinicAsset(
        id=domain.id,
        bg_asset_id=domain.bg_asset_id,
        patient_id=domain.patient_id,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        actual_datetime=domain.actual_datetime,
        received_from=domain.received_from,
        is_repeat=domain.is_repeat,
        visit_type=domain.visit_type,
        visit_outcome=domain.visit_outcome,
        schedule_enabled=domain.schedule_enabled,
        schedule_period_start=domain.schedule_period_start,
        schedule_period_end=domain.schedule_period_end,
        weekly_schedule=weekly_schedule_json,
        area=domain.area,
        specialization=domain.specialization,
        specialist=domain.specialist,
        service=domain.service,
        reason_appeal=domain.reason_appeal,
        type_active_visit=domain.type_active_visit,
        note=domain.note,
        status=domain.status,
        delivery_status=domain.delivery_status,
        has_confirm=domain.has_confirm,
        has_files=domain.has_files,
        has_refusal=domain.has_refusal,
        rejection_reason_by=domain.rejection_reason_by,
        rejection_reason=domain.rejection_reason,
    )


def map_polyclinic_asset_db_to_domain(db_asset: PolyclinicAsset) -> PolyclinicAssetDomain:
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

    # Преобразуем недельное расписание из JSON
    weekly_schedule = WeeklySchedule()
    if db_asset.weekly_schedule:
        weekly_schedule = map_weekly_schedule_dict_to_domain(db_asset.weekly_schedule)

    return PolyclinicAssetDomain(
        id=db_asset.id,
        bg_asset_id=db_asset.bg_asset_id,
        patient_id=db_asset.patient_id,
        receive_date=db_asset.receive_date,
        receive_time=db_asset.receive_time,
        actual_datetime=db_asset.actual_datetime,
        received_from=db_asset.received_from,
        is_repeat=db_asset.is_repeat,
        visit_type=db_asset.visit_type,
        visit_outcome=db_asset.visit_outcome,
        schedule_enabled=db_asset.schedule_enabled,
        schedule_period_start=db_asset.schedule_period_start,
        schedule_period_end=db_asset.schedule_period_end,
        weekly_schedule=weekly_schedule,
        area=db_asset.area,
        specialization=db_asset.specialization,
        specialist=db_asset.specialist,
        service=db_asset.service,
        reason_appeal=db_asset.reason_appeal,
        type_active_visit=db_asset.type_active_visit,
        note=db_asset.note,
        status=db_asset.status,
        delivery_status=db_asset.delivery_status,
        has_confirm=db_asset.has_confirm,
        has_files=db_asset.has_files,
        has_refusal=db_asset.has_refusal,
        rejection_reason_by=db_asset.rejection_reason_by,
        rejection_reason=db_asset.rejection_reason,
        created_at=db_asset.created_at,
        updated_at=db_asset.changed_at,
        patient_data=patient_data,
    )


def map_polyclinic_asset_domain_to_full_response(domain: PolyclinicAssetDomain) -> PolyclinicAssetResponseSchema:
    """Маппинг доменной модели в полную схему ответа"""
    weekly_schedule_response = map_weekly_schedule_domain_to_response(
        domain.weekly_schedule) if domain.weekly_schedule else None

    return PolyclinicAssetResponseSchema(
        id=domain.id,
        bg_asset_id=domain.bg_asset_id,
        organization_id=domain.organization_id,
        patient_id=domain.patient_id,
        patient_full_name=domain.patient_full_name,
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        actual_datetime=domain.actual_datetime,
        received_from=domain.received_from,
        is_repeat=domain.is_repeat,
        visit_type=domain.visit_type,
        visit_outcome=domain.visit_outcome,
        schedule_enabled=domain.schedule_enabled,
        schedule_period_start=domain.schedule_period_start,
        schedule_period_end=domain.schedule_period_end,
        weekly_schedule=weekly_schedule_response,
        area=domain.area,
        specialization=domain.specialization,
        specialist=domain.specialist,
        service=domain.service,
        reason_appeal=domain.reason_appeal,
        type_active_visit=domain.type_active_visit,
        note=domain.note,
        status=domain.status,
        delivery_status=domain.delivery_status,
        has_confirm=domain.has_confirm,
        has_files=domain.has_files,
        has_refusal=domain.has_refusal,
        rejection_reason_by=domain.rejection_reason_by,
        rejection_reason=domain.rejection_reason,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
        organization_data=domain.organization_data,
        patient_data=domain.patient_data,
    )


def map_polyclinic_asset_domain_to_list_item(domain: PolyclinicAssetDomain) -> PolyclinicAssetListItemSchema:
    """Маппинг доменной модели в схему для списка"""
    # Получаем данные организации если они загружены
    organization_name = None
    if domain.organization_data:
        organization_name = domain.organization_data.get('name')

    return PolyclinicAssetListItemSchema(
        id=domain.id,
        organization_id=domain.organization_id,
        organization_name=organization_name,
        patient_id=domain.patient_id,
        patient_full_name=domain.patient_full_name,
        patient_iin=domain.patient_iin,
        patient_birth_date=domain.patient_birth_date,
        area=domain.area,
        specialization=domain.specialization,
        specialist=domain.specialist,
        service=domain.service,
        reason_appeal=domain.reason_appeal,
        type_active_visit=domain.type_active_visit,
        visit_type=domain.visit_type,
        status=domain.status,
        delivery_status=domain.delivery_status,
        receive_date=domain.receive_date,
        receive_time=domain.receive_time,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
    )


def map_create_schema_to_domain(create_schema: CreatePolyclinicAssetSchema, patient_id: UUID) -> PolyclinicAssetDomain:
    """Маппинг схемы создания в доменную модель"""

    # Преобразуем недельное расписание
    weekly_schedule = WeeklySchedule()
    if create_schema.weekly_schedule:
        weekly_schedule = map_weekly_schedule_schema_to_domain(create_schema.weekly_schedule)

    return PolyclinicAssetDomain(
        bg_asset_id=create_schema.bg_asset_id,
        patient_id=patient_id,
        receive_date=create_schema.receive_date,
        receive_time=create_schema.receive_time,
        actual_datetime=create_schema.actual_datetime or create_schema.receive_date,
        received_from=create_schema.received_from,
        is_repeat=create_schema.is_repeat,
        visit_type=create_schema.visit_type,
        visit_outcome=create_schema.visit_outcome,
        schedule_enabled=create_schema.schedule_enabled,
        schedule_period_start=create_schema.schedule_period_start,
        schedule_period_end=create_schema.schedule_period_end,
        weekly_schedule=weekly_schedule,
        area=create_schema.area,
        specialization=create_schema.specialization,
        specialist=create_schema.specialist,
        service=create_schema.service,
        reason_appeal=create_schema.reason_appeal,
        type_active_visit=create_schema.type_active_visit,
        note=create_schema.note,
    )


def map_bg_response_to_polyclinic_domain(bg_data: dict, patient_id: UUID) -> PolyclinicAssetDomain:
    """Маппинг ответа BG в доменную модель активов поликлиники"""

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

    # Определяем тип посещения из данных BG
    visit_type = PolyclinicVisitTypeEnum.FIRST_VISIT
    if bg_data.get("visitType"):
        visit_type_mapping = {
            "first": PolyclinicVisitTypeEnum.FIRST_VISIT,
            "repeat": PolyclinicVisitTypeEnum.REPEAT_VISIT,
        }
        visit_type = visit_type_mapping.get(bg_data["visitType"], PolyclinicVisitTypeEnum.FIRST_VISIT)
    return PolyclinicAssetDomain(
        bg_asset_id=bg_data.get("id", ""),
        patient_id=patient_id,
        receive_date=reg_datetime,
        receive_time=reg_time,
        actual_datetime=parse_datetime(bg_data.get("visitDate")) or reg_datetime,
        received_from=bg_data.get("orgHealthCareRequest", {}).get("name", ""),
        is_repeat=bg_data.get("isRepeat", False),
        visit_type=visit_type,
        visit_outcome=None,
        schedule_enabled=False,
        weekly_schedule=WeeklySchedule(),
        area=bg_data.get("area", "Общий"),
        specialization=bg_data.get("specialization", ""),
        specialist=bg_data.get("directDoctor", ""),
        service=bg_data.get("service"),
        reason_appeal=bg_data.get("reasonAppeal", PolyclinicReasonAppeal.PATRONAGE),
        type_active_visit=bg_data.get("typeActiveVisit", PolyclinicTypeActiveVisit.FIRST_APPEAL),
        note=bg_data.get("additionalInformation"),
        has_confirm=bg_data.get("hasConfirm", "false").lower() == "true",
        has_files=bg_data.get("hasFiles", "false").lower() == "true",
        has_refusal=bg_data.get("hasRefusal", "false").lower() == "true",
    )

