from abc import ABC, abstractmethod
from typing import List, Optional

from src.apps.catalogs.infrastructure.api.schemas.requests.patient_context_attributes_catalog_request_schemas import (
    AddPatientContextAttributeSchema,
    UpdatePatientContextAttributeSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.patient_context_attributes_catalog_response_schemas import (
    PatientContextAttributeCatalogFullResponseSchema,
)


class PatientContextAttributesCatalogRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_default_name(
        self, name: str
    ) -> Optional[PatientContextAttributeCatalogFullResponseSchema]:
        """Returns an entity with DEFAULT_LANGUAGE and name=name or None"""

    @abstractmethod
    async def get_by_locale(
        self, locale: str, name: str
    ) -> Optional[PatientContextAttributeCatalogFullResponseSchema]:
        """Returns an entity in which name_locales[locale] == name, or None"""

    @abstractmethod
    async def get_total_number_of_patient_context_attributes(self) -> int:
        """
        Retrieve a number of ALL patient context attributes from the Registry Service DB.

        :return: Amount of ALL patient context attributes from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, context_attribute_id: int
    ) -> Optional[PatientContextAttributeCatalogFullResponseSchema]:
        """
        Retrieve a patient context attribute record by its unique identifier.

        :param context_attribute_id: Unique identifier of the patient context attribute record.
        :type context_attribute_id: int
        :return: patient context attribute record instance or None if not found.

        :rtype: Optional[PatientContextAttributeCatalogFullResponseSchema]
        """
        pass

    @abstractmethod
    async def get_patient_context_attributes(
        self,
        name_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[PatientContextAttributeCatalogFullResponseSchema]:
        """
        Retrieve a list of patient context attribute records, filtered by name.

        :param name_filter: Filter by patient context attribute name (exact match).
        :type name_filter: str
        :param page: Pagination page number.
        :type page: int
        :param limit: Pagination limit.
        :type limit: int
        :return: List of matching patient context attribute records.
        :rtype: List[PatientContextAttributeCatalogFullResponseSchema]
        """
        pass

    @abstractmethod
    async def add_patient_context_attribute(
        self, request_dto: AddPatientContextAttributeSchema
    ) -> PatientContextAttributeCatalogFullResponseSchema:
        """
        Add a new patient context attribute record to the catalog.

        :param request_dto: Data for creating a new patient context attribute record.
        :type request_dto: AddPatientContextAttributeSchema

        :return: The created patient context attribute record.
        :rtype: PatientContextAttributeCatalogFullResponseSchema
        """
        pass

    @abstractmethod
    async def update_patient_context_attribute(
        self,
        context_attribute_id: int,
        request_dto: UpdatePatientContextAttributeSchema,
    ) -> PatientContextAttributeCatalogFullResponseSchema:
        """
        Update an existing patient context attribute record.

        :param context_attribute_id: patient context attribute ID to update.
        :param request_dto: Data for updating a patient context attribute record.
        :type request_dto: UpdatePatientContextAttributeSchema

        :return: The updated patient context attribute record.
        :rtype: PatientContextAttributeCatalogFullResponseSchema
        """
        pass

    @abstractmethod
    async def delete_by_id(self, context_attribute_id: int) -> None:
        """
        Delete a patient context attribute record by its unique identifier.

        :param context_attribute_id: Unique identifier of the patient context attribute record to delete.
        :type context_attribute_id: int
        :return: None
        """
        pass
