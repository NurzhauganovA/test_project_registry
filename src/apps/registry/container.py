from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.session import sessionmaker

from src.apps.catalogs.services.financing_sources_catalog_service import (
    FinancingSourceCatalogService,
)
from src.apps.patients.services.patients_service import PatientService
from src.apps.platform_rules.infrastructure.repositories.platform_rules_repository import (
    SQLAlchemyPlatformRulesRepositoryImpl,
)
from src.apps.registry.infrastructure.repositories.appointment_repository import (
    AppointmentRepositoryImpl,
)
from src.apps.registry.infrastructure.repositories.schedule_day_repostiory import (
    ScheduleDayRepositoryImpl,
)
from src.apps.registry.infrastructure.repositories.schedule_repository import (
    ScheduleRepositoryImpl,
)
from src.apps.registry.services.appointment_service import AppointmentService
from src.apps.registry.services.schedule_day_service import ScheduleDayService
from src.apps.registry.services.schedule_service import ScheduleService
from src.apps.registry.uow import UnitOfWorkImpl
from src.apps.users.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from src.apps.users.services.user_service import UserService
from src.core.database.config import provide_async_session
from src.core.logger import LoggerService


class RegistryContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.apps.registry.infrastructure.api",
        ]
    )
    config = providers.Configuration()

    # Dependencies from core DI-container
    logger = providers.Dependency(instance_of=LoggerService)
    user_service: providers.Dependency[UserService] = providers.Dependency()
    patients_service: providers.Dependency[PatientService] = providers.Dependency()
    user_repository: providers.Dependency[SQLAlchemyUserRepository] = providers.Dependency()
    platform_rules_repository: providers.Dependency[SQLAlchemyPlatformRulesRepositoryImpl] = providers.Dependency()
    engine = providers.Dependency(instance_of=AsyncEngine)
    financing_sources_catalog_service = providers.Dependency(
        instance_of=FinancingSourceCatalogService
    )

    # Session factory
    session_factory = providers.Singleton(
        sessionmaker, bind=engine, expire_on_commit=False, class_=AsyncSession
    )

    # Async session
    async_db_session = providers.Resource(provide_async_session, session_factory)

    # UOW
    unit_of_work = providers.Factory(
        UnitOfWorkImpl,
        session=async_db_session,
        logger=logger,
    )

    # Repositories
    schedule_day_repository = providers.Factory(
        ScheduleDayRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    appointment_repository = providers.Factory(
        AppointmentRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    schedule_repository = providers.Factory(
        ScheduleRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )

    # Services
    schedule_day_service = providers.Factory(
        ScheduleDayService,
        uow=unit_of_work,
        logger=logger,
        schedule_day_repository=schedule_day_repository,
        appointment_repository=appointment_repository,
    )

    appointment_service = providers.Factory(
        AppointmentService,
        uow=unit_of_work,
        logger=logger,
        appointment_repository=appointment_repository,
        schedule_repository=schedule_repository,
        schedule_day_repository=schedule_day_repository,
        user_service=user_service,
        patients_service=patients_service,
        user_repository=user_repository,
        financing_sources_catalog_service=financing_sources_catalog_service,
    )

    schedule_service = providers.Factory(
        ScheduleService,
        uow=unit_of_work,
        logger=logger,
        appointment_repository=appointment_repository,
        schedule_repository=schedule_repository,
        schedule_day_repository=schedule_day_repository,
        schedule_day_service=schedule_day_service,
        user_service=user_service,
        platform_rules_repository=platform_rules_repository,
    )
