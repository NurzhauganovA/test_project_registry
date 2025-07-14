from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.apps.catalogs.infrastructure.api.schemas.requests.citizenship_catalog_request_schemas import (
    AddCitizenshipSchema,
    UpdateCitizenshipSchema
)
from src.apps.catalogs.infrastructure.api.schemas.responses.citizenship_catalog_response_schemas import (
    CitizenshipCatalogFullResponseSchema
)
from src.apps.catalogs.infrastructure.db_models.citizenship_catalogue import SQLAlchemyCitizenshipCatalogue


@pytest.mark.asyncio
async def test_get_by_id_found(mock_citizenship_catalog_repository, mock_async_db_session):
    obj = SQLAlchemyCitizenshipCatalogue(
        id=1,
        country_code="KZ",
        name="Казахстан",
        lang="ru",
        name_locales={"en": "Kazakhstan"},
        created_at=datetime.now(UTC),
        changed_at=datetime.now(UTC),
    )
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = obj
    mock_async_db_session.execute = AsyncMock(return_value=execute_result)

    result = await mock_citizenship_catalog_repository.get_by_id(1)

    assert isinstance(result, CitizenshipCatalogFullResponseSchema)
    assert result.id == 1
    assert result.country_code == "KZ"
    mock_async_db_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_citizenship_catalog_repository, mock_async_db_session):
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    mock_async_db_session.execute = AsyncMock(return_value=execute_result)

    result = await mock_citizenship_catalog_repository.get_by_id(999)
    assert result is None
    mock_async_db_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_by_country_code_found(mock_citizenship_catalog_repository, mock_async_db_session):
    obj = SQLAlchemyCitizenshipCatalogue(
        id=1,
        country_code="KZ",
        name="Казахстан",
        lang="ru",
        name_locales={"en": "Kazakhstan"},
        created_at=datetime.now(UTC),
        changed_at=datetime.now(UTC),
    )
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = obj
    mock_async_db_session.execute = AsyncMock(return_value=execute_result)

    result = await mock_citizenship_catalog_repository.get_by_country_code("KZ")
    assert isinstance(result, CitizenshipCatalogFullResponseSchema)
    assert result.country_code == "KZ"
    mock_async_db_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_by_country_code_not_found(mock_citizenship_catalog_repository, mock_async_db_session):
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    mock_async_db_session.execute = AsyncMock(return_value=execute_result)

    result = await mock_citizenship_catalog_repository.get_by_country_code("ZZ")
    assert result is None
    mock_async_db_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_citizenship_records(mock_citizenship_catalog_repository, mock_async_db_session):
    obj1 = SQLAlchemyCitizenshipCatalogue(
        id=1,
        country_code="KZ",
        name="Казахстан",
        lang="ru",
        name_locales={"en": "Kazakhstan"},
        created_at=datetime.now(UTC),
        changed_at=datetime.now(UTC),
    )
    obj2 = SQLAlchemyCitizenshipCatalogue(
        id=1,
        country_code="RU",
        name="Россия",
        lang="ru",
        name_locales={"en": "Russia"},
        created_at=datetime.now(UTC),
        changed_at=datetime.now(UTC),
    )

    scalars_result = MagicMock()
    scalars_result.all.return_value = [obj1, obj2]
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_result
    mock_async_db_session.execute = AsyncMock(return_value=execute_result)

    result = await mock_citizenship_catalog_repository.get_citizenship_records(name_filter="", country_code_filter="")

    assert isinstance(result, list)
    assert all(isinstance(r, CitizenshipCatalogFullResponseSchema) for r in result)
    assert result[0].country_code == "KZ"
    assert result[1].country_code == "RU"
    mock_async_db_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_add_citizenship(mock_citizenship_catalog_repository, mock_async_db_session):
    add_dto = AddCitizenshipSchema.model_construct(
        country_code="BY",
        name="Беларусь",
        lang="ru",
        name_locales={"en": "Belarus"},
    )
    mock_async_db_session.flush = AsyncMock()
    mock_async_db_session.refresh = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    def fake_refresh(obj_in):
        obj_in.id = 3
        obj_in.created_at = datetime.now(UTC)
        obj_in.changed_at = datetime.now(UTC)

    mock_async_db_session.refresh.side_effect = fake_refresh

    result = await mock_citizenship_catalog_repository.add_citizenship(add_dto)

    assert isinstance(result, CitizenshipCatalogFullResponseSchema)
    assert result.country_code == "BY"
    mock_async_db_session.add.assert_called_once()
    mock_async_db_session.flush.assert_awaited()
    mock_async_db_session.refresh.assert_awaited()
    mock_async_db_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_update_citizenship(mock_citizenship_catalog_repository, mock_async_db_session):
    update_dto = UpdateCitizenshipSchema.model_construct(
        country_code="UA",
        name="Украина",
        lang="ru",
        name_locales={"en": "Ukraine"},
    )
    obj = SQLAlchemyCitizenshipCatalogue(
        id=1,
        country_code="KZ",
        name="Казахстан",
        lang="ru",
        name_locales={"en": "Kazakhstan"},
        created_at=datetime.now(UTC),
        changed_at=datetime.now(UTC),
    )
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = obj
    mock_async_db_session.execute = AsyncMock(return_value=execute_result)
    mock_async_db_session.flush = AsyncMock()
    mock_async_db_session.refresh = AsyncMock()

    result = await mock_citizenship_catalog_repository.update_citizenship(4, update_dto)

    assert isinstance(result, CitizenshipCatalogFullResponseSchema)
    assert result.country_code == "UA"
    mock_async_db_session.flush.assert_awaited()
    mock_async_db_session.refresh.assert_awaited()


@pytest.mark.asyncio
async def test_delete_citizenship_by_id(mock_citizenship_catalog_repository, mock_async_db_session):
    mock_async_db_session.execute = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    await mock_citizenship_catalog_repository.delete_by_id(5)

    mock_async_db_session.execute.assert_awaited()
    mock_async_db_session.commit.assert_awaited()
