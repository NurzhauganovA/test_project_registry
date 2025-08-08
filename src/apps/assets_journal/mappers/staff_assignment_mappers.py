from datetime import datetime

from src.apps.assets_journal.domain.models.staff_assignment import StaffAssignmentDomain, StaffAssignmentListItemDomain
from src.apps.assets_journal.infrastructure.db_models.staff_assignment import StaffAssignment
from src.apps.assets_journal.infrastructure.api.schemas.responses.staff_assignment_schemas import (
    StaffAssignmentResponseSchema,
    StaffAssignmentListItemSchema,
)


def map_staff_assignment_domain_to_db(domain: StaffAssignmentDomain) -> StaffAssignment:
    """Маппинг доменной модели в DB модель"""
    return StaffAssignment(
        id=domain.id,
        specialist_name=domain.specialist_name,
        specialization=domain.specialization,
        area_number=domain.area_number,
        area_type=domain.area_type,
        department=domain.department,
        start_date=domain.start_date,
        end_date=domain.end_date,
        reception_hours_per_day=domain.reception_hours_per_day,
        reception_minutes_per_day=domain.reception_minutes_per_day,
        area_hours_per_day=domain.area_hours_per_day,
        area_minutes_per_day=domain.area_minutes_per_day,
        status=domain.status,
        notes=domain.notes,
    )


def map_staff_assignment_db_to_domain(db_assignment: StaffAssignment) -> StaffAssignmentDomain:
    """Маппинг DB модели в доменную модель"""
    return StaffAssignmentDomain(
        id=db_assignment.id,
        specialist_name=db_assignment.specialist_name,
        specialization=db_assignment.specialization,
        area_number=db_assignment.area_number,
        area_type=db_assignment.area_type,
        department=db_assignment.department,
        start_date=db_assignment.start_date,
        end_date=db_assignment.end_date,
        reception_hours_per_day=db_assignment.reception_hours_per_day,
        reception_minutes_per_day=db_assignment.reception_minutes_per_day,
        area_hours_per_day=db_assignment.area_hours_per_day,
        area_minutes_per_day=db_assignment.area_minutes_per_day,
        status=db_assignment.status,
        notes=db_assignment.notes,
        created_at=db_assignment.created_at,
        updated_at=db_assignment.changed_at,
    )


def map_staff_assignment_db_to_list_item(db_assignment: StaffAssignment) -> StaffAssignmentListItemDomain:
    """Маппинг DB модели в доменную модель для списка"""

    # Форматируем время
    reception_time_formatted = f"{db_assignment.reception_hours_per_day:02d}:{db_assignment.reception_minutes_per_day:02d}"
    area_time_formatted = f"{db_assignment.area_hours_per_day:02d}:{db_assignment.area_minutes_per_day:02d}"

    return StaffAssignmentListItemDomain(
        id=db_assignment.id,
        specialist_name=db_assignment.specialist_name,
        specialization=db_assignment.specialization,
        area_number=db_assignment.area_number,
        area_type=db_assignment.area_type,
        department=db_assignment.department,
        start_date=db_assignment.start_date,
        end_date=db_assignment.end_date,
        status=db_assignment.status,
        reception_time_formatted=reception_time_formatted,
        area_time_formatted=area_time_formatted,
        created_at=db_assignment.created_at,
        updated_at=db_assignment.changed_at,
    )


def map_staff_assignment_domain_to_full_response(domain: StaffAssignmentDomain) -> StaffAssignmentResponseSchema:
    """Маппинг доменной модели в полную схему ответа"""
    return StaffAssignmentResponseSchema(
        id=domain.id,
        specialist_name=domain.specialist_name,
        specialization=domain.specialization,
        area_number=domain.area_number,
        area_type=domain.area_type,
        department=domain.department,
        start_date=domain.start_date,
        end_date=domain.end_date,
        reception_hours_per_day=domain.reception_hours_per_day,
        reception_minutes_per_day=domain.reception_minutes_per_day,
        area_hours_per_day=domain.area_hours_per_day,
        area_minutes_per_day=domain.area_minutes_per_day,
        reception_time_formatted=domain.reception_time_formatted,
        area_time_formatted=domain.area_time_formatted,
        total_work_minutes_per_day=domain.total_work_minutes_per_day,
        status=domain.status,
        notes=domain.notes,
        is_active=domain.is_active,
        is_current=domain.is_current,
        days_assigned=domain.days_assigned,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
    )


def map_staff_assignment_domain_to_list_item(domain: StaffAssignmentDomain) -> StaffAssignmentListItemSchema:
    """Маппинг доменной модели в схему для списка"""
    return StaffAssignmentListItemSchema(
        id=domain.id,
        specialist_name=domain.specialist_name,
        specialization=domain.specialization,
        area_number=domain.area_number,
        department=domain.department,
        start_date=domain.start_date,
        end_date=domain.end_date,
        status=domain.status,
        reception_time_formatted=domain.reception_time_formatted,
        area_time_formatted=domain.area_time_formatted,
        created_at=domain.created_at or datetime.now(),
        updated_at=domain.updated_at or datetime.now(),
    )


def map_create_schema_to_domain(create_schema) -> StaffAssignmentDomain:
    """Маппинг схемы создания в доменную модель"""
    return StaffAssignmentDomain(
        specialist_name=create_schema.specialist_name,
        specialization=create_schema.specialization,
        area_number=create_schema.area_number,
        area_type=create_schema.area_type,
        department=create_schema.department,
        start_date=create_schema.start_date,
        end_date=create_schema.end_date,
        reception_hours_per_day=create_schema.reception_hours_per_day,
        reception_minutes_per_day=create_schema.reception_minutes_per_day,
        area_hours_per_day=create_schema.area_hours_per_day,
        area_minutes_per_day=create_schema.area_minutes_per_day,
        notes=create_schema.notes,
    )