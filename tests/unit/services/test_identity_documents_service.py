import math
import uuid
from unittest.mock import MagicMock

import pytest

from src.apps.catalogs.enums import IdentityDocumentTypeEnum
from src.apps.catalogs.infrastructure.api.schemas.requests.filters.identity_documents_catalog_filters import \
    IdentityDocumentsCatalogFilterParams
from src.apps.catalogs.infrastructure.api.schemas.responses.identity_documents_catalog_response_schemas import (
    MultipleIdentityDocumentsCatalogResponseSchema
)
from src.shared.exceptions import NoInstanceFoundError
from src.shared.schemas.pagination_schemas import PaginationParams


@pytest.mark.asyncio
async def test_get_by_id_found(
        identity_documents_service,
        mock_identity_documents_repository,
        mock_identity_document_response_schema
):
    mock_identity_documents_repository.get_by_id.return_value = mock_identity_document_response_schema
    out = await identity_documents_service.get_by_id(1)
    assert out is mock_identity_document_response_schema


@pytest.mark.asyncio
async def test_get_by_id_not_found(identity_documents_service, mock_identity_documents_repository):
    mock_identity_documents_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await identity_documents_service.get_by_id(1)


@pytest.mark.asyncio
async def test_get_identity_documents_with_pagination(
        identity_documents_service, 
        mock_identity_documents_repository,
        mock_identity_document_response_schema,
):
    mock_identity_documents_repository.get_identity_documents.return_value = [mock_identity_document_response_schema]
    mock_identity_documents_repository.get_total_number_of_identity_documents.return_value = 5

    mock_pagination_params = PaginationParams(
        limit=10,
        page=1
    )

    mock_identity_catalog_filters = IdentityDocumentsCatalogFilterParams(
        by_patient_id=None,
        by_type=IdentityDocumentTypeEnum.ID_CARD,
        by_series=None,
        by_number=None,
        only_active=True
    )

    result = await identity_documents_service.get_identity_documents(
        pagination_params=mock_pagination_params,
        filters=mock_identity_catalog_filters
    )
    assert isinstance(result, MultipleIdentityDocumentsCatalogResponseSchema)
    assert len(result.items) == 1
    assert result.pagination.current_page == mock_pagination_params.page
    assert result.pagination.per_page == mock_pagination_params.limit
    assert result.pagination.total_items == 5
    assert result.pagination.total_pages == math.ceil(5 / mock_pagination_params.limit)
    assert result.pagination.has_next is False
    assert result.pagination.has_prev is False


@pytest.mark.asyncio
async def test_add_identity_document_calls_patient_check(
        identity_documents_service, 
        mock_patient_service,
        mock_add_identity_document_schema,
        mock_identity_documents_repository,
        mock_identity_document_response_schema
):
    mock_patient_service.get_by_id.return_value = MagicMock()
    mock_identity_documents_repository.add_identity_document.return_value = mock_identity_document_response_schema

    result = await identity_documents_service.add_identity_document(mock_add_identity_document_schema)
    assert result is mock_identity_document_response_schema
    mock_patient_service.get_by_id.assert_awaited_once_with(mock_add_identity_document_schema.patient_id)
    mock_identity_documents_repository.add_identity_document.assert_awaited_once_with(mock_add_identity_document_schema)


@pytest.mark.asyncio
async def test_update_identity_document_with_patient_id(
        identity_documents_service, 
        mock_identity_documents_repository,
        mock_patient_service, 
        mock_identity_document_response_schema,
        mock_update_identity_document_schema
):
    mock_update_identity_document_schema.patient_id = uuid.uuid4()
    mock_identity_documents_repository.get_by_id.return_value = mock_identity_document_response_schema
    mock_identity_documents_repository.update_identity_document.return_value = mock_identity_document_response_schema
    mock_patient_service.get_by_id.return_value = MagicMock()

    result = await identity_documents_service.update_identity_document(1, mock_update_identity_document_schema)
    assert result is mock_identity_document_response_schema
    mock_patient_service.get_by_id.assert_awaited_once_with(mock_update_identity_document_schema.patient_id)
    mock_identity_documents_repository.update_identity_document.assert_awaited_once_with(
        1,
        mock_update_identity_document_schema
    )


@pytest.mark.asyncio
async def test_update_identity_document_without_patient_id(
        identity_documents_service,
        mock_identity_documents_repository,
        mock_update_identity_document_schema,
        mock_identity_document_response_schema
):
    mock_update_identity_document_schema.patient_id = None
    mock_identity_documents_repository.get_by_id.return_value = mock_identity_document_response_schema
    mock_identity_documents_repository.update_identity_document.return_value = mock_identity_document_response_schema

    result = await identity_documents_service.update_identity_document(1, mock_update_identity_document_schema)
    assert result is mock_identity_document_response_schema
    mock_identity_documents_repository.update_identity_document.assert_awaited_once_with(
        1,
        mock_update_identity_document_schema
    )


@pytest.mark.asyncio
async def test_update_identity_document_not_found(
        identity_documents_service, 
        mock_identity_documents_repository,
        mock_update_identity_document_schema
):
    mock_identity_documents_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await identity_documents_service.update_identity_document(1, mock_update_identity_document_schema)


@pytest.mark.asyncio
async def test_delete_by_id_success(
        identity_documents_service, 
        mock_identity_documents_repository,
        mock_identity_document_response_schema
):
    mock_identity_documents_repository.get_by_id.return_value = mock_identity_document_response_schema
    await identity_documents_service.delete_by_id(1)
    mock_identity_documents_repository.delete_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_by_id_not_found(identity_documents_service, mock_identity_documents_repository):
    mock_identity_documents_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await identity_documents_service.delete_by_id(1)
