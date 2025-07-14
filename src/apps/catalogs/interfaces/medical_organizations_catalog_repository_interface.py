from abc import ABC, abstractmethod
from typing import List, Optional

from src.apps.catalogs.infrastructure.api.schemas.requests.medical_organizations_catalog_schemas import (
    AddMedicalOrganizationSchema,
    UpdateMedicalOrganizationSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.medical_organizations_catalog_schemas import (
    MedicalOrganizationCatalogFullResponseSchema,
)


class MedicalOrganizationsCatalogRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_default_name(
        self, name: str
    ) -> Optional[MedicalOrganizationCatalogFullResponseSchema]:
        """Returns an entity with DEFAULT_LANGUAGE and name=name or None"""

    @abstractmethod
    async def get_by_organization_code(
        self, organization_code: str
    ) -> Optional[MedicalOrganizationCatalogFullResponseSchema]:
        """Returns an entity in which code (organization_code) == organization_code, or None"""
        pass

    @abstractmethod
    async def get_by_name_locale(
        self, locale: str, name: str
    ) -> Optional[MedicalOrganizationCatalogFullResponseSchema]:
        """Returns an entity in which name_locales[locale] == name, or None"""

    @abstractmethod
    async def get_by_address_locale(
        self, locale: str, address: str
    ) -> Optional[MedicalOrganizationCatalogFullResponseSchema]:
        """Returns an entity in which address_locales[locale] == address, or None"""

    @abstractmethod
    async def get_total_number_of_medical_organizations(self) -> int:
        """
        Retrieve a number of ALL medical organizations from the Registry Service DB.

        :return: Number of ALL medical organizations from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, medical_organization_id: int
    ) -> Optional[MedicalOrganizationCatalogFullResponseSchema]:
        """
        Retrieve a medical organization record by its unique identifier.

        :param medical_organization_id: Unique identifier of the medical organization record.
        :type medical_organization_id: int
        :return: medical organization record instance or None if not found.

        :rtype: Optional[MedicalOrganizationCatalogFullResponseSchema]
        """
        pass

    @abstractmethod
    async def get_medical_organizations(
        self,
        name_filter: Optional[str],
        organization_code_filter: Optional[str],
        address_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[MedicalOrganizationCatalogFullResponseSchema]:
        """
        Retrieve a list of medical organization records, filtered by some parameters.

        :param name_filter: Filter by medical organization name (partial match).
        :type name_filter: str
        :param organization_code_filter: Filter by medical organization code (exact match).
        :type organization_code_filter: str
        :param address_filter: Filter by medical organization address (partial match, search).
        :type address_filter: str
        :param page: Pagination page number.
        :type page: int
        :param limit: Pagination limit.
        :type limit: int
        :return: List of matching medical organizations records.
        :rtype: List[MedicalOrganizationCatalogFullResponseSchema]
        """
        pass

    @abstractmethod
    async def add_medical_organization(
        self, request_dto: AddMedicalOrganizationSchema
    ) -> MedicalOrganizationCatalogFullResponseSchema:
        """
        Add a new medical organization record to the catalog.

        :param request_dto: Data for creating a new medical organization record.
        :type request_dto: AddMedicalOrganizationSchema

        :return: The created medical organization record.
        :rtype: MedicalOrganizationCatalogFullResponseSchema
        """
        pass

    @abstractmethod
    async def update_medical_organization(
        self,
        medical_organization_id: int,
        request_dto: UpdateMedicalOrganizationSchema,
    ) -> MedicalOrganizationCatalogFullResponseSchema:
        """
        Update an existing medical organization record.

        :param medical_organization_id: medical organization ID to update.
        :param request_dto: Data for updating a medical organization record.
        :type request_dto: UpdateMedicalOrganizationSchema

        :return: The updated medical organization record.
        :rtype: MedicalOrganizationCatalogFullResponseSchema
        """
        pass

    @abstractmethod
    async def delete_by_id(self, medical_organization_id: int) -> None:
        """
        Delete a medical organization record by its unique identifier.

        :param medical_organization_id: Unique identifier of the medical organization record to delete.
        :type medical_organization_id: int
        :return: None
        """
        pass
