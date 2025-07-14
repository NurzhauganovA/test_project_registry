import math
from typing import Optional

from src.apps.catalogs.exceptions import InsuranceInfoInvalidDateError
from src.apps.catalogs.infrastructure.api.schemas.requests.filters.insurance_info_catalog_filters import (
    InsuranceInfoCatalogFilterParams,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.insurance_info_catalog_request_schemas import (
    AddInsuranceInfoRecordSchema,
    UpdateInsuranceInfoRecordSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.insurance_info_catalog_response_schemas import (
    MultipleInsuranceInfoRecordsSchema,
    ResponseInsuranceInfoRecordSchema,
)
from src.apps.catalogs.interfaces.insurance_info_catalog_repository_interface import (
    InsuranceInfoCatalogRepositoryInterface,
)
from src.apps.catalogs.services.financing_sources_catalog_service import (
    FinancingSourceCatalogService,
)
from src.apps.patients.services.patients_service import PatientService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import NoInstanceFoundError
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)


class InsuranceInfoCatalogService:
    def __init__(
        self,
        logger: LoggerService,
        insurance_info_catalog_repository: InsuranceInfoCatalogRepositoryInterface,
        patients_service: PatientService,
        financing_sources_catalog_service: FinancingSourceCatalogService,
    ):
        self._logger = logger
        self._insurance_info_catalog_repository = insurance_info_catalog_repository
        self._patients_service = patients_service
        self._financing_sources_catalog_service = financing_sources_catalog_service

    @staticmethod
    def _check_insurance_info_record_exists(
        insurance_info_record: Optional[ResponseInsuranceInfoRecordSchema],
        original_id: Optional[int] = None,
    ) -> ResponseInsuranceInfoRecordSchema:
        """
        Checks if an insurance info record exists and raises an error if not.

        Args:
            insurance_info_record: The insurance info record to check. None if not found.
            original_id: The ID used for searching (optional), used in an error message.

        Returns:
            The validated ResponseInsuranceInfoRecordSchema if found.

        Raises:
            NoInstanceFoundError: If insurance_info_record is None.
        """
        if not insurance_info_record:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_(
                    "Insurance info record with ID: %(ID)s was not found."
                    % {"ID": original_id if original_id is not None else "unknown"}
                ),
            )

        return insurance_info_record

    async def get_by_id(
        self,
        insurance_info_record_id: int,
    ) -> ResponseInsuranceInfoRecordSchema:
        record = await self._insurance_info_catalog_repository.get_by_id(
            insurance_info_record_id
        )

        return self._check_insurance_info_record_exists(
            record, original_id=insurance_info_record_id
        )

    async def get_insurance_info_records(
        self,
        pagination_params: PaginationParams,
        filters: InsuranceInfoCatalogFilterParams,
    ) -> MultipleInsuranceInfoRecordsSchema:
        page = pagination_params.page or 1
        limit = pagination_params.limit or 30

        items = (
            await self._insurance_info_catalog_repository.get_insurance_info_records(
                filters=filters,
                page=page,
                limit=limit,
            )
        )

        total_items = (
            await self._insurance_info_catalog_repository.get_total_number_of_insurance_info_records()
        )

        total_pages = math.ceil(total_items / limit) if limit else 1
        has_next = page < total_pages
        has_prev = page > 1

        pagination_metadata = PaginationMetaDataSchema(
            current_page=page,
            per_page=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        )

        response_with_pagination = MultipleInsuranceInfoRecordsSchema(
            items=items,
            pagination=pagination_metadata,
        )

        return response_with_pagination

    async def add_insurance_info_record(
        self, request_dto: AddInsuranceInfoRecordSchema
    ) -> ResponseInsuranceInfoRecordSchema:
        # Check that patient and financing source exist
        await self._patients_service.get_by_id(request_dto.patient_id)
        await self._financing_sources_catalog_service.get_by_id(
            request_dto.financing_source_id
        )

        return await self._insurance_info_catalog_repository.add_insurance_info_record(
            request_dto
        )

    async def update_insurance_info_record(
        self,
        insurance_info_record_id: int,
        request_dto: UpdateInsuranceInfoRecordSchema,
    ) -> ResponseInsuranceInfoRecordSchema:
        # Check that insurance infor record exists
        existing = await self._insurance_info_catalog_repository.get_by_id(
            insurance_info_record_id
        )
        self._check_insurance_info_record_exists(
            existing, original_id=insurance_info_record_id
        )

        # Check that patient exists if provided
        if "patient_id" in request_dto.model_fields_set:
            await self._patients_service.get_by_id(request_dto.patient_id)

        # Check that financing source exists if provided
        if "financing_source_id" in request_dto.model_fields_set:
            await self._financing_sources_catalog_service.get_by_id(
                request_dto.financing_source_id
            )

        # Validation of dates taking into account explicit zeroing
        if "valid_from" in request_dto.model_fields_set:
            valid_from = request_dto.valid_from
        else:
            valid_from = existing.valid_from

        if "valid_till" in request_dto.model_fields_set:
            valid_till = request_dto.valid_till
        else:
            valid_till = existing.valid_till

        if valid_from is not None and valid_till is not None:
            if valid_till < valid_from:
                raise InsuranceInfoInvalidDateError(
                    status_code=400,
                    detail=_(
                        "'valid_till' date must be equal or greater than 'valid_from' date."
                    ),
                )

        updated = (
            await self._insurance_info_catalog_repository.update_insurance_info_record(
                insurance_info_record_id, request_dto
            )
        )

        return updated

    async def delete_by_id(self, insurance_info_record_id: int) -> None:
        # Check that insurance infor record exists
        existing = await self._insurance_info_catalog_repository.get_by_id(
            insurance_info_record_id
        )
        self._check_insurance_info_record_exists(
            existing, original_id=insurance_info_record_id
        )

        await self._insurance_info_catalog_repository.delete_by_id(
            insurance_info_record_id
        )
