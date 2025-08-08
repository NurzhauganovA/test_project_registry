from src.apps.assets_journal.infrastructure.repositories.maternity_asset_repository import MaternityAssetRepositoryImpl
from src.apps.assets_journal.infrastructure.repositories.polyclinic_asset_repository import (
    PolyclinicAssetRepositoryImpl
)
from src.apps.assets_journal.infrastructure.repositories.sick_leave_repository import SickLeaveRepositoryImpl
from src.apps.assets_journal.infrastructure.repositories.stationary_asset_repository import (
    StationaryAssetRepositoryImpl,
)
from src.apps.assets_journal.infrastructure.repositories.emergency_asset_repository import (
    EmergencyAssetRepositoryImpl,
)
from src.apps.assets_journal.infrastructure.repositories.newborn_asset_repository import (
    NewbornAssetRepositoryImpl,
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

    @property
    def emergency_asset_repository(self) -> EmergencyAssetRepositoryImpl:
        """Репозиторий активов скорой помощи"""
        return EmergencyAssetRepositoryImpl(
            async_db_session=self._session,
            logger=self._logger
        )

    @property
    def newborn_asset_repository(self) -> NewbornAssetRepositoryImpl:
        """Репозиторий активов новорожденных"""
        return NewbornAssetRepositoryImpl(
            async_db_session=self._session,
            logger=self._logger
        )

    @property
    def polyclinic_asset_repository(self) -> PolyclinicAssetRepositoryImpl:
        """Репозиторий активов поликлиники"""
        return PolyclinicAssetRepositoryImpl(
            async_db_session=self._session,
            logger=self._logger
        )

    @property
    def maternity_asset_repository(self) -> MaternityAssetRepositoryImpl:
        """Репозиторий активов роддома"""
        return MaternityAssetRepositoryImpl(
            async_db_session=self._session,
            logger=self._logger
        )

    # Журнал больничных листов
    @property
    def sick_leave_repository(self) -> SickLeaveRepositoryImpl:
        """Репозиторий больничных листов"""
        return SickLeaveRepositoryImpl(
            async_db_session=self._session,
            logger=self._logger
        )