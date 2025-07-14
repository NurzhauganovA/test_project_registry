from abc import ABC, abstractmethod
from typing import List, Optional

from src.apps.catalogs.infrastructure.api.schemas.requests.diagnoses_catalog_request_schemas import (
    AddDiagnosisRequestSchema,
    UpdateDiagnosisRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import (
    DiagnosesCatalogResponseSchema,
)


class DiagnosesCatalogRepositoryInterface(ABC):
    @abstractmethod
    async def get_total_number_of_diagnoses(self) -> int:
        """
        Retrieve a number of ALL diagnoses from the Registry Service DB.

        :return: Number of ALL diagnoses from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, diagnosis_id: int
    ) -> Optional[DiagnosesCatalogResponseSchema]:
        """
        Retrieve a diagnosis by its unique identifier.

        :param diagnosis_id: Unique identifier of the diagnosis.
        :type diagnosis_id: int
        :return: Diagnosis instance or None if not found.

        :rtype: Optional[DiagnosesCatalogResponseSchema]
        """
        pass

    @abstractmethod
    async def get_by_code(
        self, diagnosis_code: str
    ) -> Optional[DiagnosesCatalogResponseSchema]:
        """
        Retrieve a diagnosis by its code.

        :param diagnosis_code: Unique code of the diagnosis.
        :type diagnosis_code: str
        :return: Diagnosis record instance or None if not found.

        :rtype: Optional[DiagnosesCatalogResponseSchema]
        """
        pass

    @abstractmethod
    async def get_diagnoses(
        self,
        diagnosis_code_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[DiagnosesCatalogResponseSchema]:
        """
        Retrieve a list of diagnoses records, filtered by code if needed.

        :param diagnosis_code_filter: Filter by diagnosis code.
        :type diagnosis_code_filter: str
        :param page: Pagination page parameter.
        :type page: int
        :param limit: Pagination limit (per page) parameter.
        :type limit: int

        :return: List of matching diagnoses records.
        :rtype: List[DiagnosesCatalogResponseSchema]
        """
        pass

    @abstractmethod
    async def add_diagnosis(
        self, request_dto: AddDiagnosisRequestSchema
    ) -> DiagnosesCatalogResponseSchema:
        """
        Add a new diagnosis record to the catalog.

        :param request_dto: Data for creating a new diagnoses record.
        :type request_dto: AddDiagnosisRequestSchema

        :return: The created diagnoses record.
        :rtype: DiagnosesCatalogResponseSchema
        """
        pass

    @abstractmethod
    async def update_diagnosis(
        self, diagnosis_id: int, request_dto: UpdateDiagnosisRequestSchema
    ) -> DiagnosesCatalogResponseSchema:
        """
        Update an existing diagnoses record.

        :param diagnosis_id: Diagnosis ID to update.
        :param request_dto: Data for updating a diagnosis record.
        :type request_dto: UpdateDiagnosisRequestSchema

        :return: The updated diagnosis record.
        :rtype: DiagnosesCatalogResponseSchema
        """
        pass

    @abstractmethod
    async def delete_by_id(self, diagnosis_id: int) -> None:
        """
        Delete a diagnosis record by its unique identifier.

        :param diagnosis_id: Unique identifier of the diagnoses record to delete.
        :type diagnosis_id: int
        :return: None
        """
        pass
