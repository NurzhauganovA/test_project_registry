from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type

from src.apps.catalogs.infrastructure.repositories.citizenship_catalog_repository import (
    SQLAlchemyCitizenshipCatalogueRepositoryImpl,
)
from src.apps.catalogs.infrastructure.repositories.financing_sources_repository import (
    SQLAlchemyFinancingSourcesCatalogRepositoryImpl,
)
from src.apps.catalogs.infrastructure.repositories.medical_organizations_catalog_repository import (
    SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl,
)
from src.apps.catalogs.infrastructure.repositories.nationalities_catalog_repository import (
    SQLAlchemyNationalitiesCatalogRepositoryImpl,
)
from src.apps.catalogs.infrastructure.repositories.patient_context_attributes_repository import (
    SQLAlchemyPatientContextAttributesCatalogueRepositoryImpl,
)
from src.apps.patients.infrastructure.repositories.patient_repository import (
    SQLAlchemyPatientRepository,
)


class UnitOfWorkInterface(ABC):
    patients_repository: SQLAlchemyPatientRepository
    citizenship_repository: SQLAlchemyCitizenshipCatalogueRepositoryImpl
    nationalities_repository: SQLAlchemyNationalitiesCatalogRepositoryImpl
    medical_organizations_repository: (
        SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl
    )
    financing_sources_repository: SQLAlchemyFinancingSourcesCatalogRepositoryImpl
    patient_context_attributes_repository: (
        SQLAlchemyPatientContextAttributesCatalogueRepositoryImpl
    )

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWorkInterface":
        pass

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        pass
