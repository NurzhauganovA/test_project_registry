from abc import ABC, abstractmethod

from src.apps.assets_journal.interfaces.home_call_repository_interfaces import HomeCallRepositoryInterface
from src.apps.assets_journal.interfaces.maternity_repository_interfaces import MaternityAssetRepositoryInterface
from src.apps.assets_journal.interfaces.polyclinic_repository_interfaces import PolyclinicAssetRepositoryInterface
from src.apps.assets_journal.interfaces.sick_leave_repository_interfaces import SickLeaveRepositoryInterface
from src.apps.assets_journal.interfaces.stationary_repository_interfaces import (
    StationaryAssetRepositoryInterface,
)
from src.apps.assets_journal.interfaces.emergency_repository_interfaces import (
    EmergencyAssetRepositoryInterface,
)
from src.apps.assets_journal.interfaces.newborn_repository_interfaces import (
    NewbornAssetRepositoryInterface,
)


class AssetsJournalUnitOfWorkInterface(ABC):
    """Интерфейс Unit of Work для журналов активов"""

    stationary_asset_repository: StationaryAssetRepositoryInterface
    emergency_asset_repository: EmergencyAssetRepositoryInterface
    newborn_asset_repository: NewbornAssetRepositoryInterface
    polyclinic_asset_repository: PolyclinicAssetRepositoryInterface
    maternity_asset_repository: MaternityAssetRepositoryInterface

    # Журнал больничных листов
    sick_leave_repository: SickLeaveRepositoryInterface

    # Журнал вызовов на дом
    home_call_repository: HomeCallRepositoryInterface

    @abstractmethod
    async def commit(self) -> None:
        """Подтвердить транзакцию"""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Откатить транзакцию"""
        pass