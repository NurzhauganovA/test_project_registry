import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.apps.catalogs.infrastructure.db_models.financing_sources_catalogue import SQLAlchemyFinancingSourcesCatalog
from src.apps.catalogs.infrastructure.api.schemas.responses.financing_sources_catalog_response_schemas import (
    FinancingSourceFullResponseSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.financing_sources_catalog_request_schemas import (
    AddFinancingSourceSchema,
    UpdateFinancingSourceSchema,
)
from src.core.settings import project_settings


@pytest.mark.asyncio
async def test_get_by_default_name_returns_schema(
    financing_sources_catalog_repository,
    mock_async_db_session,
    dummy_financing_source_from_db,
):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(
            scalar_one_or_none=MagicMock(return_value=dummy_financing_source_from_db)
        )
    )
    with patch.object(
        FinancingSourceFullResponseSchema,
        "model_validate",
        return_value="SCHEMA_DEFAULT"
    ) as mv:
        out = await financing_sources_catalog_repository.get_by_default_name("DummyName")
        mv.assert_called_once_with(dummy_financing_source_from_db)
        assert out == "SCHEMA_DEFAULT"

    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_default_name_not_found(
    financing_sources_catalog_repository,
    mock_async_db_session,
):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    out = await financing_sources_catalog_repository.get_by_default_name("Missing")
    assert out is None
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_name_locale_returns_schema(
    financing_sources_catalog_repository,
    mock_async_db_session,
    dummy_financing_source_from_db,
):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(
            scalar_one_or_none=MagicMock(return_value=dummy_financing_source_from_db)
        )
    )
    with patch.object(
        FinancingSourceFullResponseSchema,
        "model_validate",
        return_value="SCHEMA_LOCALE"
    ) as mv:
        out = await financing_sources_catalog_repository.get_by_name_locale("kk", "DummyName_KK")
        mv.assert_called_once_with(dummy_financing_source_from_db)
        assert out == "SCHEMA_LOCALE"

    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_name_locale_not_found(
    financing_sources_catalog_repository,
    mock_async_db_session,
):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    out = await financing_sources_catalog_repository.get_by_name_locale("kk", "Nope")
    assert out is None
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_financing_source_code_returns_schema(
    financing_sources_catalog_repository,
    mock_async_db_session,
    dummy_financing_source_from_db,
):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(
            scalar_one_or_none=MagicMock(return_value=dummy_financing_source_from_db)
        )
    )
    with patch.object(
        FinancingSourceFullResponseSchema,
        "model_validate",
        return_value="SCHEMA_CODE"
    ) as mv:
        out = await financing_sources_catalog_repository.get_by_financing_source_code("DummyCode")
        mv.assert_called_once_with(dummy_financing_source_from_db)
        assert out == "SCHEMA_CODE"

    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_financing_source_code_not_found(
    financing_sources_catalog_repository,
    mock_async_db_session,
):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    out = await financing_sources_catalog_repository.get_by_financing_source_code("XYZ")
    assert out is None
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_total_number_of_financing_sources(
    financing_sources_catalog_repository,
    mock_async_db_session,
):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one=MagicMock(return_value=42))
    )
    total = await financing_sources_catalog_repository.get_total_number_of_financing_sources()
    assert total == 42
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_found_and_not_found(
    financing_sources_catalog_repository,
    mock_async_db_session,
    dummy_financing_source_from_db,
):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(
            scalar_one_or_none=MagicMock(return_value=dummy_financing_source_from_db)
        )
    )
    with patch.object(
        FinancingSourceFullResponseSchema,
        "model_validate",
        return_value="FOUND"
    ) as mv:
        found = await financing_sources_catalog_repository.get_by_id(7)
        mv.assert_called_once_with(dummy_financing_source_from_db)
        assert found == "FOUND"

    mock_async_db_session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=None)
    )
    not_found = await financing_sources_catalog_repository.get_by_id(999)
    assert not_found is None


@pytest.mark.asyncio
async def test_get_financing_sources_without_filters(
    financing_sources_catalog_repository,
    mock_async_db_session,
    dummy_financing_source_from_db,
):
    scalars = MagicMock(all=MagicMock(return_value=[dummy_financing_source_from_db]))
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=scalars))
    )
    with patch.object(
        FinancingSourceFullResponseSchema,
        "model_validate",
        side_effect=lambda x: x
    ):
        out = await financing_sources_catalog_repository.get_financing_sources(
            name_filter=None, code_filter=None, page=1, limit=10
        )
        assert isinstance(out, list)
        assert out[0] is dummy_financing_source_from_db


@pytest.mark.asyncio
async def test_get_financing_sources_with_filters(
    financing_sources_catalog_repository,
    mock_async_db_session,
    dummy_financing_source_from_db,
):
    scalars = MagicMock(all=MagicMock(return_value=[dummy_financing_source_from_db]))
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=scalars))
    )
    with patch.object(
        FinancingSourceFullResponseSchema,
        "model_validate",
        side_effect=lambda x: x
    ):
        project_settings.LANGUAGES = ["en", "kk"]
        out = await financing_sources_catalog_repository.get_financing_sources(
            name_filter=dummy_financing_source_from_db.name,
            code_filter=dummy_financing_source_from_db.code,
            page=2,
            limit=5
        )
        assert out == [dummy_financing_source_from_db]


@pytest.mark.asyncio
async def test_add_financing_source(
    financing_sources_catalog_repository,
    mock_async_db_session,
):
    dto = AddFinancingSourceSchema.model_construct(
        name="New",
        financing_source_code="NEW",
        lang="en",
        name_locales={"ru": "Н"},
    )
    mock_async_db_session.add = MagicMock()
    mock_async_db_session.flush = AsyncMock()
    mock_async_db_session.refresh = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    with patch.object(
        FinancingSourceFullResponseSchema,
        "model_validate",
        return_value="ADDED"
    ) as mv:
        out = await financing_sources_catalog_repository.add_financing_source(dto)
        mv.assert_called_once()
        added = mock_async_db_session.add.call_args[0][0]
        assert isinstance(added, SQLAlchemyFinancingSourcesCatalog)
        assert added.name == dto.name
        assert added.code == dto.financing_source_code
        assert added.lang == dto.lang
        assert added.name_locales == dto.name_locales
        assert out == "ADDED"

    mock_async_db_session.flush.assert_awaited_once()
    mock_async_db_session.refresh.assert_awaited_once_with(added)
    mock_async_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_financing_source(
    financing_sources_catalog_repository,
    mock_async_db_session,
    dummy_financing_source_from_db,
):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(
            scalar_one_or_none=MagicMock(return_value=dummy_financing_source_from_db)
        )
    )
    mock_async_db_session.flush = AsyncMock()
    mock_async_db_session.refresh = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    dto = UpdateFinancingSourceSchema.model_construct(
        name="Updated",
        financing_source_code="UPD",
        name_locales={},
    )
    with patch.object(
        FinancingSourceFullResponseSchema,
        "model_validate",
        return_value="UPDATED"
    ) as mv:
        out = await financing_sources_catalog_repository.update_financing_source(7, dto)
        assert dummy_financing_source_from_db.name_locales is None
        assert dummy_financing_source_from_db.name == "Updated"
        assert dummy_financing_source_from_db.code == "UPD"
        mv.assert_called_once_with(dummy_financing_source_from_db)
        assert out == "UPDATED"

    mock_async_db_session.flush.assert_awaited_once()
    mock_async_db_session.refresh.assert_awaited_once_with(dummy_financing_source_from_db)
    mock_async_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id(
    financing_sources_catalog_repository,
    mock_async_db_session,
):
    mock_async_db_session.execute = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    await financing_sources_catalog_repository.delete_by_id(99)
    mock_async_db_session.execute.assert_awaited_once()
    mock_async_db_session.commit.assert_awaited_once()
