from abc import ABC, abstractmethod
from typing import List, Optional

from src.apps.catalogs.infrastructure.api.schemas.requests.nationalities_catalog_request_schemas import (
    AddNationalitySchema,
    UpdateNationalitySchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.nationalities_catalog_response_schemas import (
    NationalityCatalogFullResponseSchema,
)


class NationalitiesCatalogRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_default_name(
        self, name: str
    ) -> Optional[NationalityCatalogFullResponseSchema]:
        """Returns an entity with DEFAULT_LANGUAGE and name=name or None"""

    @abstractmethod
    async def get_by_locale(
        self, locale: str, name: str
    ) -> Optional[NationalityCatalogFullResponseSchema]:
        """Returns an entity in which name_locales[locale] == name, or None"""

    @abstractmethod
    async def get_total_number_of_nationalities(self) -> int:
        """
        Retrieve a number of ALL nationalities from the Registry Service DB.

        :return: Number of ALL nationalities from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, nationality_id: int
    ) -> Optional[NationalityCatalogFullResponseSchema]:
        """
        Retrieve a nationality record by its unique identifier.

        :param nationality_id: Unique identifier of the nationality record.
        :type nationality_id: int
        :return: Nationality record instance or None if not found.

        :rtype: Optional[NationalityCatalogFullResponseSchema]
        """
        pass

    @abstractmethod
    async def get_nationalities(
        self,
        name_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[NationalityCatalogFullResponseSchema]:
        """
        Retrieve a list of nationality records, filtered by name.

        :param name_filter: Filter by nationality name (partial match).
        :type name_filter: str
        :param page: Pagination page number.
        :type page: int
        :param limit: Pagination limit.
        :type limit: int
        :return: List of matching nationality records.
        :rtype: List[NationalityCatalogFullResponseSchema]
        """
        pass

    @abstractmethod
    async def add_nationality(
        self, request_dto: AddNationalitySchema
    ) -> NationalityCatalogFullResponseSchema:
        """
        Add a new nationality record to the catalog.

        :param request_dto: Data for creating a new nationality record.
        :type request_dto: AddNationalitySchema
        :return: The created nationality record.
        :rtype: NationalityCatalogFullResponseSchema
        """
        pass

    @abstractmethod
    async def update_nationality(
        self, nationality_id: int, request_dto: UpdateNationalitySchema
    ) -> NationalityCatalogFullResponseSchema:
        """
        Update an existing nationality record.

        :param nationality_id: Nationality ID to update.
        :param request_dto: Data for updating a nationality record.
        :type request_dto: UpdateNationalitySchema
        :return: The updated nationality record.
        :rtype: NationalityCatalogFullResponseSchema
        """
        pass

    @abstractmethod
    async def delete_by_id(self, nationality_id: int) -> None:
        """
        Delete a nationality record by its unique identifier.

        :param nationality_id: Unique identifier of the nationality record to delete.
        :type nationality_id: int
        :return: None
        """
        pass
