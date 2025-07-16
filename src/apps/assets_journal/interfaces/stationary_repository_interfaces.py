from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from src.apps.assets_journal.domain.models.stationary_asset import StationaryAssetDomain, StationaryAssetListItemDomain
from src.apps.assets_journal.infrastructure.api.schemas.responses.stationary_asset_schemas import (
    StationaryAssetStatisticsSchema,
)


class StationaryAssetRepositoryInterface(ABC):
    """Интерфейс репозитория активов стационара"""

    @abstractmethod
    async def get_by_id(self, asset_id: UUID) -> Optional[StationaryAssetDomain]:
        """
        Получить актив по ID

        :param asset_id: ID актива
        :return: Доменная модель актива или None
        """
        pass

    @abstractmethod
    async def get_by_bg_asset_id(self, bg_asset_id: str) -> Optional[StationaryAssetDomain]:
        """
        Получить актив по BG ID

        :param bg_asset_id: ID актива в BG системе
        :return: Доменная модель актива или None
        """
        pass

    @abstractmethod
    async def get_assets(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[StationaryAssetListItemDomain]:
        """
        Получить список активов с фильтрацией и пагинацией

        :param filters: Словарь фильтров
        :param page: Номер страницы
        :param limit: Количество записей на странице
        :return: Список доменных моделей активов
        """
        pass

    @abstractmethod
    async def get_total_count(self, filters: Dict[str, any]) -> int:
        """
        Получить общее количество активов с учетом фильтров

        :param filters: Словарь фильтров
        :return: Общее количество записей
        """
        pass

    @abstractmethod
    async def create(self, asset: StationaryAssetDomain) -> StationaryAssetDomain:
        """
        Создать новый актив

        :param asset: Доменная модель актива
        :return: Созданная доменная модель актива
        """
        pass

    @abstractmethod
    async def update(self, asset: StationaryAssetDomain) -> StationaryAssetDomain:
        """
        Обновить актив

        :param asset: Доменная модель актива
        :return: Обновленная доменная модель актива
        """
        pass

    @abstractmethod
    async def delete(self, asset_id: UUID) -> None:
        """
        Удалить актив

        :param asset_id: ID актива
        """
        pass

    @abstractmethod
    async def get_statistics(self, filters: Dict[str, any]) -> StationaryAssetStatisticsSchema:
        """
        Получить статистику активов

        :param filters: Словарь фильтров
        :return: Статистика активов
        """
        pass

    @abstractmethod
    async def bulk_create(self, assets: List[StationaryAssetDomain]) -> List[StationaryAssetDomain]:
        """
        Массовое создание активов

        :param assets: Список доменных моделей активов
        :return: Список созданных доменных моделей активов
        """
        pass

    @abstractmethod
    async def exists_by_bg_asset_id(self, bg_asset_id: str) -> bool:
        """
        Проверить существование актива по BG ID

        :param bg_asset_id: ID актива в BG системе
        :return: True если актив существует, False иначе
        """
        pass