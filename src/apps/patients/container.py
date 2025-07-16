from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.session import sessionmaker

from src.apps.catalogs.services.citizenship_catalog_service import (
    CitizenshipCatalogService,
)
from src.apps.catalogs.services.financing_sources_catalog_service import (
    FinancingSourceCatalogService,
)
from src.apps.catalogs.services.medical_organizations_catalog_service import (
    MedicalOrganizationsCatalogService,
)
from src.apps.catalogs.services.nationalities_catalog_service import (
    NationalitiesCatalogService,
)
from src.apps.catalogs.services.patient_context_attribute_service import (
    PatientContextAttributeService,
)
from src.apps.patients.infrastructure.repositories.patient_repository import (
    SQLAlchemyPatientRepository,
)
from src.apps.patients.services.patients_service import PatientService
from src.apps.patients.uow import UnitOfWorkImpl
from src.core.database.config import provide_async_session
from src.core.logger import LoggerService


class PatientsContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.apps.patients.infrastructure.api",
        ]
    )
    config = providers.Configuration()

    # Dependencies from core DI-container
    logger = providers.Dependency(instance_of=LoggerService)
    engine = providers.Dependency(instance_of=AsyncEngine)
    citizenship_service = providers.Dependency(instance_of=CitizenshipCatalogService)
    nationalities_service = providers.Dependency(
        instance_of=NationalitiesCatalogService
    )
    medical_org_service = providers.Dependency(
        instance_of=MedicalOrganizationsCatalogService
    )
    financing_source_service = providers.Dependency(
        instance_of=FinancingSourceCatalogService
    )
    patient_context_attributes_service = providers.Dependency(
        instance_of=PatientContextAttributeService
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
    patients_repository = providers.Factory(
        SQLAlchemyPatientRepository, async_db_session=async_db_session, logger=logger
    )

    # Services
    patients_service = providers.Factory(
        PatientService,
        uow=unit_of_work,
        patients_repository=patients_repository,
        citizenship_service=citizenship_service,
        nationalities_service=nationalities_service,
        medical_org_service=medical_org_service,
        financing_source_service=financing_source_service,
        patient_context_attributes_service=patient_context_attributes_service,
    )
