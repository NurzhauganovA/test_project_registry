from dependency_injector import containers, providers
from fastapi import FastAPI

from src.apps.assets_journal.container import AssetsJournalContainer
from src.apps.catalogs.container import CatalogsContainer
from src.apps.medical_staff_journal.container import MedicalStaffJournalContainer
from src.apps.patients.container import PatientsContainer
from src.apps.platform_rules.container import PlatformRulesContainer
from src.apps.registry.container import RegistryContainer
from src.apps.users.container import UsersContainer
from src.core.logger import LoggerService
from src.core.resources.fastapi_resource import FastAPIResource
from src.core.resources.httpx_resource import HttpxClientResource
from src.core.resources.sqlalchemy_resource import sqlalchemy_resource
from src.core.resources.uvicorn_resource import uvicorn_server_resource
from src.core.settings import project_settings
from src.core.utils import get_exception_handlers, get_routers
from src.shared.infrastructure.auth_service_adapter.container import (
    AuthServiceContainer,
)


class CoreContainer(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()

    # Logger
    logger = providers.Singleton(
        LoggerService,
        name="Registry Service Logger",
    )

    # Database engine
    engine = providers.Resource(
        sqlalchemy_resource,
        project_settings.DATABASE_URI,
        pool_pre_ping=True,
        pool_size=project_settings.POOL_SIZE,
        max_overflow=project_settings.MAX_OVERFLOW,
    )

    routers = providers.Callable(get_routers)
    exception_handlers = providers.Callable(get_exception_handlers)

    # FastAPI app
    api_application: providers.Resource[FastAPI] = providers.Resource(
        FastAPIResource,
        routers=routers,
        exception_handlers=exception_handlers,
        project_name=config.PROJECT_NAME,
        project_version=config.PROJECT_VERSION,
        api_prefix=config.API_PREFIX,
        debug=config.API_ENABLE_DOCS,
        enable_docs=config.API_ENABLE_DOCS,
        backend_cors_origins=config.BACKEND_CORS_ORIGINS,
    )

    # ASGI server
    api_server = providers.Singleton(
        uvicorn_server_resource,
        app=api_application,
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=config.API_ENABLE_DOCS,
    )

    # httpx client
    httpx_client = providers.Resource(
        HttpxClientResource,
        timeout=config.TIMEOUT,
        max_keepalive_connections=config.MAX_KEEPALIVE_CONNECTIONS,
        max_connections=config.MAX_CONNECTIONS,
    )

    # Apps containers
    users_container = providers.Container(
        UsersContainer,
        logger=logger,
        engine=engine,
        kafka_bootstrap_servers=config.kafka.KAFKA_BOOTSTRAP_SERVERS,
        kafka_users_topic=config.kafka.ACTIONS_ON_USERS_KAFKA_TOPIC,
        kafka_group_id=config.kafka.KAFKA_GROUP_ID,
    )

    platform_rules_container = providers.Container(
        PlatformRulesContainer,
        logger=logger,
        engine=engine,
    )

    medical_staff_journal_container = providers.Container(
        MedicalStaffJournalContainer,
        httpx_client=httpx_client,
        base_url=config.RPN_INTEGRATION_SERVICE_BASE_URL,
        logger=logger,
    )

    catalogs_container = providers.Container(
        CatalogsContainer,
        logger=logger,
        engine=engine,
        # patients_container is below
    )

    patients_container = providers.Container(
        PatientsContainer,
        logger=logger,
        engine=engine,
        # catalogs are below
    )

    registry_container = providers.Container(
        RegistryContainer,
        logger=logger,
        engine=engine,
        user_service=users_container.user_service,
        patients_service=patients_container.patients_service,
        user_repository=users_container.user_repository,
        platform_rules_repository=platform_rules_container.platform_rules_repository,
    )

    # OVERRIDE --------------------------------------------------------------------------------------------------------
    """
    Override is needed here because of the cyclic dependency between catalogs container and patients container.
    """
    catalogs_container.override(
        providers.Container(
            CatalogsContainer,
            logger=logger,
            engine=engine,
            patients_service=patients_container.patients_service,
            user_service=users_container.user_service,
        )
    )

    patients_container.override(
        providers.Container(
            PatientsContainer,
            logger=logger,
            engine=engine,
            citizenship_service=catalogs_container.citizenship_catalog_service,
            nationalities_service=catalogs_container.nationalities_catalog_service,
            medical_org_service=catalogs_container.medical_organizations_catalog_service,
            financing_source_service=catalogs_container.financing_sources_catalog_service,
            patient_context_attributes_service=catalogs_container.patient_context_attributes_service,
        )
    )
    # --------------------------------------------------------------------------------------------------------

    # Shared adapters containers
    auth_container = providers.Container(
        AuthServiceContainer,
        httpx_client=httpx_client,
        base_url=config.AUTH_SERVICE_BASE_URL,
        logger=logger,
    )

    # Assets Journal container
    assets_journal_container = providers.Container(
        AssetsJournalContainer,
        logger=logger,
        engine=engine,
        patients_service=patients_container.patients_service,
        medical_organizations_catalog_service=catalogs_container.medical_organizations_catalog_service,
    )
