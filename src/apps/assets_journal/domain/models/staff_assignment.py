# src/apps/assets_journal/domain/models/staff_assignment.py

from datetime import datetime, date, time
from typing import Optional
from uuid import UUID

from src.apps.assets_journal.domain.enums import (
    StaffAssignmentStatusEnum,
    MedicalSpecializationEnum,
    MedicalDepartmentEnum,
    AreaTypeEnum,
)


class StaffAssignmentDomain:
    """
    Доменная модель назначения медперсонала на участок
    """

    def __init__(
            self,
            *,
            id: Optional[UUID] = None,

            # Данные специалиста
            specialist_name: str,  # ФИО специалиста
            specialization: MedicalSpecializationEnum,  # Специализация

            # Назначение
            area_number: str,  # Номер участка
            area_type: AreaTypeEnum,  # Тип участка
            department: MedicalDepartmentEnum,  # Отделение

            # Период работы
            start_date: date,  # Дата начала
            end_date: Optional[date] = None,  # Дата окончания

            # Время работы
            reception_hours_per_day: Optional[int] = None,  # Часов на приёме в день
            reception_minutes_per_day: Optional[int] = None,  # Минут на приёме в день
            area_hours_per_day: Optional[int] = None,  # Часов на участке в день
            area_minutes_per_day: Optional[int] = None,  # Минут на участке в день

            # Статус
            status: StaffAssignmentStatusEnum = StaffAssignmentStatusEnum.ACTIVE,

            # Дополнительная информация
            notes: Optional[str] = None,  # Примечания

            # Метаданные
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.specialist_name = specialist_name
        self.specialization = specialization
        self.area_number = area_number
        self.area_type = area_type
        self.department = department
        self.start_date = start_date
        self.end_date = end_date
        self.reception_hours_per_day = reception_hours_per_day or 0
        self.reception_minutes_per_day = reception_minutes_per_day or 0
        self.area_hours_per_day = area_hours_per_day or 0
        self.area_minutes_per_day = area_minutes_per_day or 0
        self.status = status
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    def complete_assignment(self, end_date: date, notes: Optional[str] = None) -> None:
        """Завершить назначение"""
        self.status = StaffAssignmentStatusEnum.COMPLETED
        self.end_date = end_date
        if notes:
            self.add_note(notes)
        self.updated_at = datetime.utcnow()

    def suspend_assignment(self, reason: Optional[str] = None) -> None:
        """Приостановить назначение"""
        self.status = StaffAssignmentStatusEnum.SUSPENDED
        if reason:
            self.add_note(f"Приостановлен: {reason}")
        self.updated_at = datetime.utcnow()

    def activate_assignment(self) -> None:
        """Активировать назначение"""
        self.status = StaffAssignmentStatusEnum.ACTIVE
        self.updated_at = datetime.utcnow()

    def deactivate_assignment(self, reason: Optional[str] = None) -> None:
        """Деактивировать назначение"""
        self.status = StaffAssignmentStatusEnum.INACTIVE
        if reason:
            self.add_note(f"Деактивирован: {reason}")
        self.updated_at = datetime.utcnow()

    def add_note(self, note: str) -> None:
        """Добавить примечание"""
        if self.notes:
            self.notes = f"{self.notes}\n{note}"
        else:
            self.notes = note
        self.updated_at = datetime.utcnow()

    def extend_assignment(self, new_end_date: date, reason: Optional[str] = None) -> None:
        """Продлить назначение"""
        self.end_date = new_end_date
        if reason:
            self.add_note(f"Продлен до {new_end_date}: {reason}")
        self.updated_at = datetime.utcnow()

    @property
    def is_active(self) -> bool:
        """Проверить, активно ли назначение"""
        return self.status == StaffAssignmentStatusEnum.ACTIVE

    @property
    def is_current(self) -> bool:
        """Проверить, является ли назначение текущим (активным на сегодня)"""
        today = date.today()
        if self.status != StaffAssignmentStatusEnum.ACTIVE:
            return False
        if self.start_date > today:
            return False
        if self.end_date and self.end_date < today:
            return False
        return True

    @property
    def days_assigned(self) -> Optional[int]:
        """Количество дней назначения"""
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        else:
            # Если назначение без окончания, считаем от начала до сегодня
            return (date.today() - self.start_date).days + 1

    @property
    def total_reception_minutes_per_day(self) -> int:
        """Общее время на приёме в минутах за день"""
        return (self.reception_hours_per_day * 60) + self.reception_minutes_per_day

    @property
    def total_area_minutes_per_day(self) -> int:
        """Общее время на участке в минутах за день"""
        return (self.area_hours_per_day * 60) + self.area_minutes_per_day

    @property
    def total_work_minutes_per_day(self) -> int:
        """Общее время работы в минутах за день"""
        return self.total_reception_minutes_per_day + self.total_area_minutes_per_day

    @property
    def reception_time_formatted(self) -> str:
        """Форматированное время на приёме"""
        if self.reception_hours_per_day or self.reception_minutes_per_day:
            return f"{self.reception_hours_per_day:02d}:{self.reception_minutes_per_day:02d}"
        return "00:00"

    @property
    def area_time_formatted(self) -> str:
        """Форматированное время на участке"""
        if self.area_hours_per_day or self.area_minutes_per_day:
            return f"{self.area_hours_per_day:02d}:{self.area_minutes_per_day:02d}"
        return "00:00"

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            StaffAssignmentStatusEnum.ACTIVE: "Активен",
            StaffAssignmentStatusEnum.INACTIVE: "Неактивен",
            StaffAssignmentStatusEnum.SUSPENDED: "Приостановлен",
            StaffAssignmentStatusEnum.COMPLETED: "Завершен",
        }
        return status_map.get(self.status, "Неизвестно")

    def _get_specialization_display(self) -> str:
        """Получить отображаемое название специализации"""
        specialization_map = {
            MedicalSpecializationEnum.THERAPIST: "Терапевт",
            MedicalSpecializationEnum.PEDIATRICIAN: "Педиатр",
            MedicalSpecializationEnum.CARDIOLOGIST: "Кардиолог",
            MedicalSpecializationEnum.NEUROLOGIST: "Невролог",
            MedicalSpecializationEnum.SURGEON: "Хирург",
            MedicalSpecializationEnum.GYNECOLOGIST: "Гинеколог",
            MedicalSpecializationEnum.UROLOGIST: "Уролог",
            MedicalSpecializationEnum.DERMATOLOGIST: "Дерматолог",
            MedicalSpecializationEnum.OPHTHALMOLOGIST: "Офтальмолог",
            MedicalSpecializationEnum.OTOLARYNGOLOGIST: "ЛОР",
            MedicalSpecializationEnum.PSYCHIATRIST: "Психиатр",
            MedicalSpecializationEnum.PSYCHOLOGIST: "Психолог",
            MedicalSpecializationEnum.PSYCHOTHERAPIST: "Психотерапевт",
            MedicalSpecializationEnum.GENERAL_PRACTITIONER: "Врач общей практики",
            MedicalSpecializationEnum.NURSE: "Медсестра",
            MedicalSpecializationEnum.PARAMEDIC: "Фельдшер",
        }
        return specialization_map.get(self.specialization, "Неизвестно")

    def _get_department_display(self) -> str:
        """Получить отображаемое название отделения"""
        department_map = {
            MedicalDepartmentEnum.THERAPEUTIC: "Терапевтическое",
            MedicalDepartmentEnum.PEDIATRIC: "Педиатрическое",
            MedicalDepartmentEnum.SURGICAL: "Хирургическое",
            MedicalDepartmentEnum.GYNECOLOGICAL: "Гинекологическое",
            MedicalDepartmentEnum.NEUROLOGICAL: "Неврологическое",
            MedicalDepartmentEnum.CARDIOLOGICAL: "Кардиологическое",
            MedicalDepartmentEnum.PSYCHIATRIC: "Психиатрическое",
            MedicalDepartmentEnum.DERMATOLOGICAL: "Дерматологическое",
            MedicalDepartmentEnum.OPHTHALMOLOGICAL: "Офтальмологическое",
            MedicalDepartmentEnum.OTOLARYNGOLOGICAL: "ЛОР",
            MedicalDepartmentEnum.EMERGENCY: "Скорая помощь",
            MedicalDepartmentEnum.OUTPATIENT: "Поликлиническое",
            MedicalDepartmentEnum.GENERAL_PRACTICE: "Общая практика",
        }
        return department_map.get(self.department, "Неизвестно")


class StaffAssignmentListItemDomain:
    """
    Доменная модель для элемента списка назначений медперсонала
    """

    def __init__(
            self,
            id: UUID,
            specialist_name: str,
            specialization: MedicalSpecializationEnum,
            area_number: str,
            area_type: AreaTypeEnum,
            department: MedicalDepartmentEnum,
            start_date: date,
            end_date: Optional[date],
            status: StaffAssignmentStatusEnum,
            reception_time_formatted: str,
            area_time_formatted: str,
            created_at: datetime,
            updated_at: datetime,
    ):
        self.id = id
        self.specialist_name = specialist_name
        self.specialization = specialization
        self.area_number = area_number
        self.area_type = area_type
        self.department = department
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.reception_time_formatted = reception_time_formatted
        self.area_time_formatted = area_time_formatted
        self.created_at = created_at
        self.updated_at = updated_at