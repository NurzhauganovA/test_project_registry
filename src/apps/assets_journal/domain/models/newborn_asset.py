from datetime import datetime, time
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
    DiagnosisTypeEnum,
    DeliveryTypeEnum,
    PregnancyWeekEnum,
    NewbornConditionEnum,
    TransferDestinationEnum,
    MedicalServiceTypeEnum,
)


class NewbornDiagnosis:
    """Доменная модель диагноза для новорожденного"""

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


class MotherData:
    """Данные о матери"""

    def __init__(
            self,
            iin: Optional[str] = None,
            full_name: Optional[str] = None,
            address: Optional[str] = None,
            birth_date: Optional[datetime] = None,
            birth_time: Optional[time] = None,
            delivery_type: Optional[DeliveryTypeEnum] = None,
            pregnancy_weeks: Optional[PregnancyWeekEnum] = None,
            discharge_date: Optional[datetime] = None,
            discharge_time: Optional[time] = None,
    ):
        self.iin = iin
        self.full_name = full_name
        self.address = address
        self.birth_date = birth_date
        self.birth_time = birth_time
        self.delivery_type = delivery_type
        self.pregnancy_weeks = pregnancy_weeks
        self.discharge_date = discharge_date
        self.discharge_time = discharge_time


class NewbornData:
    """Данные о новорожденном"""

    def __init__(
            self,
            birth_date: Optional[datetime] = None,
            birth_time: Optional[time] = None,
            weight_grams: Optional[Decimal] = None,  # Вес в граммах
            height_cm: Optional[Decimal] = None,  # Рост в см
            transfer_destination: Optional[TransferDestinationEnum] = None,
            condition: Optional[NewbornConditionEnum] = None,
            medical_services: Optional[List[MedicalServiceTypeEnum]] = None,
    ):
        self.birth_date = birth_date
        self.birth_time = birth_time
        self.weight_grams = weight_grams
        self.height_cm = height_cm
        self.transfer_destination = transfer_destination
        self.condition = condition
        self.medical_services = medical_services or []


class NewbornAssetDomain:
    """
    Доменная модель актива новорожденного
    """

    def __init__(
            self,
            *,
            id: Optional[UUID] = None,

            # Данные из BG
            bg_asset_id: Optional[str] = None,

            patient_id: Optional[UUID],
            patient_full_name_if_not_registered: Optional[str] = None,

            # Данные о получении актива
            receive_date: datetime,
            receive_time: time,
            actual_datetime: datetime,
            received_from: str,
            is_repeat: bool = False,

            # Данные о матери
            mother_data: Optional[MotherData] = None,

            # Данные о новорожденном
            newborn_data: Optional[NewbornData] = None,

            # Диагнозы
            diagnoses: Optional[List[NewbornDiagnosis]] = None,

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
        self.patient_full_name_if_not_registered = patient_full_name_if_not_registered
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.actual_datetime = actual_datetime
        self.received_from = received_from
        self.is_repeat = is_repeat
        self.mother_data = mother_data or MotherData()
        self.newborn_data = newborn_data or NewbornData()
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

    def add_diagnosis(self, diagnosis: NewbornDiagnosis) -> None:
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

    def update_mother_data(self, mother_data: MotherData) -> None:
        """Обновить данные о матери"""
        self.mother_data = mother_data
        self.updated_at = datetime.utcnow()

    def update_newborn_data(self, newborn_data: NewbornData) -> None:
        """Обновить данные о новорожденном"""
        self.newborn_data = newborn_data
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
        """Получить ФИО пациента (новорожденного)"""
        if self.patient_full_name_if_not_registered:
            return self.patient_full_name_if_not_registered

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
        elif self.newborn_data and self.newborn_data.birth_date:
            return self.newborn_data.birth_date
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
    def primary_diagnosis(self) -> Optional[NewbornDiagnosis]:
        """Получить основной диагноз"""
        for diagnosis in self.diagnoses:
            if diagnosis.diagnosis_type == DiagnosisTypeEnum.PRIMARY:
                return diagnosis
        return None

    @property
    def secondary_diagnoses(self) -> List[NewbornDiagnosis]:
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

    @property
    def newborn_summary(self) -> str:
        """Краткое описание новорожденного для списка"""
        if not self.newborn_data:
            return "Данные не указаны"

        parts = []
        if self.newborn_data.weight_grams:
            parts.append(f"{self.newborn_data.weight_grams}г")
        if self.newborn_data.height_cm:
            parts.append(f"{self.newborn_data.height_cm}см")
        if self.newborn_data.condition:
            parts.append(self._get_condition_display())

        return " / ".join(parts) if parts else "Данные не указаны"

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

    def _get_condition_display(self) -> str:
        """Получить отображаемое название состояния новорожденного"""
        if not self.newborn_data or not self.newborn_data.condition:
            return "Не указано"

        condition_map = {
            NewbornConditionEnum.EXCELLENT: "Отличное",
            NewbornConditionEnum.GOOD: "Хорошее",
            NewbornConditionEnum.SATISFACTORY: "Удовлетворительное",
            NewbornConditionEnum.SEVERE: "Тяжелое",
            NewbornConditionEnum.CRITICAL: "Критическое",
        }
        return condition_map.get(self.newborn_data.condition, "Не указано")


class NewbornAssetListItemDomain:
    """
    Доменная модель для списка активов новорожденных
    """

    def __init__(
            self,
            id: UUID,
            patient_id: Optional[UUID],
            patient_full_name: str,
            patient_iin: Optional[str],
            patient_birth_date: Optional[datetime],
            mother_full_name: Optional[str],
            newborn_summary: str,
            diagnoses_summary: str,
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
        self.mother_full_name = mother_full_name
        self.newborn_summary = newborn_summary
        self.diagnoses_summary = diagnoses_summary
        self.status = status
        self.delivery_status = delivery_status
        self.receive_date = receive_date
        self.receive_time = receive_time
        self.created_at = created_at
        self.updated_at = updated_at
        self.organization_id = organization_id
        self.organization_name = organization_name