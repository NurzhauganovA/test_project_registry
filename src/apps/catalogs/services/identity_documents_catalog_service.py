import math
from typing import List, Optional

from src.apps.catalogs.infrastructure.api.schemas.requests.filters.identity_documents_catalog_filters import (
    IdentityDocumentsCatalogFilterParams,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.identity_documents_catalog_request_schemas import (
    AddIdentityDocumentRequestSchema,
    UpdateIdentityDocumentRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.identity_documents_catalog_response_schemas import (
    IdentityDocumentResponseSchema,
    MultipleIdentityDocumentsCatalogResponseSchema,
)
from src.apps.catalogs.interfaces.identity_documents_repository_interface import (
    IdentityDocumentsCatalogRepositoryInterface,
)
from src.apps.patients.services.patients_service import PatientService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import NoInstanceFoundError
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)


class IdentityDocumentsCatalogService:
    def __init__(
        self,
        logger: LoggerService,
        identity_documents_repository: IdentityDocumentsCatalogRepositoryInterface,
        patients_service: PatientService,
    ):
        self._logger = logger
        self._identity_documents_repository = identity_documents_repository
        self._patient_service = patients_service

    @staticmethod
    def _check_identity_document_exists_by_id(
        document: Optional[IdentityDocumentResponseSchema],
        original_id: int,
    ) -> IdentityDocumentResponseSchema:
        """
        Checks if an identity document exists by its ID.

        Args:
            document: The identity document object returned from the repository or None.
            original_id: The ID that was requested.

        Returns:
            The identity document object if it exists.

        Raises:
            NoInstanceFoundError: If the identity document was not found.
        """
        if document:
            return document

        raise NoInstanceFoundError(
            status_code=404,
            detail=_("Identity document with ID: %(ID)s was not found.")
            % {"ID": original_id},
        )

    async def get_by_id(
        self,
        document_id: int,
    ) -> IdentityDocumentResponseSchema:
        document: Optional[IdentityDocumentResponseSchema] = (
            await self._identity_documents_repository.get_by_id(document_id)
        )

        return self._check_identity_document_exists_by_id(document, document_id)

    async def get_identity_documents(
        self,
        pagination_params: PaginationParams,
        filters: IdentityDocumentsCatalogFilterParams,
    ) -> MultipleIdentityDocumentsCatalogResponseSchema:
        page: int = pagination_params.page or 1  # for mypy
        limit: int = pagination_params.limit or 30  # for mypy

        items: List[IdentityDocumentResponseSchema] = (
            await self._identity_documents_repository.get_identity_documents(
                page=page,
                limit=limit,
                filters=filters.to_dict(exclude_none=True),
            )
        )

        total_items = (
            await self._identity_documents_repository.get_total_number_of_identity_documents()
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

        return MultipleIdentityDocumentsCatalogResponseSchema(
            items=items,
            pagination=pagination,
        )

    async def add_identity_document(
        self, request_dto: AddIdentityDocumentRequestSchema
    ) -> IdentityDocumentResponseSchema:
        # Check that patient exists
        await self._patient_service.get_by_id(request_dto.patient_id)

        return await self._identity_documents_repository.add_identity_document(
            request_dto
        )

    async def update_identity_document(
        self,
        document_id: int,
        request_dto: UpdateIdentityDocumentRequestSchema,
    ) -> IdentityDocumentResponseSchema:
        # Check that patient exists
        if request_dto.patient_id:
            await self._patient_service.get_by_id(request_dto.patient_id)

        existing = await self._identity_documents_repository.get_by_id(document_id)
        self._check_identity_document_exists_by_id(existing, document_id)

        updated = await self._identity_documents_repository.update_identity_document(
            document_id, request_dto
        )

        return updated

    async def delete_by_id(self, document_id: int) -> None:
        existing = await self._identity_documents_repository.get_by_id(document_id)
        self._check_identity_document_exists_by_id(existing, document_id)

        await self._identity_documents_repository.delete_by_id(document_id)
