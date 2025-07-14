from abc import ABC, abstractmethod
from typing import List, Optional

from src.apps.catalogs.infrastructure.api.schemas.requests.citizenship_catalog_request_schemas import (
    AddCitizenshipSchema,
    UpdateCitizenshipSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.citizenship_catalog_response_schemas import (
    CitizenshipCatalogFullResponseSchema,
)


class CitizenshipCatalogRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_default_name(
        self, name: str
    ) -> Optional[CitizenshipCatalogFullResponseSchema]:
        """Returns an entity with DEFAULT_LANGUAGE and name=name or None"""

    @abstractmethod
    async def get_by_locale(
        self, locale: str, name: str
    ) -> Optional[CitizenshipCatalogFullResponseSchema]:
        """Returns an entity in which name_locales[locale] == name, or None"""

    @abstractmethod
    async def get_total_number_of_citizenship_records(self) -> int:
        """
        Retrieve a number of ALL citizenship from the Registry Service DB.

        :return: Amount of ALL citizenship from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, citizenship_id: int
    ) -> Optional[CitizenshipCatalogFullResponseSchema]:
        """
        Retrieve a citizenship record by its unique identifier.

        :param citizenship_id: Unique identifier of the citizenship record.
        :type citizenship_id: int
        :return: Citizenship record instance or None if not found.

        :rtype: Optional[CitizenshipCatalogFullResponseSchema]
        """
        pass

    @abstractmethod
    async def get_by_country_code(
        self, country_code: str
    ) -> Optional[CitizenshipCatalogFullResponseSchema]:
        """
        Retrieve a citizenship record by its country code.

        :param country_code: Unique identifier of the citizenship record.
        :type country_code: str
        :return: Citizenship record instance or None if not found.

        :rtype: Optional[CitizenshipCatalogFullResponseSchema]
        """
        pass

    @abstractmethod
    async def get_citizenship_records(
        self,
        name_filter: Optional[str],
        country_code_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[CitizenshipCatalogFullResponseSchema]:
        """
        Retrieve a list of citizenship records, filtered by name and country code.

        :param name_filter: Filter by citizenship name (partial match).
        :type name_filter: str
        :param country_code_filter: Filter by country code (ISO).
        :type country_code_filter: str
        :param page: Pagination page parameter.
        :type page: int
        :param limit: Pagination limit (per page) parameter.
        :type limit: int

        :return: List of matching citizenship records.
        :rtype: List[CitizenshipCatalogFullResponseSchema]
        """
        pass

    @abstractmethod
    async def add_citizenship(
        self, request_dto: AddCitizenshipSchema
    ) -> CitizenshipCatalogFullResponseSchema:
        """
        Add a new citizenship record to the catalog.

        :param request_dto: Data for creating a new citizenship record.
        :type request_dto: AddCitizenshipSchema
        :return: The created citizenship record.
        :rtype: CitizenshipCatalogFullResponseSchema
        """
        pass

    @abstractmethod
    async def update_citizenship(
        self, citizenship_id: int, request_dto: UpdateCitizenshipSchema
    ) -> CitizenshipCatalogFullResponseSchema:
        """
        Update an existing citizenship record.

        :param citizenship_id: Citizenship ID to update.
        :param request_dto: Data for updating a citizenship record.
        :type request_dto: UpdateCitizenshipSchema
        :return: The updated citizenship record.
        :rtype: CitizenshipCatalogFullResponseSchema
        """
        pass

    @abstractmethod
    async def delete_by_id(self, citizenship_id: int) -> None:
        """
        Delete a citizenship record by its unique identifier.

        :param citizenship_id: Unique identifier of the citizenship record to delete.
        :type citizenship_id: int
        :return: None
        """
        pass
