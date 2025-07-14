from datetime import datetime, time
from typing import Optional
from uuid import UUID

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)


class StationaryAssetDomain:
    """
    Доменная модель актива стационара
    """

    def __init__(
            self,
            *,
            id: Optional[UUID] = None,

            # Данные из BG
            bg_asset_id: Optional[str] = None,
            card_number: Optional[str] = None,

            # Данные о пациенте
            patient_id: UUID,

            # Данные о получении актива
            receive_date: datetime,
            receive_time: time,
            actual_datetime: datetime,
            received_from: str,
            is_repeat: bool,

            # Данные пребывания в стационаре
            stay_period_start: datetime,
            stay_period_end: Optional[datetime] = None,
            stay_outcome: Optional[str] = None,
            diagnosis: str,

            # Участок и специалист
            area: str,
            specialization: str,
            specialist: str,

            # Примечание
            note: Optional[str] = None,

            # Статусы
            status: AssetStatusEnum = AssetStatusEnum.REGISTERED,
            delivery_status: AssetDeliveryStatusEnum = AssetDeliveryStatusEnum.RECEIVED_AUTOMATICALLY,

            # Флаги для совместимости с BG
            has_confirm: bool = False,
            has_files: bool = False,
            has_refusal: bool = False,

            # Метаданные
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,

            # Связанные данные
            patient_data: Optional[dict] = None,
    ):
        self.id = id
        self.bg_asset_id = bg_asset_id
        self.card_number = card_number
        self.patient_id = patient_id
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.actual_datetime = actual_datetime
        self.received_from = received_from
        self.is_repeat = is_repeat
        self.stay_period_start = stay_period_start
        self.stay_period_end = stay_period_end
        self.stay_outcome = stay_outcome
        self.diagnosis = diagnosis
        self.area = area
        self.specialization = specialization
        self.specialist = specialist
        self.note = note
        self.status = status
        self.delivery_status = delivery_status
        self.has_confirm = has_confirm
        self.has_files = has_files
        self.has_refusal = has_refusal
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

    def update_diagnosis(self, diagnosis: str) -> None:
        """Обновить диагноз"""
        self.diagnosis = diagnosis
        self.updated_at = datetime.utcnow()

    def update_stay_outcome(self, outcome: str) -> None:
        """Обновить исход лечения"""
        self.stay_outcome = outcome
        self.updated_at = datetime.utcnow()

    def confirm_asset(self) -> None:
        """Подтвердить актив"""
        self.has_confirm = True
        self.status = AssetStatusEnum.CONFIRMED
        self.updated_at = datetime.utcnow()

    def refuse_asset(self, reason: str) -> None:
        """Отказать в активе"""
        self.has_refusal = True
        self.status = AssetStatusEnum.REFUSED
        current_note = self.note or ""
        self.note = f"Отказ: {reason}" + (f"\n{current_note}" if current_note else "")
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
        # Эти данные будут загружаться в сервисе
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


class StationaryAssetListItemDomain:
    """
    Доменная модель для списка активов стационара
    """

    def __init__(
            self,
            id: UUID,
            card_number: Optional[str],
            patient_id: UUID,
            patient_full_name: str,
            patient_iin: str,
            patient_birth_date: datetime,
            diagnosis_name: str,
            specialization: Optional[str],
            specialist: str,
            area: str,
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
        self.card_number = card_number
        self.patient_id = patient_id
        self.patient_full_name = patient_full_name
        self.patient_iin = patient_iin
        self.patient_birth_date = patient_birth_date
        self.diagnosis_name = diagnosis_name
        self.specialization = specialization
        self.specialist = specialist
        self.area = area
        self.status = status
        self.delivery_status = delivery_status
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.created_at = created_at
        self.updated_at = updated_at
        self.organization_id = organization_id
        self.organization_name = organization_name