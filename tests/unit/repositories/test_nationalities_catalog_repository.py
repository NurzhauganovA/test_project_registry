import math
import datetime

import pytest
from unittest.mock import AsyncMock

from src.apps.catalogs.infrastructure.api.schemas.requests.nationalities_catalog_request_schemas import (
    AddNationalitySchema,
    UpdateNationalitySchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.nationalities_catalog_response_schemas import (
    NationalityCatalogFullResponseSchema,
    NationalityCatalogPartialResponseSchema,
    MultipleNationalitiesCatalogSchema,
)
from src.shared.schemas.pagination_schemas import PaginationParams
from src.shared.exceptions import NoInstanceFoundError, InstanceAlreadyExistsError


@pytest.mark.asyncio
async def test_get_by_id_not_found(nationalities_catalog_service, nationalities_catalog_repository):
    nationalities_catalog_repository.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NoInstanceFoundError):
        await nationalities_catalog_service.get_by_id(123, include_all_locales=False)
    nationalities_catalog_repository.get_by_id.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_get_by_id_include_all_locales(nationalities_catalog_service, nationalities_catalog_repository):
    now = datetime.datetime.now(datetime.UTC)
    full = NationalityCatalogFullResponseSchema.model_construct(
        id=7,
        name="Русский",
        lang="ru",
        name_locales={"en": "Russian"},
        created_at=now,
        changed_at=now,
    )
    nationalities_catalog_repository.get_by_id = AsyncMock(return_value=full)

    out = await nationalities_catalog_service.get_by_id(7, include_all_locales=True)
    assert out is full
    nationalities_catalog_repository.get_by_id.assert_awaited_once_with(7)


@pytest.mark.asyncio
async def test_get_by_id_partial(nationalities_catalog_service, nationalities_catalog_repository):
    now = datetime.datetime.now(datetime.UTC)
    full = NationalityCatalogFullResponseSchema.model_construct(
        id=8,
        name="Русский",
        lang="ru",
        name_locales={"en": "Russian"},
        created_at=now,
        changed_at=now,
    )
    nationalities_catalog_repository.get_by_id = AsyncMock(return_value=full)

    out = await nationalities_catalog_service.get_by_id(8, include_all_locales=False)
    assert isinstance(out, NationalityCatalogPartialResponseSchema)
    assert out.lang == "en"
    assert out.name == "Russian"
    assert out.created_at == now
    assert out.changed_at == now


@pytest.mark.asyncio
async def test_get_nationalities_pagination(nationalities_catalog_service, nationalities_catalog_repository):
    now = datetime.datetime.now(datetime.UTC)
    full_items = [
        NationalityCatalogFullResponseSchema.model_construct(
            id=1,
            name="Русский",
            lang="ru",
            name_locales={"en": "Russian"},
            created_at=now,
            changed_at=now,
        ),
        NationalityCatalogFullResponseSchema.model_construct(
            id=2,
            name="English",
            lang="en",
            name_locales={},
            created_at=now,
            changed_at=now,
        ),
    ]
    nationalities_catalog_repository.get_nationalities = AsyncMock(return_value=full_items)
    nationalities_catalog_repository.get_total_number_of_nationalities = AsyncMock(return_value=5)

    params = PaginationParams(page=1, limit=2)
    result = await nationalities_catalog_service.get_nationalities(
        pagination_params=params,
        name_filter="Рус",
        include_all_locales=False,
    )

    assert isinstance(result, MultipleNationalitiesCatalogSchema)
    assert len(result.items) == 2
    assert result.items[0].lang == "en"
    assert result.items[0].name == "Russian"

    assert result.pagination.current_page == 1
    assert result.pagination.per_page == 2
    assert result.pagination.total_items == 5
    assert result.pagination.total_pages == math.ceil(5 / 2)
    assert result.pagination.has_next is True
    assert result.pagination.has_prev is False

    result2 = await nationalities_catalog_service.get_nationalities(
        pagination_params=params,
        name_filter=None,
        include_all_locales=True,
    )
    assert result2.items == full_items


@pytest.mark.asyncio
async def test_create_nationality_conflicts_and_success(nationalities_catalog_service, nationalities_catalog_repository):
    dto = AddNationalitySchema.model_construct(
        name="Русский",
        lang="ru",
        name_locales={"en": "Russian"},
    )
    nationalities_catalog_repository.get_by_default_name = AsyncMock(return_value=True)
    with pytest.raises(InstanceAlreadyExistsError):
        await nationalities_catalog_service.add_nationality(dto)
    nationalities_catalog_repository.add_nationality.assert_not_called()

    nationalities_catalog_repository.get_by_default_name = AsyncMock(return_value=False)

    async def exists_locale(lang_code, val):
        return lang_code == "en" and val == "Russian"
    nationalities_catalog_repository.get_by_locale = AsyncMock(side_effect=exists_locale)

    with pytest.raises(InstanceAlreadyExistsError):
        await nationalities_catalog_service.add_nationality(dto)
    nationalities_catalog_repository.add_nationality.assert_not_called()

    nationalities_catalog_repository.get_by_locale = AsyncMock(return_value=False)
    fake_full = NationalityCatalogFullResponseSchema.model_construct(
        id=10,
        name="Русский",
        lang="ru",
        name_locales={"en": "Russian"},
        created_at=datetime.datetime.now(datetime.UTC),
        changed_at=datetime.datetime.now(datetime.UTC),
    )
    nationalities_catalog_repository.add_nationality = AsyncMock(return_value=fake_full)

    out = await nationalities_catalog_service.add_nationality(dto)
    assert out is fake_full
    nationalities_catalog_repository.add_nationality.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_update_nationality_all_branches(nationalities_catalog_service, nationalities_catalog_repository):
    nationalities_catalog_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await nationalities_catalog_service.update_nationality(5, UpdateNationalitySchema.model_construct())

    now = datetime.datetime.now(datetime.UTC)
    existing = NationalityCatalogFullResponseSchema.model_construct(
        id=6, name="Old", lang="en", name_locales={}, created_at=now, changed_at=now
    )
    nationalities_catalog_repository.get_by_id.return_value = existing

    with pytest.raises(ValueError):
        await nationalities_catalog_service.update_nationality(
            6, UpdateNationalitySchema.model_construct(lang="ru")
        )

    nationalities_catalog_repository.get_by_default_name.return_value = True
    with pytest.raises(InstanceAlreadyExistsError):
        await nationalities_catalog_service.update_nationality(
            6, UpdateNationalitySchema.model_construct(name="NewName")
        )

    nationalities_catalog_repository.get_by_default_name.return_value = False
    async def exists_locale(code, val):
        return code == "en" and val == "Conflict"
    nationalities_catalog_repository.get_by_locale.side_effect = exists_locale

    existing.name_locales = {"en": "Existing"}
    with pytest.raises(InstanceAlreadyExistsError):
        await nationalities_catalog_service.update_nationality(
            6, UpdateNationalitySchema.model_construct(name_locales={"en": "Conflict"})
        )

    nationalities_catalog_repository.get_by_locale.return_value = False
    fake_updated = NationalityCatalogFullResponseSchema.model_construct(
        id=6, name="Updated", lang="en", name_locales={}, created_at=existing.created_at, changed_at=existing.changed_at
    )
    nationalities_catalog_repository.update_nationality.return_value = fake_updated

    out = await nationalities_catalog_service.update_nationality(
        6, UpdateNationalitySchema.model_construct(name="Updated")
    )
    assert out is fake_updated
    nationalities_catalog_repository.update_nationality.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_nationality_by_id(nationalities_catalog_service, nationalities_catalog_repository):
    nationalities_catalog_repository.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(NoInstanceFoundError):
        await nationalities_catalog_service.delete_by_id(42)

    now = datetime.datetime.now(datetime.UTC)
    existing = NationalityCatalogFullResponseSchema.model_construct(
        id=9,
        name="Русский",
        lang="ru",
        name_locales={},
        created_at=now,
        changed_at=now,
    )
    nationalities_catalog_repository.get_by_id = AsyncMock(return_value=existing)
    nationalities_catalog_repository.delete_by_id = AsyncMock()

    await nationalities_catalog_service.delete_by_id(9)
    nationalities_catalog_repository.delete_by_id.assert_awaited_once_with(9)
