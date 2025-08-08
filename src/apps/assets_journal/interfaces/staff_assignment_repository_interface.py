from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from src.apps.assets_journal.domain.models.staff_assignment import StaffAssignmentDomain, StaffAssignmentListItemDomain


class StaffAssignmentRepositoryInterface(ABC):
    """Интерфейс репозитория назначений медперсонала"""

    @abstractmethod
    async def get_by_id(self, assignment_id: UUID) -> Optional[StaffAssignmentDomain]:
        """
        Получить назначение медперсонала по ID

        :param assignment_id: ID назначения
        :return: Доменная модель назначения медперсонала или None
        """
        pass

    @abstractmethod
    async def get_staff_assignments(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[StaffAssignmentListItemDomain]:
        """
        Получить список назначений медперсонала с фильтрацией и пагинацией

        :param filters: Словарь фильтров
        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список доменных моделей назначений медперсонала
        """
        pass

    @abstractmethod
    async def get_total_count(self, filters: Dict[str, any]) -> int:
        """
        Получить общее количество назначений медперсонала с учетом фильтров

        :param filters: Словарь фильтров
        :return: Общее количество записей
        """
        pass

    @abstractmethod
    async def create(self, assignment: StaffAssignmentDomain) -> StaffAssignmentDomain:
        """
        Создать новое назначение медперсонала

        :param assignment: Доменная модель назначения медперсонала
        :return: Созданная доменная модель назначения медперсонала
        """
        pass

    @abstractmethod
    async def update(self, assignment: StaffAssignmentDomain) -> StaffAssignmentDomain:
        """
        Обновить назначение медперсонала

        :param assignment: Доменная модель назначения медперсонала
        :return: Обновленная доменная модель назначения медперсонала
        """
        pass

    @abstractmethod
    async def delete(self, assignment_id: UUID) -> None:
        """
        Удалить назначение медперсонала

        :param assignment_id: ID назначения медперсонала
        """
        pass

    @abstractmethod
    async def get_assignments_by_specialist(
            self,
            specialist_name: str,
            page: int = 1,
            limit: int = 30,
    ) -> List[StaffAssignmentDomain]:
        """
        Получить назначения конкретного специалиста

        :param specialist_name: Имя специалиста
        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список назначений специалиста
        """
        pass

    @abstractmethod
    async def get_assignments_by_area(
            self,
            area_number: str,
            page: int = 1,
            limit: int = 30,
    ) -> List[StaffAssignmentDomain]:
        """
        Получить назначения на конкретный участок

        :param area_number: Номер участка
        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список назначений на участок
        """
        pass

    @abstractmethod
    async def get_assignments_by_department(
            self,
            department: str,
            page: int = 1,
            limit: int = 30,
    ) -> List[StaffAssignmentDomain]:
        """
        Получить назначения по отделению

        :param department: Отделение
        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список назначений по отделению
        """
        pass

    @abstractmethod
    async def get_current_assignments(
            self,
            page: int = 1,
            limit: int = 30,
    ) -> List[StaffAssignmentDomain]:
        """
        Получить текущие активные назначения

        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список текущих назначений
        """
        pass

    @abstractmethod
    async def check_assignment_conflict(
            self,
            specialist_name: str,
            area_number: str,
            start_date: any,
            end_date: any = None,
            exclude_id: UUID = None,
    ) -> bool:
        """
        Проверить конфликт назначений (один специалист не может быть назначен
        на несколько участков одновременно)

        :param specialist_name: Имя специалиста
        :param area_number: Номер участка
        :param start_date: Дата начала нового назначения
        :param end_date: Дата окончания нового назначения
        :param exclude_id: ID назначения, которое нужно исключить из проверки
        :return: True если есть конфликт, False если нет
        """
        pass