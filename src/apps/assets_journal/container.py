from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.session import sessionmaker

from src.apps.assets_journal.infrastructure.repositories import polyclinic_asset_repository
from src.apps.assets_journal.infrastructure.repositories.polyclinic_asset_repository import \
    PolyclinicAssetRepositoryImpl
from src.apps.assets_journal.infrastructure.repositories.stationary_asset_repository import (
    StationaryAssetRepositoryImpl,
)
from src.apps.assets_journal.infrastructure.repositories.emergency_asset_repository import (
    EmergencyAssetRepositoryImpl,
)
from src.apps.assets_journal.infrastructure.repositories.newborn_asset_repository import (
    NewbornAssetRepositoryImpl,
)
from src.apps.assets_journal.services.polyclinic_asset_service import PolyclinicAssetService
from src.apps.assets_journal.services.stationary_asset_service import (
    StationaryAssetService,
)
from src.apps.assets_journal.services.emergency_asset_service import (
    EmergencyAssetService,
)
from src.apps.assets_journal.services.newborn_asset_service import (
    NewbornAssetService,
)
from src.apps.assets_journal.uow import AssetsJournalUnitOfWorkImpl
from src.apps.catalogs.services.medical_organizations_catalog_service import (
    MedicalOrganizationsCatalogService,
)
from src.apps.patients.services.patients_service import PatientService
from src.core.database.config import provide_async_session
from src.core.logger import LoggerService


class AssetsJournalContainer(containers.DeclarativeContainer):
    """DI контейнер для модуля журналов активов"""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.apps.assets_journal.infrastructure.api",
        ]
    )

    config = providers.Configuration()

    # Зависимости из основного контейнера
    logger = providers.Dependency(instance_of=LoggerService)
    engine = providers.Dependency(instance_of=AsyncEngine)

    # Зависимости от других модулей
    patients_service = providers.Dependency(instance_of=PatientService)
    medical_organizations_catalog_service = providers.Dependency(
        instance_of=MedicalOrganizationsCatalogService
    )

    # Фабрика сессий
    session_factory = providers.Singleton(
        sessionmaker, bind=engine, expire_on_commit=False, class_=AsyncSession
    )

    # Асинхронная сессия БД
    async_db_session = providers.Resource(provide_async_session, session_factory)

    # Unit of Work
    unit_of_work = providers.Factory(
        AssetsJournalUnitOfWorkImpl,
        session=async_db_session,
        logger=logger,
    )

    # Репозитории
    stationary_asset_repository = providers.Factory(
        StationaryAssetRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    emergency_asset_repository = providers.Factory(
        EmergencyAssetRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    newborn_asset_repository = providers.Factory(
        NewbornAssetRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    polyclinic_asset_repository = providers.Factory(
        PolyclinicAssetRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger
    )

    # Сервисы
    stationary_asset_service = providers.Factory(
        StationaryAssetService,
        uow=unit_of_work,
        stationary_asset_repository=stationary_asset_repository,
        patients_service=patients_service,
        medical_organizations_catalog_service=medical_organizations_catalog_service,
        logger=logger,
    )

    emergency_asset_service = providers.Factory(
        EmergencyAssetService,
        uow=unit_of_work,
        emergency_asset_repository=emergency_asset_repository,
        patients_service=patients_service,
        medical_organizations_catalog_service=medical_organizations_catalog_service,
        logger=logger,
    )

    newborn_asset_service = providers.Factory(
        NewbornAssetService,
        uow=unit_of_work,
        newborn_asset_repository=newborn_asset_repository,
        patients_service=patients_service,
        medical_organizations_catalog_service=medical_organizations_catalog_service,
        logger=logger,
    )

    polyclinic_asset_service = providers.Factory(
        PolyclinicAssetService,
        uow=unit_of_work,
        polyclinic_asset_repository=polyclinic_asset_repository,
        patients_service=patients_service,
        medical_organizations_catalog_service=medical_organizations_catalog_service,
        logger=logger,
    )