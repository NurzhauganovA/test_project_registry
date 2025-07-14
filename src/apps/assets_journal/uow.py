from src.apps.assets_journal.infrastructure.repositories.stationary_asset_repository import (
    StationaryAssetRepositoryImpl,
)
from src.apps.assets_journal.interfaces.uow_interface import (
    AssetsJournalUnitOfWorkInterface,
)
from src.shared.base_uow import BaseUnitOfWork


class AssetsJournalUnitOfWorkImpl(BaseUnitOfWork, AssetsJournalUnitOfWorkInterface):
    """Реализация Unit of Work для журналов активов"""

    @property
    def stationary_asset_repository(self) -> StationaryAssetRepositoryImpl:
        """Репозиторий активов стационара"""
        return StationaryAssetRepositoryImpl(
            async_db_session=self._session,
            logger=self._logger
        )