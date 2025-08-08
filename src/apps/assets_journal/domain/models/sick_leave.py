from datetime import datetime, date, time
from typing import Optional
from uuid import UUID

from src.apps.assets_journal.domain.enums import (
    SickLeaveStatusEnum,
    SickLeaveTypeEnum,
    WorkCapacityEnum,
    SickLeaveReasonEnum,
)


class SickLeaveDomain:
    """
    Доменная модель больничного листа
    """

    def __init__(
            self,
            *,
            id: Optional[UUID] = None,

            # Связь с пациентом
            patient_id: UUID,
            patient_location_address: Optional[str] = None,  # Адрес проживания пациента

            # Данные о получении
            receive_date: datetime,
            receive_time: time,
            actual_datetime: datetime,
            received_from: str,
            is_repeat: bool = False,

            workplace_name: Optional[str] = None,  # Наименование места работы

            # Период нетрудоспособности
            disability_start_date: date,  # Начало нетрудоспособности
            disability_end_date: Optional[date] = None,  # Окончание нетрудоспособности

            # Медицинские данные
            status: SickLeaveStatusEnum = SickLeaveStatusEnum.OPEN, # Статус больничного листа
            sick_leave_reason: Optional[SickLeaveReasonEnum] = None, # Причина выдачи больничного листа
            work_capacity: WorkCapacityEnum = WorkCapacityEnum.TEMPORARILY_DISABLED, # Трудоспособность

            # Участок и специалист
            area: str,
            specialization: str,
            specialist: str,

            # Дополнительная информация
            notes: Optional[str] = None,  # Примечания
            is_primary: bool = True,  # Первичный или продление
            parent_sick_leave_id: Optional[UUID] = None,  # Ссылка на родительский больничный (для продлений)

            # Метаданные
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,

            # Связанные данные
            patient_data: Optional[dict] = None,
    ):
        self.id = id
        self.patient_id = patient_id
        self.patient_location_address = patient_location_address
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.actual_datetime = actual_datetime
        self.received_from = received_from
        self.is_repeat = is_repeat
        self.disability_start_date = disability_start_date
        self.disability_end_date = disability_end_date
        self.sick_leave_reason = sick_leave_reason
        self.work_capacity = work_capacity
        self.area = area
        self.specialization = specialization
        self.specialist = specialist
        self.workplace_name = workplace_name
        self.notes = notes
        self.is_primary = is_primary
        self.parent_sick_leave_id = parent_sick_leave_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.patient_data = patient_data

    def close_sick_leave(self, end_date: date) -> None:
        """Закрыть больничный лист"""
        self.disability_end_date = end_date
        self.status = SickLeaveStatusEnum.CLOSED
        self.updated_at = datetime.utcnow()

    def extend_sick_leave(self, new_end_date: date) -> None:
        """Продлить больничный лист"""
        self.disability_end_date = new_end_date
        self.status = SickLeaveStatusEnum.EXTENSION
        self.updated_at = datetime.utcnow()

    def cancel_sick_leave(self, reason: Optional[str] = None) -> None:
        """Отменить больничный лист"""
        self.status = SickLeaveStatusEnum.CANCELLED
        if reason and self.notes:
            self.notes = f"Отменен: {reason}\n{self.notes}"
        elif reason:
            self.notes = f"Отменен: {reason}"
        self.updated_at = datetime.utcnow()

    def add_note(self, note: str) -> None:
        """Добавить примечание"""
        if self.notes:
            self.notes = f"{self.notes}\n{note}"
        else:
            self.notes = note
        self.updated_at = datetime.utcnow()

    @property
    def patient_full_name(self) -> Optional[str]:
        """Получить ФИО пациента из связанных данных"""
        if self.patient_data:
            last_name = self.patient_data.get('last_name', '')
            first_name = self.patient_data.get('first_name', '')
            middle_name = self.patient_data.get('middle_name', '') or ''
            return f"{last_name} {first_name} {middle_name}".strip()
        return None

    @property
    def patient_iin(self) -> Optional[str]:
        """Получить ИИН пациента из связанных данных"""
        if self.patient_data:
            return self.patient_data.get('iin')
        return None

    @property
    def patient_birth_date(self) -> Optional[datetime]:
        """Получить дату рождения пациента из связанных данных"""
        if self.patient_data:
            return self.patient_data.get('date_of_birth')
        return None

    @property
    def organization_id(self) -> Optional[int]:
        """Получить ID организации из attachment_data пациента"""
        if self.patient_data and self.patient_data.get('attachment_data'):
            return self.patient_data['attachment_data'].get('attached_clinic_id')
        return None

    @property
    def organization_data(self) -> Optional[dict]:
        """Получить данные организации (будут загружаться отдельно)"""
        return getattr(self, '_organization_data', None)

    @organization_data.setter
    def organization_data(self, value: dict):
        """Установить данные организации"""
        self._organization_data = value

    @property
    def duration_days(self) -> Optional[int]:
        """Получить продолжительность больничного в днях"""
        if self.disability_end_date:
            return (self.disability_end_date - self.disability_start_date).days + 1
        return None

    @property
    def is_active(self) -> bool:
        """Проверить, активен ли больничный лист"""
        return self.status == SickLeaveStatusEnum.OPEN

    @property
    def is_expired(self) -> bool:
        """Проверить, истек ли больничный лист"""
        if self.disability_end_date:
            return self.disability_end_date < date.today()
        return False

    @property
    def receive_datetime(self) -> datetime:
        """Объединенная дата и время получения"""
        return self.actual_datetime or datetime.combine(self.receive_date.date(), self.receive_time)

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            SickLeaveStatusEnum.OPEN: "Открыт",
            SickLeaveStatusEnum.CLOSED: "Закрыт",
            SickLeaveStatusEnum.CANCELLED: "Отменен",
            SickLeaveStatusEnum.EXTENSION: "Продление",
        }
        return status_map.get(self.status, "Неизвестно")


class SickLeaveListItemDomain:
    """
    Доменная модель для элемента списка больничных листов
    """

    def __init__(
            self,
            id: UUID,
            patient_id: UUID,
            patient_full_name: str,
            patient_iin: str,
            patient_birth_date: datetime,
            disability_start_date: date,
            disability_end_date: Optional[date],
            specialist: str,
            specialization: str,
            area: str,
            status: SickLeaveStatusEnum,
            duration_days: Optional[int],
            created_at: datetime,
            updated_at: datetime,
            organization_id: Optional[int] = None,
            organization_name: Optional[str] = None,
    ):
        self.id = id
        self.patient_id = patient_id
        self.patient_full_name = patient_full_name
        self.patient_iin = patient_iin
        self.patient_birth_date = patient_birth_date
        self.disability_start_date = disability_start_date
        self.disability_end_date = disability_end_date
        self.specialist = specialist
        self.specialization = specialization
        self.area = area
        self.status = status
        self.duration_days = duration_days
        self.created_at = created_at
        self.updated_at = updated_at
        self.organization_id = organization_id
        self.organization_name = organization_name