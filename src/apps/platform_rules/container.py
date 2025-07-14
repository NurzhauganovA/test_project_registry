from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.session import sessionmaker

from src.apps.platform_rules.infrastructure.repositories.platform_rules_repository import (
    SQLAlchemyPlatformRulesRepositoryImpl,
)
from src.core.logger import LoggerService


class PlatformRulesContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.apps.platform_rules.infrastructure.api",
        ]
    )
    config = providers.Configuration()

    # Dependencies from core DI-container
    logger = providers.Dependency(instance_of=LoggerService)
    engine = providers.Dependency(instance_of=AsyncEngine)

    # Session factory
    session_factory = providers.Singleton(
        sessionmaker, bind=engine, expire_on_commit=False, class_=AsyncSession
    )

    # Async session
    async_db_session = providers.Singleton(
        lambda session_factory: session_factory(), session_factory
    )

    # Repositories
    platform_rules_repository = providers.Factory(
        SQLAlchemyPlatformRulesRepositoryImpl,
        async_db_session=async_db_session,
        logger=logger,
    )
