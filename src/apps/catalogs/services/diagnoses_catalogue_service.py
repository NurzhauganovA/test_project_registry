import math
from typing import List, Optional

from src.apps.catalogs.infrastructure.api.schemas.requests.diagnoses_catalog_request_schemas import (
    AddDiagnosisRequestSchema,
    UpdateDiagnosisRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import (
    DiagnosesCatalogResponseSchema,
    MultipleDiagnosesCatalogResponseSchema,
)
from src.apps.catalogs.interfaces.diagnoses_catalogue_repository_interface import (
    DiagnosesCatalogRepositoryInterface,
)
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import InstanceAlreadyExistsError, NoInstanceFoundError
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)


class DiagnosesCatalogService:
    def __init__(
        self,
        logger: LoggerService,
        diagnoses_catalog_repository: DiagnosesCatalogRepositoryInterface,
    ):
        self._logger = logger
        self._diagnoses_catalog_repository = diagnoses_catalog_repository

    @staticmethod
    def _check_diagnosis_exists_by_id(
        diagnosis: Optional[DiagnosesCatalogResponseSchema],
        original_id: int,
    ) -> DiagnosesCatalogResponseSchema:
        """
        Checks if a diagnosis exists by its ID.

        Args:
            diagnosis: The diagnosis object returned from the repository or None.
            original_id: The ID that was requested.

        Returns:
            The diagnosis object if it exists.

        Raises:
            NoInstanceFoundError: If the diagnosis was not found.
        """
        if diagnosis:
            return diagnosis

        raise NoInstanceFoundError(
            status_code=404,
            detail=_("Diagnosis with ID: %(ID)s was not found.") % {"ID": original_id},
        )

    @staticmethod
    def _check_diagnosis_exists_by_code(
        diagnosis: Optional[DiagnosesCatalogResponseSchema],
        original_code: str,
    ) -> DiagnosesCatalogResponseSchema:
        """
        Checks if a diagnosis exists by its code.

        Args:
            diagnosis: The diagnosis object returned from the repository or None.
            original_code: The code that was requested.

        Returns:
            The diagnosis object if it exists.

        Raises:
            NoInstanceFoundError: If the diagnosis was not found.
        """
        if diagnosis:
            return diagnosis

        raise NoInstanceFoundError(
            status_code=404,
            detail=_("Diagnosis with CODE: '%(CODE)s' was not found.")
            % {"CODE": original_code},
        )

    @staticmethod
    def _check_diagnosis_code_is_not_taken(
        received_diagnosis_by_code: Optional[DiagnosesCatalogResponseSchema],
        original_code: str,
    ) -> None:
        """
        Checks that the diagnosis code is not already used.

        Args:
            received_diagnosis_by_code: The diagnosis object found by code, or None if not found.
            original_code: The code to check for uniqueness.

        Returns:
            None if the code is not taken.

        Raises:
            InstanceAlreadyExistsError: If the code is already used by another diagnosis.
        """
        if not received_diagnosis_by_code:
            return None

        raise InstanceAlreadyExistsError(
            status_code=409,
            detail=_("Diagnosis with code: '%(CODE)s' already exists.")
            % {"CODE": original_code},
        )

    async def get_by_id(
        self,
        diagnosis_id: int,
    ) -> DiagnosesCatalogResponseSchema:
        diagnosis: Optional[DiagnosesCatalogResponseSchema] = (
            await self._diagnoses_catalog_repository.get_by_id(diagnosis_id)
        )

        return self._check_diagnosis_exists_by_id(diagnosis, diagnosis_id)

    async def get_by_code(
        self,
        diagnosis_code: str,
    ) -> DiagnosesCatalogResponseSchema:
        diagnosis: Optional[DiagnosesCatalogResponseSchema] = (
            await self._diagnoses_catalog_repository.get_by_code(diagnosis_code)
        )

        return self._check_diagnosis_exists_by_code(diagnosis, diagnosis_code)

    async def get_diagnoses(
        self,
        pagination_params: PaginationParams,
        diagnosis_code_filter: Optional[str] = None,
    ) -> MultipleDiagnosesCatalogResponseSchema:
        page: int = pagination_params.page or 1  # for mypy
        limit: int = pagination_params.limit or 30  # for mypy

        items: List[DiagnosesCatalogResponseSchema] = (
            await self._diagnoses_catalog_repository.get_diagnoses(
                page=page,
                limit=limit,
                diagnosis_code_filter=diagnosis_code_filter,
            )
        )

        total_items = (
            await self._diagnoses_catalog_repository.get_total_number_of_diagnoses()
        )

        # Calculate pagination metadata
        total_pages = math.ceil(total_items / limit) if limit else 1
        has_next = page < total_pages
        has_prev = page > 1

        pagination = PaginationMetaDataSchema(
            current_page=page,
            per_page=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        )

        return MultipleDiagnosesCatalogResponseSchema(
            items=items,
            pagination=pagination,
        )

    async def add_diagnosis(
        self, request_dto: AddDiagnosisRequestSchema
    ) -> DiagnosesCatalogResponseSchema:
        # Check that diagnosis code is not taken already
        diagnosis: Optional[DiagnosesCatalogResponseSchema] = (
            await self._diagnoses_catalog_repository.get_by_code(
                request_dto.diagnosis_code
            )
        )
        self._check_diagnosis_code_is_not_taken(diagnosis, request_dto.diagnosis_code)

        return await self._diagnoses_catalog_repository.add_diagnosis(request_dto)

    async def update_diagnosis(
        self,
        diagnosis_id: int,
        request_dto: UpdateDiagnosisRequestSchema,
    ) -> DiagnosesCatalogResponseSchema:
        # Check that diagnosis exists
        existing = await self._diagnoses_catalog_repository.get_by_id(diagnosis_id)
        existing = self._check_diagnosis_exists_by_id(existing, diagnosis_id)

        # Check that diagnosis code is not taken already
        if (
            request_dto.diagnosis_code is not None
            and request_dto.diagnosis_code != existing.diagnosis_code
        ):
            diagnosis: Optional[DiagnosesCatalogResponseSchema] = (
                await self._diagnoses_catalog_repository.get_by_code(
                    request_dto.diagnosis_code
                )
            )
            self._check_diagnosis_code_is_not_taken(
                diagnosis, request_dto.diagnosis_code
            )

        updated = await self._diagnoses_catalog_repository.update_diagnosis(
            diagnosis_id, request_dto
        )

        return updated

    async def delete_by_id(self, diagnosis_id: int) -> None:
        # Check that diagnosis exists
        existing = await self._diagnoses_catalog_repository.get_by_id(diagnosis_id)
        self._check_diagnosis_exists_by_id(existing, diagnosis_id)

        await self._diagnoses_catalog_repository.delete_by_id(diagnosis_id)
