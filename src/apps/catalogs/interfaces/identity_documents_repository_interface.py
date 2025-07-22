from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.apps.catalogs.infrastructure.api.schemas.requests.identity_documents_catalog_request_schemas import (
    AddIdentityDocumentRequestSchema,
    UpdateIdentityDocumentRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.identity_documents_catalog_response_schemas import (
    IdentityDocumentResponseSchema,
)


class IdentityDocumentsCatalogRepositoryInterface(ABC):
    @abstractmethod
    async def get_total_number_of_identity_documents(self) -> int:
        """
        Retrieve a number of ALL identity documents from the Registry Service DB.

        :return: Number of ALL identity documents from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, document_id: int
    ) -> Optional[IdentityDocumentResponseSchema]:
        """
        Retrieve an identity document by its unique identifier.

        :param document_id: Unique identifier of the identity document.
        :return: Identity document instance or None if not found.
        """
        pass

    @abstractmethod
    async def get_identity_documents(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 30,
    ) -> List[IdentityDocumentResponseSchema]:
        """
        Retrieve a list of identity documents records, filtered if needed.

        ::param filters: Parameters to filter records by.
        :param page: Pagination page parameter.
        :param limit: Pagination limit (per page) parameter.

        :return: List of matching identity documents records.
        """
        pass

    @abstractmethod
    async def add_identity_document(
        self, request_dto: AddIdentityDocumentRequestSchema
    ) -> IdentityDocumentResponseSchema:
        """
        Add a new identity document record to the catalog.

        :param request_dto: Data for creating a new identity document record.

        :return: The created identity document record.
        """
        pass

    @abstractmethod
    async def update_identity_document(
        self, document_id: int, request_dto: UpdateIdentityDocumentRequestSchema
    ) -> IdentityDocumentResponseSchema:
        """
        Update an existing identity document record.

        :param document_id: Identity document record ID to update.
        :param request_dto: Data for updating an identity document record.

        :return: The updated identity document record.
        """
        pass

    @abstractmethod
    async def delete_by_id(self, document_id: int) -> None:
        """
        Delete an identity document record by its unique identifier.

        :param document_id: Unique identifier of the identity document record to delete.
        :return: None
        """
        pass
