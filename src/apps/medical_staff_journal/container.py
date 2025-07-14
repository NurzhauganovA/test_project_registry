from dependency_injector import containers, providers
from httpx import AsyncClient

from src.apps.medical_staff_journal.services.medical_staff_jornal_service import (
    MedicalStaffJournalService,
)
from src.core.logger import LoggerService
from src.shared.infrastructure.rpn_integration_service_adapter.repositories.rpn_integration_service_repository import (
    RpnIntegrationServiceRepositoryImpl,
)


class MedicalStaffJournalContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.apps.medical_staff_journal.services",
            "src.apps.medical_staff_journal.infrastructure.api",
        ],
    )

    # Dependencies from the Core container
    httpx_client = providers.Dependency(instance_of=AsyncClient)
    logger = providers.Dependency(instance_of=LoggerService)
    base_url = providers.Dependency(instance_of=str)

    # Repositories
    rpn_integration_service_repository = providers.Factory(
        RpnIntegrationServiceRepositoryImpl,
        http_client=httpx_client,
        base_url=base_url,
        logger=logger,
    )

    # Services
    medical_staff_journal_service = providers.Factory(
        MedicalStaffJournalService,
        logger=logger,
        rpn_integration_service_repository=rpn_integration_service_repository,
    )
