from abc import ABC, abstractmethod
from typing import List, Optional

from src.apps.catalogs.infrastructure.api.schemas.requests.filters.insurance_info_catalog_filters import (
    InsuranceInfoCatalogFilterParams,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.insurance_info_catalog_request_schemas import (
    AddInsuranceInfoRecordSchema,
    UpdateInsuranceInfoRecordSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.insurance_info_catalog_response_schemas import (
    ResponseInsuranceInfoRecordSchema,
)


class InsuranceInfoCatalogRepositoryInterface(ABC):
    @abstractmethod
    async def get_total_number_of_insurance_info_records(self) -> int:
        """
        Get the total count of insurance info records in the DB.

        Returns:
            int: Total number of insurance info records.
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, insurance_info_record_id: int
    ) -> Optional[ResponseInsuranceInfoRecordSchema]:
        """
        Retrieve an insurance info record by its unique identifier.

        Args:
            insurance_info_record_id (int): Unique identifier of the insurance info record.

        Returns:
            Optional[ResponseInsuranceInfoRecordSchema]: The insurance info record if found, else None.
        """
        pass

    @abstractmethod
    async def get_insurance_info_records(
        self,
        filters: InsuranceInfoCatalogFilterParams,
        page: int = 1,
        limit: int = 30,
    ) -> List[ResponseInsuranceInfoRecordSchema]:
        """
        Retrieve a paginated list of insurance info records filtered by given parameters.

        Args:
            filters (InsuranceInfoCatalogFilterParams): Filtering parameters for insurance info records.
            page (int, optional): Page number for pagination. Defaults to 1.
            limit (int, optional): Number of records per page. Defaults to 30.

        Returns:
            List[ResponseInsuranceInfoRecordSchema]: List of matching insurance info records.
        """
        pass

    @abstractmethod
    async def add_insurance_info_record(
        self, request_dto: AddInsuranceInfoRecordSchema
    ) -> ResponseInsuranceInfoRecordSchema:
        """
        Add a new insurance info record to the catalog.
        Moreover, it COMMITS the changes in the DB.

        Args:
            request_dto (AddInsuranceInfoRecordSchema): Data to create a new insurance info record.

        Returns:
            ResponseInsuranceInfoRecordSchema: The created insurance info record.
        """
        pass

    @abstractmethod
    async def update_insurance_info_record(
        self,
        insurance_info_record_id: int,
        request_dto: UpdateInsuranceInfoRecordSchema,
    ) -> ResponseInsuranceInfoRecordSchema:
        """
        Update an existing insurance info record.
        Moreover, it COMMITS the changes in the DB.

        Args:
            insurance_info_record_id (int): Unique identifier of the insurance info record to update.
            request_dto (UpdateInsuranceInfoRecordSchema): Data for updating the insurance info record.

        Returns:
            ResponseInsuranceInfoRecordSchema: The updated insurance info record.
        """
        pass

    @abstractmethod
    async def delete_by_id(self, insurance_info_record_id: int) -> None:
        """
        Delete an insurance info record by its unique identifier.
        Moreover, it COMMITS the changes in the DB.

        Args:
            insurance_info_record_id (int): Unique identifier of the insurance info record to delete.

        Returns:
            None
        """
        pass
