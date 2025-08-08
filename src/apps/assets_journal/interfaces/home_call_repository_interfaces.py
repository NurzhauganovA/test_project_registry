from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from src.apps.assets_journal.domain.models.home_call import HomeCallDomain, HomeCallListItemDomain


class HomeCallRepositoryInterface(ABC):
    """Интерфейс репозитория вызовов на дом"""

    @abstractmethod
    async def get_by_id(self, home_call_id: UUID) -> Optional[HomeCallDomain]:
        """
        Получить вызов на дом по ID

        :param home_call_id: ID вызова на дом
        :return: Доменная модель вызова на дом или None
        """
        pass

    @abstractmethod
    async def get_by_call_number(self, call_number: str) -> Optional[HomeCallDomain]:
        """
        Получить вызов на дом по номеру

        :param call_number: Номер вызова
        :return: Доменная модель вызова на дом или None
        """
        pass

    @abstractmethod
    async def get_home_calls(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[HomeCallListItemDomain]:
        """
        Получить список вызовов на дом с фильтрацией и пагинацией

        :param filters: Словарь фильтров
        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список доменных моделей вызовов на дом
        """
        pass

    @abstractmethod
    async def get_total_count(self, filters: Dict[str, any]) -> int:
        """
        Получить общее количество вызовов на дом с учетом фильтров

        :param filters: Словарь фильтров
        :return: Общее количество записей
        """
        pass

    @abstractmethod
    async def create(self, home_call: HomeCallDomain) -> HomeCallDomain:
        """
        Создать новый вызов на дом

        :param home_call: Доменная модель вызова на дом
        :return: Созданная доменная модель вызова на дом
        """
        pass

    @abstractmethod
    async def update(self, home_call: HomeCallDomain) -> HomeCallDomain:
        """
        Обновить вызов на дом

        :param home_call: Доменная модель вызова на дом
        :return: Обновленная доменная модель вызова на дом
        """
        pass

    @abstractmethod
    async def delete(self, home_call_id: UUID) -> None:
        """
        Удалить вызов на дом

        :param home_call_id: ID вызова на дом
        """
        pass

    @abstractmethod
    async def get_active_home_calls_by_patient(self, patient_id: UUID) -> List[HomeCallDomain]:
        """
        Получить активные вызовы на дом пациента

        :param patient_id: ID пациента
        :return: Список активных вызовов на дом
        """
        pass

    @abstractmethod
    async def get_home_calls_by_patient(
            self,
            patient_id: UUID,
            page: int = 1,
            limit: int = 30,
    ) -> List[HomeCallDomain]:
        """
        Получить вызовы на дом пациента

        :param patient_id: ID пациента
        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список вызовов на дом пациента
        """
        pass

    @abstractmethod
    async def get_home_calls_by_specialist(
            self,
            specialist: str,
            page: int = 1,
            limit: int = 30,
    ) -> List[HomeCallDomain]:
        """
        Получить вызовы на дом по специалисту

        :param specialist: Имя специалиста
        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список вызовов на дом специалиста
        """
        pass

    @abstractmethod
    async def exists_by_call_number(self, call_number: str) -> bool:
        """
        Проверить существование вызова по номеру

        :param call_number: Номер вызова
        :return: True если вызов существует, False иначе
        """
        pass