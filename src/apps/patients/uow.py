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
from src.shared.base_uow import BaseUnitOfWork


class UnitOfWorkImpl(BaseUnitOfWork):
    @property
    def patients_repository(self) -> SQLAlchemyPatientRepository:
        return SQLAlchemyPatientRepository(
            async_db_session=self._session, logger=self._logger
        )

    # ONE-to-ONE relations with patients
    @property
    def citizenship_repository(self) -> SQLAlchemyCitizenshipCatalogueRepositoryImpl:
        return SQLAlchemyCitizenshipCatalogueRepositoryImpl(
            async_db_session=self._session, logger=self._logger
        )

    @property
    def nationalities_repository(self) -> SQLAlchemyNationalitiesCatalogRepositoryImpl:
        return SQLAlchemyNationalitiesCatalogRepositoryImpl(
            async_db_session=self._session, logger=self._logger
        )

    @property
    def medical_organizations_repository(
        self,
    ) -> SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl:
        return SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
            async_db_session=self._session, logger=self._logger
        )

    # MANY-TO-MANY relations with patients
    @property
    def financing_sources_repository(
        self,
    ) -> SQLAlchemyFinancingSourcesCatalogRepositoryImpl:
        return SQLAlchemyFinancingSourcesCatalogRepositoryImpl(
            async_db_session=self._session, logger=self._logger
        )

    @property
    def patient_context_attributes_repository(
        self,
    ) -> SQLAlchemyPatientContextAttributesCatalogueRepositoryImpl:
        return SQLAlchemyPatientContextAttributesCatalogueRepositoryImpl(
            async_db_session=self._session, logger=self._logger
        )
