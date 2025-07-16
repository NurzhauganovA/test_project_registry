from datetime import datetime, time
from typing import Optional, List, Dict, Any
from uuid import UUID

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
    EmergencyOutcomeEnum,
    DiagnosisTypeEnum,
)


class EmergencyDiagnosis:
    """Доменная модель диагноза для скорой помощи"""

    def __init__(
            self,
            diagnosis_type: DiagnosisTypeEnum,
            diagnosis_code: str,
            diagnosis_name: str,
            note: Optional[str] = None,
    ):
        self.diagnosis_type = diagnosis_type
        self.diagnosis_code = diagnosis_code
        self.diagnosis_name = diagnosis_name
        self.note = note


class EmergencyAssetDomain:
    """
    Доменная модель актива скорой помощи
    """

    def __init__(
            self,
            *,
            id: Optional[UUID] = None,

            # Данные из BG
            bg_asset_id: Optional[str] = None,

            # Данные о пациенте
            patient_id: UUID,
            patient_location_address: Optional[str] = None,
            is_not_attached_to_mo: bool = False,

            # Данные о получении актива
            receive_date: datetime,
            receive_time: time,
            actual_datetime: datetime,
            received_from: str,
            is_repeat: bool = False,

            # Исход обращения
            outcome: Optional[EmergencyOutcomeEnum] = None,

            # Диагнозы
            diagnoses: Optional[List[EmergencyDiagnosis]] = None,

            # Примечание к диагнозу
            diagnosis_note: Optional[str] = None,

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
        self.patient_id = patient_id
        self.patient_location_address = patient_location_address
        self.is_not_attached_to_mo = is_not_attached_to_mo
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.actual_datetime = actual_datetime
        self.received_from = received_from
        self.is_repeat = is_repeat
        self.outcome = outcome
        self.diagnoses = diagnoses or []
        self.diagnosis_note = diagnosis_note
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

    def add_diagnosis(self, diagnosis: EmergencyDiagnosis) -> None:
        """Добавить диагноз"""
        self.diagnoses.append(diagnosis)
        self.updated_at = datetime.utcnow()

    def remove_diagnosis(self, diagnosis_code: str, diagnosis_type: DiagnosisTypeEnum) -> None:
        """Удалить диагноз"""
        self.diagnoses = [
            d for d in self.diagnoses
            if not (d.diagnosis_code == diagnosis_code and d.diagnosis_type == diagnosis_type)
        ]
        self.updated_at = datetime.utcnow()

    def update_outcome(self, outcome: EmergencyOutcomeEnum) -> None:
        """Обновить исход обращения"""
        self.outcome = outcome
        self.updated_at = datetime.utcnow()

    def add_diagnosis_note(self, note: str) -> None:
        """Добавить примечание к диагнозу"""
        current_note = self.diagnosis_note or ""
        self.diagnosis_note = f"{note}\n{current_note}" if current_note else note
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
        current_note = self.diagnosis_note or ""
        self.diagnosis_note = f"Отказ: {reason}" + (f"\n{current_note}" if current_note else "")
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
    def primary_diagnosis(self) -> Optional[EmergencyDiagnosis]:
        """Получить основной диагноз"""
        for diagnosis in self.diagnoses:
            if diagnosis.diagnosis_type == DiagnosisTypeEnum.PRIMARY:
                return diagnosis
        return None

    @property
    def secondary_diagnoses(self) -> List[EmergencyDiagnosis]:
        """Получить сопутствующие диагнозы"""
        return [d for d in self.diagnoses if d.diagnosis_type == DiagnosisTypeEnum.SECONDARY]

    @property
    def diagnoses_summary(self) -> str:
        """Получить сводку диагнозов для отображения"""
        if not self.diagnoses:
            return "Диагнозы не указаны"

        primary = self.primary_diagnosis
        if primary:
            return f"{primary.diagnosis_code} - {primary.diagnosis_name}"
        elif self.diagnoses:
            first_diagnosis = self.diagnoses[0]
            return f"{first_diagnosis.diagnosis_code} - {first_diagnosis.diagnosis_name}"
        return "Диагнозы не указаны"

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

    def _get_outcome_display(self) -> str:
        """Получить отображаемое название исхода"""
        outcome_map = {
            EmergencyOutcomeEnum.HOSPITALIZED: "Госпитализирован",
            EmergencyOutcomeEnum.TREATED_AT_HOME: "Лечение на дому",
            EmergencyOutcomeEnum.REFUSED_TREATMENT: "Отказ от лечения",
            EmergencyOutcomeEnum.DEATH: "Смерть",
            EmergencyOutcomeEnum.TRANSFERRED: "Передан другой службе",
        }
        return outcome_map.get(self.outcome, "Не указан") if self.outcome else "Не указан"


class EmergencyAssetListItemDomain:
    """
    Доменная модель для списка активов скорой помощи
    """

    def __init__(
            self,
            id: UUID,
            patient_id: UUID,
            patient_full_name: str,
            patient_iin: str,
            patient_birth_date: datetime,
            diagnoses_summary: str,
            outcome: Optional[EmergencyOutcomeEnum],
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
        self.diagnoses_summary = diagnoses_summary
        self.outcome = outcome
        self.status = status
        self.delivery_status = delivery_status
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.created_at = created_at
        self.updated_at = updated_at
        self.organization_id = organization_id
        self.organization_name = organization_name