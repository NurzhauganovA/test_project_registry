from datetime import datetime, date, time
from typing import Optional
from uuid import UUID

from src.apps.assets_journal.domain.enums import (
    HomeCallStatusEnum,
    HomeCallCategoryEnum,
    HomeCallSourceEnum,
    HomeCallReasonEnum,
    HomeCallTypeEnum,
    HomeCallVisitTypeEnum,
)


class HomeCallDomain:
    """
    Доменная модель вызова на дом
    """

    def __init__(
            self,
            *,
            id: Optional[UUID] = None,
            call_number: Optional[str] = None,  # Номер вызова

            # Связь с пациентом
            patient_id: UUID,
            patient_address: Optional[str] = None,  # Адрес пациента
            patient_phone: Optional[str] = None,    # Телефон пациента

            # Данные о регистрации вызова
            registration_date: datetime,             # Дата регистрации
            registration_time: time,                 # Время регистрации
            registration_datetime: datetime,         # Объединенная дата-время регистрации

            # Исполнение вызова
            execution_date: Optional[datetime] = None,  # Дата выполнения
            execution_time: Optional[time] = None,      # Время выполнения

            # Медицинские данные
            area: str,                              # Участок
            specialization: str,                    # Специализация
            specialist: str,                        # Специалист

            # Страхование
            is_insured: bool = False,               # Застрахован
            has_oms: bool = False,                  # ОСМС

            # Данные о вызове
            source: HomeCallSourceEnum,             # Источник вызова
            category: HomeCallCategoryEnum,         # Категория вызова
            reason: HomeCallReasonEnum,             # Повод вызова
            call_type: HomeCallTypeEnum,            # Тип вызова
            reason_patient_words: Optional[str] = None,  # Повод вызова (со слов пациента)
            visit_type: HomeCallVisitTypeEnum = HomeCallVisitTypeEnum.PRIMARY,  # Вид посещения

            # Статус и примечания
            status: HomeCallStatusEnum = HomeCallStatusEnum.REGISTERED,
            notes: Optional[str] = None,            # Примечания

            # Метаданные
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,

            # Связанные данные
            patient_data: Optional[dict] = None,
    ):
        self.id = id
        self.call_number = call_number
        self.patient_id = patient_id
        self.patient_address = patient_address
        self.patient_phone = patient_phone
        self.registration_date = registration_date
        self.registration_time = registration_time
        self.registration_datetime = registration_datetime
        self.execution_date = execution_date
        self.execution_time = execution_time
        self.area = area
        self.specialization = specialization
        self.specialist = specialist
        self.is_insured = is_insured
        self.has_oms = has_oms
        self.source = source
        self.category = category
        self.reason = reason
        self.call_type = call_type
        self.reason_patient_words = reason_patient_words
        self.visit_type = visit_type
        self.status = status
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at
        self.patient_data = patient_data

    def complete_call(self, execution_date: datetime, execution_time: time, notes: Optional[str] = None) -> None:
        """Завершить вызов"""
        self.status = HomeCallStatusEnum.COMPLETED
        self.execution_date = execution_date
        self.execution_time = execution_time
        if notes:
            self.add_note(notes)
        self.updated_at = datetime.utcnow()

    def cancel_call(self, reason: Optional[str] = None) -> None:
        """Отменить вызов"""
        self.status = HomeCallStatusEnum.CANCELLED
        if reason:
            self.add_note(f"Отменен: {reason}")
        self.updated_at = datetime.utcnow()

    def start_processing(self) -> None:
        """Взять вызов в работу"""
        self.status = HomeCallStatusEnum.IN_PROGRESS
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
    def is_active(self) -> bool:
        """Проверить, активен ли вызов"""
        return self.status in [HomeCallStatusEnum.REGISTERED, HomeCallStatusEnum.IN_PROGRESS]

    @property
    def is_completed(self) -> bool:
        """Проверить, выполнен ли вызов"""
        return self.status == HomeCallStatusEnum.COMPLETED

    @property
    def registration_datetime_combined(self) -> datetime:
        """Объединенная дата и время регистрации"""
        return self.registration_datetime or datetime.combine(self.registration_date.date(), self.registration_time)

    @property
    def execution_datetime_combined(self) -> Optional[datetime]:
        """Объединенная дата и время выполнения"""
        if self.execution_date and self.execution_time:
            return datetime.combine(self.execution_date.date(), self.execution_time)
        return None

    def _get_status_display(self) -> str:
        """Получить отображаемое название статуса"""
        status_map = {
            HomeCallStatusEnum.REGISTERED: "Зарегистрирован",
            HomeCallStatusEnum.IN_PROGRESS: "В работе",
            HomeCallStatusEnum.COMPLETED: "Выполнен",
            HomeCallStatusEnum.CANCELLED: "Отменен",
        }
        return status_map.get(self.status, "Неизвестно")

    def _get_category_display(self) -> str:
        """Получить отображаемое название категории"""
        category_map = {
            HomeCallCategoryEnum.EMERGENCY: "Экстренный",
            HomeCallCategoryEnum.URGENT: "Срочный",
            HomeCallCategoryEnum.PLANNED: "Плановый",
        }
        return category_map.get(self.category, "Неизвестно")


class HomeCallListItemDomain:
    """
    Доменная модель для элемента списка вызовов на дом
    """

    def __init__(
            self,
            id: UUID,
            call_number: Optional[str],
            patient_id: UUID,
            patient_full_name: str,
            patient_iin: str,
            patient_birth_date: datetime,
            registration_date: datetime,
            registration_time: time,
            category: HomeCallCategoryEnum,
            status: HomeCallStatusEnum,
            source: HomeCallSourceEnum,
            specialist: str,
            specialization: str,
            area: str,
            created_at: datetime,
            updated_at: datetime,
            organization_id: Optional[int] = None,
            organization_name: Optional[str] = None,
    ):
        self.id = id
        self.call_number = call_number
        self.patient_id = patient_id
        self.patient_full_name = patient_full_name
        self.patient_iin = patient_iin
        self.patient_birth_date = patient_birth_date
        self.registration_date = registration_date
        self.registration_time = registration_time
        self.category = category
        self.status = status
        self.source = source
        self.specialist = specialist
        self.specialization = specialization
        self.area = area
        self.created_at = created_at
        self.updated_at = updated_at
        self.organization_id = organization_id
        self.organization_name = organization_name