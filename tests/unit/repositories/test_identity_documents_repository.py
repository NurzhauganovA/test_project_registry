import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.mark.asyncio
async def test_get_total_number_of_identity_documents(identity_documents_repository_impl):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one.return_value = 42
    identity_documents_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    result = await identity_documents_repository_impl.get_total_number_of_identity_documents()
    assert result == 42


@pytest.mark.asyncio
async def test_get_by_id_found(
        identity_documents_repository_impl,
        mock_identity_document_db_entity,
        mock_identity_document_response_schema
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one_or_none.return_value = mock_identity_document_db_entity
    identity_documents_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    with patch(
            "src.apps.catalogs.infrastructure.repositories.identity_documents_catalog_repository.map_identity_document_db_entity_to_response_schema",
            return_value=mock_identity_document_response_schema
    ):
        result = await identity_documents_repository_impl.get_by_id(1)
    assert isinstance(result, type(mock_identity_document_response_schema))
    assert result.id == mock_identity_document_response_schema.id


@pytest.mark.asyncio
async def test_get_by_id_not_found(identity_documents_repository_impl):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one_or_none.return_value = None
    identity_documents_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    result = await identity_documents_repository_impl.get_by_id(1)
    assert result is None


@pytest.mark.asyncio
async def test_get_identity_documents_WITHOUT_filters(
        identity_documents_repository_impl,
        mock_identity_document_db_entity,
        mock_identity_document_response_schema
):
    dummy_1 = mock_identity_document_db_entity
    dummy_2 = MagicMock(**{**dummy_1.__dict__, 'id': 2})

    mock_response_from_db = MagicMock()
    mock_response_from_db.scalars.return_value.all.return_value = [dummy_1, dummy_2]
    identity_documents_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    with patch(
            "src.apps.catalogs.infrastructure.repositories.identity_documents_catalog_repository.map_identity_document_db_entity_to_response_schema",
            return_value=mock_identity_document_response_schema
    ):
        result = await identity_documents_repository_impl.get_identity_documents(filters=None)
    assert isinstance(result, list)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_identity_documents_WITH_filters(
        identity_documents_repository_impl,
        mock_identity_document_db_entity,
        mock_identity_document_response_schema
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalars.return_value.all.return_value = [mock_identity_document_db_entity]
    identity_documents_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    filters = {
        'patient_id': mock_identity_document_db_entity.patient_id,
        'type': mock_identity_document_db_entity.type,
        'series': mock_identity_document_db_entity.series,
        'number': mock_identity_document_db_entity.number,
        'only_active': True
    }

    with patch(
            "src.apps.catalogs.infrastructure.repositories.identity_documents_catalog_repository.map_identity_document_db_entity_to_response_schema",
            return_value=mock_identity_document_response_schema
    ):
        result = await identity_documents_repository_impl.get_identity_documents(filters=filters)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == mock_identity_document_db_entity.id


@pytest.mark.asyncio
async def test_add_identity_document(
        identity_documents_repository_impl,
        mock_add_identity_document_schema,
        mock_identity_document_response_schema
):
    mock_orm_obj = MagicMock()
    # Patch mappers and session methods
    with patch(
            "src.apps.catalogs.infrastructure.repositories.identity_documents_catalog_repository.map_identity_document_create_schema_to_db_entity",
            return_value=mock_orm_obj
    ), patch(
        "src.apps.catalogs.infrastructure.repositories.identity_documents_catalog_repository.map_identity_document_db_entity_to_response_schema",
        return_value=mock_identity_document_response_schema
    ):
        identity_documents_repository_impl._async_db_session.add = MagicMock()
        identity_documents_repository_impl._async_db_session.flush = AsyncMock()
        identity_documents_repository_impl._async_db_session.refresh = AsyncMock()
        identity_documents_repository_impl._async_db_session.commit = AsyncMock()

        result = await identity_documents_repository_impl.add_identity_document(mock_add_identity_document_schema)

    assert isinstance(result, type(mock_identity_document_response_schema))
    identity_documents_repository_impl._async_db_session.add.assert_called_once_with(mock_orm_obj)
    identity_documents_repository_impl._async_db_session.flush.assert_awaited_once()
    identity_documents_repository_impl._async_db_session.refresh.assert_awaited_once_with(mock_orm_obj)
    identity_documents_repository_impl._async_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_identity_document(
        identity_documents_repository_impl,
        mock_update_identity_document_schema,
        mock_identity_document_db_entity,
        mock_identity_document_response_schema
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_identity_document_db_entity
    identity_documents_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_result)

    identity_documents_repository_impl._async_db_session.flush = AsyncMock()
    identity_documents_repository_impl._async_db_session.refresh = AsyncMock()
    identity_documents_repository_impl._async_db_session.commit = AsyncMock()

    with patch(
            "src.apps.catalogs.infrastructure.repositories.identity_documents_catalog_repository.map_identity_document_update_schema_to_db_entity",
            return_value=mock_identity_document_db_entity
    ), patch(
        "src.apps.catalogs.infrastructure.repositories.identity_documents_catalog_repository.map_identity_document_db_entity_to_response_schema",
        return_value=mock_identity_document_response_schema
    ):
        result = await identity_documents_repository_impl.update_identity_document(
            document_id=mock_identity_document_db_entity.id,
            request_dto=mock_update_identity_document_schema
        )

    assert isinstance(result, type(mock_identity_document_response_schema))
    identity_documents_repository_impl._async_db_session.flush.assert_awaited_once()
    identity_documents_repository_impl._async_db_session.refresh.assert_awaited_once_with(
        mock_identity_document_db_entity)
    identity_documents_repository_impl._async_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id(identity_documents_repository_impl):
    identity_documents_repository_impl._async_db_session.execute = AsyncMock(return_value=None)
    identity_documents_repository_impl._async_db_session.commit = AsyncMock()

    await identity_documents_repository_impl.delete_by_id(1)

    identity_documents_repository_impl._async_db_session.commit.assert_awaited_once()
