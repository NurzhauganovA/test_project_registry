from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from src.apps.assets_journal.domain.models.sick_leave import SickLeaveDomain, SickLeaveListItemDomain


class SickLeaveRepositoryInterface(ABC):
    """Интерфейс репозитория больничных листов"""

    @abstractmethod
    async def get_by_id(self, sick_leave_id: UUID) -> Optional[SickLeaveDomain]:
        """
        Получить больничный лист по ID

        :param sick_leave_id: ID больничного листа
        :return: Доменная модель больничного листа или None
        """
        pass

    @abstractmethod
    async def get_sick_leaves(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[SickLeaveListItemDomain]:
        """
        Получить список больничных листов с фильтрацией и пагинацией

        :param filters: Словарь фильтров
        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список доменных моделей больничных листов
        """
        pass

    @abstractmethod
    async def get_total_count(self, filters: Dict[str, any]) -> int:
        """
        Получить общее количество больничных листов с учетом фильтров

        :param filters: Словарь фильтров
        :return: Общее количество записей
        """
        pass

    @abstractmethod
    async def create(self, sick_leave: SickLeaveDomain) -> SickLeaveDomain:
        """
        Создать новый больничный лист

        :param sick_leave: Доменная модель больничного листа
        :return: Созданная доменная модель больничного листа
        """
        pass

    @abstractmethod
    async def update(self, sick_leave: SickLeaveDomain) -> SickLeaveDomain:
        """
        Обновить больничный лист

        :param sick_leave: Доменная модель больничного листа
        :return: Обновленная доменная модель больничного листа
        """
        pass

    @abstractmethod
    async def delete(self, sick_leave_id: UUID) -> None:
        """
        Удалить больничный лист

        :param sick_leave_id: ID больничного листа
        """
        pass

    @abstractmethod
    async def get_active_sick_leaves_by_patient(self, patient_id: UUID) -> List[SickLeaveDomain]:
        """
        Получить активные больничные листы пациента

        :param patient_id: ID пациента
        :return: Список активных больничных листов
        """
        pass

    @abstractmethod
    async def get_sick_leaves_by_patient(
            self,
            patient_id: UUID,
            page: int = 1,
            limit: int = 30,
    ) -> List[SickLeaveDomain]:
        """
        Получить больничные листы пациента

        :param patient_id: ID пациента
        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список больничных листов пациента
        """
        pass

    @abstractmethod
    async def get_extensions(self, parent_sick_leave_id: UUID) -> List[SickLeaveDomain]:
        """
        Получить продления больничного листа

        :param parent_sick_leave_id: ID родительского больничного листа
        :return: Список продлений
        """
        pass