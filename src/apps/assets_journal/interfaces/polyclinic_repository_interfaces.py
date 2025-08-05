from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from src.apps.assets_journal.domain.models.polyclinic_asset import PolyclinicAssetDomain, PolyclinicAssetListItemDomain
from src.apps.assets_journal.infrastructure.api.schemas.responses.polyclinic_asset_schemas import (
    PolyclinicAssetStatisticsSchema,
)


class PolyclinicAssetRepositoryInterface(ABC):
    """Интерфейс репозитория активов поликлиники"""

    @abstractmethod
    async def get_by_id(self, asset_id: UUID) -> Optional[PolyclinicAssetDomain]:
        """
        Получить актив по ID

        :param asset_id: ID актива
        :return: Доменная модель актива или None
        """
        pass

    @abstractmethod
    async def get_by_bg_asset_id(self, bg_asset_id: str) -> Optional[PolyclinicAssetDomain]:
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
    ) -> List[PolyclinicAssetListItemDomain]:
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
    async def create(self, asset: PolyclinicAssetDomain) -> PolyclinicAssetDomain:
        """
        Создать новый актив

        :param asset: Доменная модель актива
        :return: Созданная доменная модель актива
        """
        pass

    @abstractmethod
    async def update(self, asset: PolyclinicAssetDomain) -> PolyclinicAssetDomain:
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
    async def get_statistics(self, filters: Dict[str, any]) -> PolyclinicAssetStatisticsSchema:
        """
        Получить статистику активов

        :param filters: Словарь фильтров
        :return: Статистика активов
        """
        pass

    @abstractmethod
    async def bulk_create(self, assets: List[PolyclinicAssetDomain]) -> List[PolyclinicAssetDomain]:
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