from datetime import datetime, time
from typing import Optional, List, Dict, Any
from uuid import UUID

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
    PolyclinicVisitTypeEnum,
    PolyclinicServiceTypeEnum,
    PolyclinicOutcomeEnum,
    WeekdayEnum,
    RejectionReasonByEnum, PolyclinicReasonAppeal, PolyclinicTypeActiveVisit,
)


class WeeklySchedule:
    """Недельное расписание работы поликлиники"""

    def __init__(
            self,
            monday_enabled: bool = False,
            monday_start_time: Optional[time] = None,
            monday_end_time: Optional[time] = None,
            tuesday_enabled: bool = False,
            tuesday_start_time: Optional[time] = None,
            tuesday_end_time: Optional[time] = None,
            wednesday_enabled: bool = False,
            wednesday_start_time: Optional[time] = None,
            wednesday_end_time: Optional[time] = None,
            thursday_enabled: bool = False,
            thursday_start_time: Optional[time] = None,
            thursday_end_time: Optional[time] = None,
            friday_enabled: bool = False,
            friday_start_time: Optional[time] = None,
            friday_end_time: Optional[time] = None,
            saturday_enabled: bool = False,
            saturday_start_time: Optional[time] = None,
            saturday_end_time: Optional[time] = None,
            sunday_enabled: bool = False,
            sunday_start_time: Optional[time] = None,
            sunday_end_time: Optional[time] = None,
    ):
        self.monday_enabled = monday_enabled
        self.monday_start_time = monday_start_time
        self.monday_end_time = monday_end_time
        self.tuesday_enabled = tuesday_enabled
        self.tuesday_start_time = tuesday_start_time
        self.tuesday_end_time = tuesday_end_time
        self.wednesday_enabled = wednesday_enabled
        self.wednesday_start_time = wednesday_start_time
        self.wednesday_end_time = wednesday_end_time
        self.thursday_enabled = thursday_enabled
        self.thursday_start_time = thursday_start_time
        self.thursday_end_time = thursday_end_time
        self.friday_enabled = friday_enabled
        self.friday_start_time = friday_start_time
        self.friday_end_time = friday_end_time
        self.saturday_enabled = saturday_enabled
        self.saturday_start_time = saturday_start_time
        self.saturday_end_time = saturday_end_time
        self.sunday_enabled = sunday_enabled
        self.sunday_start_time = sunday_start_time
        self.sunday_end_time = sunday_end_time

    def get_schedule_for_day(self, weekday: WeekdayEnum) -> Dict[str, Any]:
        """Получить расписание для конкретного дня"""
        day_mapping = {
            WeekdayEnum.MONDAY: ('monday_enabled', 'monday_start_time', 'monday_end_time'),
            WeekdayEnum.TUESDAY: ('tuesday_enabled', 'tuesday_start_time', 'tuesday_end_time'),
            WeekdayEnum.WEDNESDAY: ('wednesday_enabled', 'wednesday_start_time', 'wednesday_end_time'),
            WeekdayEnum.THURSDAY: ('thursday_enabled', 'thursday_start_time', 'thursday_end_time'),
            WeekdayEnum.FRIDAY: ('friday_enabled', 'friday_start_time', 'friday_end_time'),
            WeekdayEnum.SATURDAY: ('saturday_enabled', 'saturday_start_time', 'saturday_end_time'),
            WeekdayEnum.SUNDAY: ('sunday_enabled', 'sunday_start_time', 'sunday_end_time'),
        }

        enabled_attr, start_attr, end_attr = day_mapping[weekday]
        return {
            'enabled': getattr(self, enabled_attr),
            'start_time': getattr(self, start_attr),
            'end_time': getattr(self, end_attr),
        }


class PolyclinicAssetDomain:
    """
    Доменная модель актива поликлиники
    """

    def __init__(
            self,
            *,
            id: Optional[UUID] = None,

            # Данные из BG
            bg_asset_id: Optional[str] = None,

            patient_id: UUID,

            # Данные о получении актива
            receive_date: datetime,
            receive_time: time,
            actual_datetime: datetime,
            received_from: str,
            is_repeat: bool = False,

            # Данные о посещении поликлиники
            visit_type: PolyclinicVisitTypeEnum = PolyclinicVisitTypeEnum.FIRST_VISIT,
            visit_outcome: Optional[PolyclinicOutcomeEnum] = None,

            # Расписание активов
            schedule_enabled: bool = False,
            schedule_period_start: Optional[datetime] = None,
            schedule_period_end: Optional[datetime] = None,
            weekly_schedule: Optional[WeeklySchedule] = None,

            # Участок и специалист
            area: str,
            specialization: str,
            specialist: str,

            service: PolyclinicServiceTypeEnum = PolyclinicServiceTypeEnum.CONSULTATION,
            reason_appeal: PolyclinicReasonAppeal = PolyclinicReasonAppeal.PATRONAGE,
            type_active_visit: PolyclinicTypeActiveVisit = PolyclinicTypeActiveVisit.FIRST_APPEAL,

            # Примечание
            note: Optional[str] = None,

            # Статусы
            status: AssetStatusEnum = AssetStatusEnum.REGISTERED,
            delivery_status: AssetDeliveryStatusEnum = AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY,

            # Флаги для совместимости с BG
            has_confirm: bool = False,
            has_files: bool = False,
            has_refusal: bool = False,

            # Данные об отклонении
            rejection_reason_by: Optional[RejectionReasonByEnum] = None,
            rejection_reason: Optional[str] = None,

            # Метаданные
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,

            # Связанные данные
            patient_data: Optional[dict] = None,
    ):
        self.id = id
        self.bg_asset_id = bg_asset_id
        self.patient_id = patient_id
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.actual_datetime = actual_datetime
        self.received_from = received_from
        self.is_repeat = is_repeat
        self.visit_type = visit_type
        self.visit_outcome = visit_outcome
        self.schedule_enabled = schedule_enabled
        self.schedule_period_start = schedule_period_start
        self.schedule_period_end = schedule_period_end
        self.weekly_schedule = weekly_schedule or WeeklySchedule()
        self.area = area
        self.specialization = specialization
        self.specialist = specialist
        self.service = service
        self.reason_appeal = reason_appeal
        self.type_active_visit = type_active_visit
        self.note = note
        self.status = status
        self.delivery_status = delivery_status
        self.has_confirm = has_confirm
        self.has_files = has_files
        self.has_refusal = has_refusal
        self.rejection_reason_by = rejection_reason_by
        self.rejection_reason = rejection_reason
        self.created_at = created_at
        self.updated_at = updated_at

        self.patient_data = patient_data

    def update_status(self, new_status: AssetStatusEnum) -> None:
        """Обновить статус актива"""
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def update_delivery_status(self, new_delivery_status: AssetDeliveryStatusEnum) -> None:
        """Обновить статус доставки"""
        self.delivery_status = new_delivery_status
        self.updated_at = datetime.utcnow()

    def add_note(self, note: str) -> None:
        """Добавить примечание"""
        self.note = note
        self.updated_at = datetime.utcnow()

    def update_visit_outcome(self, outcome: PolyclinicOutcomeEnum) -> None:
        """Обновить исход посещения"""
        self.visit_outcome = outcome
        self.updated_at = datetime.utcnow()

    def confirm_asset(self) -> None:
        """Подтвердить актив"""
        self.has_confirm = True
        self.status = AssetStatusEnum.CONFIRMED
        self.updated_at = datetime.utcnow()

    def refuse_asset(self, reason: str, refused_by: RejectionReasonByEnum) -> None:
        """Отказать в активе"""
        self.has_refusal = True
        self.status = AssetStatusEnum.REFUSED
        self.rejection_reason = reason
        self.rejection_reason_by = refused_by
        current_note = self.note or ""
        self.note = f"Отказ: {reason}" + (f"\n{current_note}" if current_note else "")
        self.updated_at = datetime.utcnow()

    def enable_schedule(self, period_start: datetime, period_end: datetime, schedule: WeeklySchedule) -> None:
        """Включить планирование активов"""
        self.schedule_enabled = True
        self.schedule_period_start = period_start
        self.schedule_period_end = period_end
        self.weekly_schedule = schedule
        self.updated_at = datetime.utcnow()

    def disable_schedule(self) -> None:
        """Отключить планирование активов"""
        self.schedule_enabled = False
        self.schedule_period_start = None
        self.schedule_period_end = None
        self.weekly_schedule = WeeklySchedule()  # Сброс расписания
        self.updated_at = datetime.utcnow()

    @property
    def is_confirmed(self) -> bool:
        """Проверить, подтвержден ли актив"""
        return self.has_confirm

    @property
    def is_refused(self) -> bool:
        """Проверить, отказан ли актив"""
        return self.has_refusal

    @property
    def receive_datetime(self) -> datetime:
        """Объединенная дата и время получения"""
        return self.actual_datetime or datetime.combine(self.receive_date.date(), self.receive_time)

    @property
    def patient_full_name(self) -> Optional[str]:
        """Получить ФИО пациента из связанных данных"""
        if self.patient_data:
            return f"{self.patient_data.get('last_name', '')} {self.patient_data.get('first_name', '')} {self.patient_data.get('middle_name', '') or ''}".strip()
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
    def patient_area_number(self) -> Optional[int]:
        """Получить номер участка пациента из attachment_data"""
        if self.patient_data and self.patient_data.get('attachment_data'):
            return self.patient_data['attachment_data'].get('area_number')
        return None

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            AssetStatusEnum.REGISTERED: "Зарегистрирован",
            AssetStatusEnum.CONFIRMED: "Подтвержден",
            AssetStatusEnum.REFUSED: "Отказан",
            AssetStatusEnum.CANCELLED: "Отменен",
        }
        return status_map.get(self.status, "Неизвестно")

    def _get_delivery_status_display(self) -> str:
        """Получить отображаемое название статуса доставки"""
        status_map = {
            AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY: "Получен автоматически",
            AssetDeliveryStatusEnum.PENDING_DELIVERY: "Ожидает доставки",
            AssetDeliveryStatusEnum.DELIVERED: "Доставлен",
        }
        return status_map.get(self.delivery_status, "Неизвестно")

    def _get_visit_type_display(self) -> str:
        """Получить отображаемое название типа посещения"""
        type_map = {
            PolyclinicVisitTypeEnum.FIRST_VISIT: "Первичное обращение",
            PolyclinicVisitTypeEnum.REPEAT_VISIT: "Повторное обращение",
        }
        return type_map.get(self.visit_type, "Неизвестно")

    def _get_type_active_visit_display(self) -> str:
        """Получить отображаемое название типа активного посещения"""
        type_map = {
            PolyclinicTypeActiveVisit.FIRST_APPEAL: "Первичное обращение",
            PolyclinicTypeActiveVisit.REPEAT_APPEAL: "Повторное обращение",
            PolyclinicTypeActiveVisit.EMERGENCY_APPEAL: "Экстренное обращение",
            PolyclinicTypeActiveVisit.PLANNED_APPEAL: "Плановое обращение",
        }
        return type_map.get(self.type_active_visit, "Неизвестно")


class PolyclinicAssetListItemDomain:
    """
    Доменная модель для списка активов поликлиники
    """

    def __init__(
            self,
            id: UUID,
            patient_id: UUID,
            patient_full_name: str,
            patient_iin: str,
            patient_birth_date: datetime,
            area: str,
            specialization: str,
            specialist: str,
            service: Optional[str],
            visit_type: PolyclinicVisitTypeEnum,
            type_active_visit: PolyclinicTypeActiveVisit,
            reason_appeal: PolyclinicReasonAppeal,
            status: AssetStatusEnum,
            delivery_status: AssetDeliveryStatusEnum,
            receive_date: datetime,
            receive_time: time,
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
        self.area = area
        self.specialization = specialization
        self.specialist = specialist
        self.service = service
        self.visit_type = visit_type
        self.type_active_visit = type_active_visit
        self.reason_appeal = reason_appeal
        self.status = status
        self.delivery_status = delivery_status
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.created_at = created_at
        self.updated_at = updated_at
        self.organization_id = organization_id
        self.organization_name = organization_name