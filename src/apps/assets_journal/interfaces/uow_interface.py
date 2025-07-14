from abc import ABC, abstractmethod

from src.apps.assets_journal.interfaces.repository_interfaces import (
    StationaryAssetRepositoryInterface,
)


class AssetsJournalUnitOfWorkInterface(ABC):
    """Интерфейс Unit of Work для журналов активов"""

    stationary_asset_repository: StationaryAssetRepositoryInterface

    @abstractmethod
    async def commit(self) -> None:
        """Подтвердить транзакцию"""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Откатить транзакцию"""
        pass