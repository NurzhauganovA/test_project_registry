from abc import ABC, abstractmethod
from typing import List, Optional

from src.apps.catalogs.infrastructure.api.schemas.requests.financing_sources_catalog_request_schemas import (
    AddFinancingSourceSchema,
    UpdateFinancingSourceSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.financing_sources_catalog_response_schemas import (
    FinancingSourceFullResponseSchema,
)


class FinancingSourcesCatalogRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_default_name(
        self, name: str
    ) -> Optional[FinancingSourceFullResponseSchema]:
        """Returns an entity with DEFAULT_LANGUAGE and name=name or None"""

    @abstractmethod
    async def get_by_name_locale(
        self, locale: str, name: str
    ) -> Optional[FinancingSourceFullResponseSchema]:
        """Returns an entity in which name_locales[locale] == name, or None"""

    @abstractmethod
    async def get_by_financing_source_code(
        self, financing_source_code: str
    ) -> Optional[FinancingSourceFullResponseSchema]:
        """Returns an entity in which financing_source_code = financing_source_code (given as argument)?"""

    @abstractmethod
    async def get_total_number_of_financing_sources(self) -> int:
        """
        Retrieve a number of ALL financing sources from the Registry Service DB.

        :return: Number of ALL financing sources from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, financing_source_id: int
    ) -> Optional[FinancingSourceFullResponseSchema]:
        """
        Retrieve a financing source record by its unique identifier.

        :param financing_source_id: Unique identifier of the financing source record.
        :type financing_source_id: int
        :return: financing source record instance or None if not found.

        :rtype: Optional[FinancingSourceFullResponseSchema]
        """
        pass

    @abstractmethod
    async def get_financing_sources(
        self,
        name_filter: Optional[str],
        code_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[FinancingSourceFullResponseSchema]:
        """
        Retrieve a list of financing source records, filtered by name.

        :param name_filter: Filter by financing source name (exact match).
        :type name_filter: str
        :param code_filter: Filter by financing source code (exact match).
        :type code_filter: str
        :param page: Pagination page number.
        :type page: int
        :param limit: Pagination limit.
        :type limit: int
        :return: List of matching financing source records.
        :rtype: List[FinancingSourceFullResponseSchema]
        """
        pass

    @abstractmethod
    async def add_financing_source(
        self, request_dto: AddFinancingSourceSchema
    ) -> FinancingSourceFullResponseSchema:
        """
        Add a new financing source record to the catalog.

        :param request_dto: Data for creating a new financing source record.
        :type request_dto: AddFinancingSourceSchema

        :return: The created financing source record.
        :rtype: FinancingSourceFullResponseSchema
        """
        pass

    @abstractmethod
    async def update_financing_source(
        self,
        financing_source_id: int,
        request_dto: UpdateFinancingSourceSchema,
    ) -> FinancingSourceFullResponseSchema:
        """
        Update an existing financing source record.

        :param financing_source_id: financing source ID to update.
        :param request_dto: Data for updating a financing source record.
        :type request_dto: UpdateFinancingSourceSchema

        :return: The updated financing source record.
        :rtype: FinancingSourceFullResponseSchema
        """
        pass

    @abstractmethod
    async def delete_by_id(self, financing_source_id: int) -> None:
        """
        Delete a financing source record by its unique identifier.

        :param financing_source_id: Unique identifier of the financing source record to delete.
        :type financing_source_id: int
        :return: None
        """
        pass
