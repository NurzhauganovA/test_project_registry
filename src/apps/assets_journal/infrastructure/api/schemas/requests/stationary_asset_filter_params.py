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
            patient_search: Optional[str] = None,
            patient_id: Optional[UUID] = None,
            patient_iin: Optional[str] = None,

            # Период
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,

            # Статус актива
            status: Optional[AssetStatusEnum] = None,

            # Статус доставки
            delivery_status: Optional[AssetDeliveryStatusEnum] = None,

            # Участок
            area: Optional[str] = None,

            # Специализация
            specialization: Optional[str] = None,

            # Специалист
            specialist: Optional[str] = None,

            # ID организации (может быть передан вручную для фильтрации)
            organization_id: Optional[int] = None,
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
        data = {}
        for key, value in vars(self).items():
            if not exclude_none or value is not None:
                # Преобразуем enum в его значение
                if isinstance(value, (AssetStatusEnum, AssetDeliveryStatusEnum)):
                    data[key] = value.value
                else:
                    data[key] = value
        return data


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