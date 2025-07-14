from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Query

from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
)


class StationaryAssetFilterParams:
    """Параметры фильтрации активов стационара"""

    def __init__(
            self,
            # Поиск по пациенту
            patient_search: Optional[str] = Query(
                None,
                description="Поиск по ФИО или ИИН пациента"
            ),
            patient_id: Optional[UUID] = Query(
                None,
                description="ID пациента"
            ),
            patient_iin: Optional[str] = Query(
                None,
                description="ИИН пациента"
            ),

            # Период
            date_from: Optional[datetime] = Query(
                None,
                description="Дата начала периода"
            ),
            date_to: Optional[datetime] = Query(
                None,
                description="Дата окончания периода"
            ),

            # Статус актива
            status: Optional[AssetStatusEnum] = Query(
                None,
                description="Статус актива"
            ),

            # Статус доставки
            delivery_status: Optional[AssetDeliveryStatusEnum] = Query(
                None,
                description="Статус доставки"
            ),

            # Участок
            area: Optional[str] = Query(
                None,
                description="Участок (например: 17-Терапевтический)"
            ),

            # Специализация
            specialization: Optional[str] = Query(
                None,
                description="Специализация (например: Педиатр)"
            ),

            # Специалист
            specialist: Optional[str] = Query(
                None,
                description="Специалист (например: Малышева А.О.)"
            ),

            # ID организации (может быть передан вручную для фильтрации)
            organization_id: Optional[UUID] = None,
    ):
        self.patient_search = patient_search
        self.patient_id = patient_id
        self.patient_iin = patient_iin
        self.date_from = date_from
        self.date_to = date_to
        self.status = status
        self.delivery_status = delivery_status
        self.area = area
        self.specialization = specialization
        self.specialist = specialist
        self.organization_id = organization_id

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }


class OrganizationAssetsFilterParams:
    """Параметры фильтрации активов по организации"""

    def __init__(
            self,
            date_from: Optional[datetime] = Query(
                None,
                description="Дата начала периода"
            ),
            date_to: Optional[datetime] = Query(
                None,
                description="Дата окончания периода"
            ),
            status: Optional[AssetStatusEnum] = Query(
                None,
                description="Статус актива"
            ),
    ):
        # organization_id убираем отсюда, он будет path-параметром
        self.date_from = date_from
        self.date_to = date_to
        self.status = status

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Преобразовать в словарь для передачи в репозиторий"""
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }