from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.session import sessionmaker

from src.apps.users.infrastructure.kafka.kafka_consumer import UsersKafkaConsumerImpl
from src.apps.users.infrastructure.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from src.apps.users.services.user_service import UserService
from src.core.logger import LoggerService


class UsersContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.apps.users.infrastructure",
            "src.apps.users.services",
        ],
    )
    # Dependencies from core DI-container
    logger = providers.Dependency(instance_of=LoggerService)
    kafka_bootstrap_servers = providers.Dependency(instance_of=list)  # ['kafka:9092']
    kafka_users_topic = providers.Dependency(
        instance_of=str
    )  # 'auth_service-registry_service'
    kafka_group_id = providers.Dependency(
        instance_of=str, default="registry-service-users-group"
    )
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
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        async_db_session=async_db_session,
        logger=logger,
    )

    # Services
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        logger=logger,
    )

    users_kafka_consumer = providers.Singleton(
        UsersKafkaConsumerImpl,
        user_service=user_service,
        bootstrap_servers=kafka_bootstrap_servers,
        topic=kafka_users_topic,
        logger=logger,
        group_id=kafka_group_id,
    )
