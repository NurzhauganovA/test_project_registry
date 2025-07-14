from dependency_injector import containers, providers
from httpx import AsyncClient

from src.core.logger import LoggerService
from src.shared.infrastructure.auth_service_adapter.repositories.auth_service_repository import (
    AuthServiceRepositoryImpl,
)


class AuthServiceContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["src.shared.dependencies"],
    )

    # Dependencies from the Core container
    httpx_client = providers.Dependency(instance_of=AsyncClient)
    logger = providers.Dependency(instance_of=LoggerService)
    base_url = providers.Dependency(instance_of=str)

    auth_service_repository = providers.Factory(
        AuthServiceRepositoryImpl,
        http_client=httpx_client,
        base_url=base_url,
        logger=logger,
    )
