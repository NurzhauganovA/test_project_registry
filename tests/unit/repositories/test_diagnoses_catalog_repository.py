from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import \
    DiagnosesCatalogResponseSchema


@pytest.mark.asyncio
async def test_get_total_number_of_diagnoses(
        diagnoses_catalog_repository_impl
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one.return_value = 34
    diagnoses_catalog_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    result = await diagnoses_catalog_repository_impl.get_total_number_of_diagnoses()

    assert isinstance(result, int)
    assert result == 34


@pytest.mark.asyncio
async def test_get_by_id_found(
        diagnoses_catalog_repository_impl,
        mock_diagnoses_catalog_response_from_db,
        mock_diagnoses_catalog_response_schema
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one_or_none.return_value = mock_diagnoses_catalog_response_from_db
    diagnoses_catalog_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    # Patch the mapper
    with patch(
            "src.apps.catalogs.infrastructure.repositories.diagnoses_catalog_repository.map_diagnosis_catalog_db_entity_to_response_schema",
            return_value=mock_diagnoses_catalog_response_schema
    ):
        result = await diagnoses_catalog_repository_impl.get_by_id(12)

    assert isinstance(result, type(mock_diagnoses_catalog_response_schema))
    assert result.id == mock_diagnoses_catalog_response_from_db.id
    assert result.diagnosis_code == mock_diagnoses_catalog_response_from_db.diagnosis_code


@pytest.mark.asyncio
async def test_get_by_id_not_found(
        diagnoses_catalog_repository_impl,
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one_or_none.return_value = None
    diagnoses_catalog_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    result = await diagnoses_catalog_repository_impl.get_by_id(1)

    assert result is None


@pytest.mark.asyncio
async def test_get_by_code_found(
        diagnoses_catalog_repository_impl,
        mock_diagnoses_catalog_response_from_db,
        mock_diagnoses_catalog_response_schema
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one_or_none.return_value = mock_diagnoses_catalog_response_from_db
    diagnoses_catalog_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    # Patch the mapper
    with patch(
            "src.apps.catalogs.infrastructure.repositories.diagnoses_catalog_repository.map_diagnosis_catalog_db_entity_to_response_schema",
            return_value=mock_diagnoses_catalog_response_schema
    ):
        result = await diagnoses_catalog_repository_impl.get_by_code('AJ-09')

    assert isinstance(result, type(mock_diagnoses_catalog_response_schema))
    assert result.id == mock_diagnoses_catalog_response_from_db.id
    assert result.diagnosis_code == mock_diagnoses_catalog_response_from_db.diagnosis_code


@pytest.mark.asyncio
async def test_get_by_code_not_found(
        diagnoses_catalog_repository_impl,
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one_or_none.return_value = None
    diagnoses_catalog_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    result = await diagnoses_catalog_repository_impl.get_by_code('МКБ-11')

    assert result is None


@pytest.mark.asyncio
async def test_get_diagnoses_WITHOUT_filters(
        diagnoses_catalog_repository_impl,
        mock_diagnoses_catalog_response_from_db,
        mock_diagnoses_catalog_response_schema
):
    # Dummy responses
    dummy_diagnosis_response_1 = mock_diagnoses_catalog_response_from_db
    dummy_diagnosis_response_2 = mock_diagnoses_catalog_response_from_db

    # Make them different
    dummy_diagnosis_response_2.id = 13
    dummy_diagnosis_response_2.diagnosis_code = 'МКБ-24'

    mock_response_from_db = MagicMock()
    mock_response_from_db.scalars.return_value.all.return_value = [
        dummy_diagnosis_response_1,
        dummy_diagnosis_response_2
    ]
    diagnoses_catalog_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    result = await diagnoses_catalog_repository_impl.get_diagnoses(
        diagnosis_code_filter=None,
    )

    assert isinstance(result, list)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_diagnoses_WITH_filters_and_pagination(
        diagnoses_catalog_repository_impl,
        mock_diagnoses_catalog_response_from_db,
        mock_diagnoses_catalog_response_schema
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalars.return_value.all.return_value = [
        mock_diagnoses_catalog_response_from_db
    ]
    diagnoses_catalog_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    result = await diagnoses_catalog_repository_impl.get_diagnoses(
        diagnosis_code_filter='AJ-09',
        page=1,
        limit=1,
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].diagnosis_code == 'AJ-09'


@pytest.mark.asyncio
async def test_add_diagnoses(
        diagnoses_catalog_repository_impl,
        mock_diagnoses_catalog_response_from_db,
        mock_diagnoses_catalog_response_schema,
        mock_diagnoses_catalog_add_schema,
):
    mock_orm_obj = MagicMock()
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one_or_none.return_value = mock_diagnoses_catalog_response_schema,
    diagnoses_catalog_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    # Mock the session's methods
    diagnoses_catalog_repository_impl._async_db_session.add = MagicMock()
    diagnoses_catalog_repository_impl._async_db_session.flush = AsyncMock()
    diagnoses_catalog_repository_impl._async_db_session.refresh = AsyncMock()
    diagnoses_catalog_repository_impl._async_db_session.commit = AsyncMock()

    # Patch the mappers
    with patch(
        "src.apps.catalogs.infrastructure.repositories.diagnoses_catalog_repository.map_diagnosis_catalog_create_schema_to_db_entity",
        return_value=mock_orm_obj
    ), patch(
        "src.apps.catalogs.infrastructure.repositories.diagnoses_catalog_repository.map_diagnosis_catalog_db_entity_to_response_schema",
        return_value=mock_diagnoses_catalog_response_schema
    ):
        result = await diagnoses_catalog_repository_impl.add_diagnosis(mock_diagnoses_catalog_add_schema)

    assert isinstance(result, type(mock_diagnoses_catalog_response_schema))
    assert result.diagnosis_code == mock_diagnoses_catalog_response_schema.diagnosis_code
    assert result.description == mock_diagnoses_catalog_response_schema.description
    assert result.is_active == mock_diagnoses_catalog_response_schema.is_active

    diagnoses_catalog_repository_impl._async_db_session.add.assert_called_once_with(mock_orm_obj)
    diagnoses_catalog_repository_impl._async_db_session.flush.assert_awaited_once()
    diagnoses_catalog_repository_impl._async_db_session.refresh.assert_awaited_once_with(mock_orm_obj)
    diagnoses_catalog_repository_impl._async_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_diagnosis(
    diagnoses_catalog_repository_impl,
    mock_diagnoses_catalog_update_schema,
    mock_diagnoses_catalog_response_schema,
    mock_diagnoses_catalog_response_from_db,
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_diagnoses_catalog_response_from_db
    diagnoses_catalog_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_result)

    # Mock the session's methods
    diagnoses_catalog_repository_impl._async_db_session.flush = AsyncMock()
    diagnoses_catalog_repository_impl._async_db_session.refresh = AsyncMock()
    diagnoses_catalog_repository_impl._async_db_session.commit = AsyncMock()

    # Patch the mappers
    def mapper_side_effect(db_entity):
        return DiagnosesCatalogResponseSchema(
            id=db_entity.id,
            diagnosis_code=db_entity.diagnosis_code,
            description=db_entity.description,
            is_active=db_entity.is_active,
        )

    with patch(
        "src.apps.catalogs.infrastructure.repositories.diagnoses_catalog_repository.map_diagnosis_catalog_db_entity_to_response_schema",
        side_effect=mapper_side_effect
    ):
        result = await diagnoses_catalog_repository_impl.update_diagnosis(
            diagnosis_id=mock_diagnoses_catalog_response_from_db.id,
            request_dto=mock_diagnoses_catalog_update_schema
        )

    # Check that the ORM object fields have been updated according to request_dto (exclude_unset=True)
    update_data = mock_diagnoses_catalog_update_schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        assert getattr(mock_diagnoses_catalog_response_from_db, key) == value

    assert isinstance(result, type(mock_diagnoses_catalog_response_schema))
    assert result.description == mock_diagnoses_catalog_update_schema.description
    assert result.is_active == mock_diagnoses_catalog_update_schema.is_active

    diagnoses_catalog_repository_impl._async_db_session.flush.assert_awaited_once()
    diagnoses_catalog_repository_impl._async_db_session.refresh.assert_awaited_once_with(
        mock_diagnoses_catalog_response_from_db
    )
    diagnoses_catalog_repository_impl._async_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id(
        diagnoses_catalog_repository_impl,
):
    diagnoses_catalog_repository_impl._async_db_session.execute = AsyncMock(return_value=None)

    # Mock the session method
    diagnoses_catalog_repository_impl._async_db_session.commit = AsyncMock()

    await diagnoses_catalog_repository_impl.delete_by_id(12)

    diagnoses_catalog_repository_impl._async_db_session.commit.assert_awaited_once()

