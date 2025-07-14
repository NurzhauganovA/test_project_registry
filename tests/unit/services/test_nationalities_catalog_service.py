import math
import pytest
from datetime import datetime, timezone

from src.apps.catalogs.services.nationalities_catalog_service import NationalitiesCatalogService
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


def test___get_localized_name_various_cases():
    Full = NationalityCatalogFullResponseSchema
    now = datetime.now(timezone.utc)

    obj = Full.model_construct(
        id=1, name="Orig", lang="en", name_locales={"ru": "Рус"}, created_at=now, changed_at=now
    )
    got = NationalitiesCatalogService._NationalitiesCatalogService__get_localized_name(obj)
    assert got == "Orig"
    obj = Full.model_construct(
        id=2, name="Orig", lang="ru", name_locales={"en": "Translated"}, created_at=now, changed_at=now
    )
    got = NationalitiesCatalogService._NationalitiesCatalogService__get_localized_name(obj)
    assert got == "Translated"

    obj = Full.model_construct(
        id=3, name="Orig", lang="ru", name_locales={}, created_at=now, changed_at=now
    )
    got = NationalitiesCatalogService._NationalitiesCatalogService__get_localized_name(obj)
    assert got == "Orig"

    obj = Full.model_construct(
        id=4, name="Orig", lang="fr", name_locales={}, created_at=now, changed_at=now
    )
    got = NationalitiesCatalogService._NationalitiesCatalogService__get_localized_name(obj)
    assert got == "Orig"


@pytest.mark.asyncio
async def test_get_by_id_not_found_raises(nationalities_catalog_service, nationalities_catalog_repository):
    nationalities_catalog_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await nationalities_catalog_service.get_by_id(123, include_all_locales=False)


@pytest.mark.asyncio
async def test_get_by_id_include_all_locales_returns_full(nationalities_catalog_service,
                                                          nationalities_catalog_repository):
    now = datetime.now(timezone.utc)
    full = NationalityCatalogFullResponseSchema.model_construct(
        id=7, name="N", lang="en", name_locales={}, created_at=now, changed_at=now
    )
    nationalities_catalog_repository.get_by_id.return_value = full

    out = await nationalities_catalog_service.get_by_id(7, include_all_locales=True)
    assert out is full


@pytest.mark.asyncio
async def test_get_by_id_localized_partial(nationalities_catalog_service, nationalities_catalog_repository):
    now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    full = NationalityCatalogFullResponseSchema.model_construct(
        id=8,
        name="Orig",
        lang="ru",
        name_locales={"en": "EnName"},
        created_at=now,
        changed_at=now,
    )
    nationalities_catalog_repository.get_by_id.return_value = full

    partial = await nationalities_catalog_service.get_by_id(8, include_all_locales=False)
    assert isinstance(partial, NationalityCatalogPartialResponseSchema)
    assert partial.id == 8
    assert partial.lang == "en"
    assert partial.name == "EnName"
    assert partial.created_at == now
    assert partial.changed_at == now


@pytest.mark.asyncio
async def test_get_nationalities_pagination_and_locales(nationalities_catalog_service,
                                                        nationalities_catalog_repository):
    now = datetime.now(timezone.utc)
    full_items = [
        NationalityCatalogFullResponseSchema.model_construct(
            id=1, name="A", lang="ru", name_locales={"en": "A_en"}, created_at=now, changed_at=now
        ),
        NationalityCatalogFullResponseSchema.model_construct(
            id=2, name="B", lang="en", name_locales={}, created_at=now, changed_at=now
        ),
    ]
    nationalities_catalog_repository.get_nationalities.return_value = full_items
    nationalities_catalog_repository.get_total_number_of_nationalities.return_value = 5

    params = PaginationParams(page=1, limit=2)
    result = await nationalities_catalog_service.get_nationalities(
        pagination_params=params, name_filter="x", include_all_locales=False
    )

    assert isinstance(result, MultipleNationalitiesCatalogSchema)
    assert len(result.items) == 2
    assert result.items[0].name == "A_en"

    assert result.pagination.current_page == 1
    assert result.pagination.per_page == 2
    assert result.pagination.total_items == 5
    assert result.pagination.total_pages == math.ceil(5 / 2)
    assert result.pagination.has_next is True
    assert result.pagination.has_prev is False

    result2 = await nationalities_catalog_service.get_nationalities(
        pagination_params=params, name_filter=None, include_all_locales=True
    )
    assert result2.items == full_items


@pytest.mark.asyncio
async def test_add_nationality_name_conflict(nationalities_catalog_service, nationalities_catalog_repository):
    dto = AddNationalitySchema.model_construct(name="X", lang="en", name_locales={"ru": "Y"})
    nationalities_catalog_repository.get_by_default_name.return_value = True

    with pytest.raises(InstanceAlreadyExistsError):
        await nationalities_catalog_service.add_nationality(dto)
    nationalities_catalog_repository.add_nationality.assert_not_called()


@pytest.mark.asyncio
async def test_add_nationality_locale_conflict(nationalities_catalog_service, nationalities_catalog_repository):
    dto = AddNationalitySchema.model_construct(name="X", lang="en", name_locales={"ru": "Y"})
    nationalities_catalog_repository.get_by_default_name.return_value = False

    async def exists_locale(code, val):
        return code == "ru" and val == "Y"

    nationalities_catalog_repository.get_by_locale.side_effect = exists_locale

    with pytest.raises(InstanceAlreadyExistsError):
        await nationalities_catalog_service.add_nationality(dto)
    nationalities_catalog_repository.add_nationality.assert_not_called()


@pytest.mark.asyncio
async def test_add_nationality_success(nationalities_catalog_service, nationalities_catalog_repository):
    dto = AddNationalitySchema.model_construct(name="X", lang="en", name_locales={"ru": "Y"})
    nationalities_catalog_repository.get_by_default_name.return_value = False
    nationalities_catalog_repository.get_by_locale.return_value = False
    fake_full = NationalityCatalogFullResponseSchema.model_construct(
        id=10, name="X", lang="en", name_locales={"ru": "Y"}, created_at=datetime.now(timezone.utc),
        changed_at=datetime.now(timezone.utc)
    )
    nationalities_catalog_repository.add_nationality.return_value = fake_full

    out = await nationalities_catalog_service.add_nationality(dto)
    assert out is fake_full
    nationalities_catalog_repository.add_nationality.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_update_nationality_not_found(nationalities_catalog_service, nationalities_catalog_repository):
    nationalities_catalog_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await nationalities_catalog_service.update_nationality(5, UpdateNationalitySchema.model_construct())


@pytest.mark.asyncio
async def test_update_nationality_bad_lang(nationalities_catalog_service, nationalities_catalog_repository):
    now = datetime.now(timezone.utc)
    existing = NationalityCatalogFullResponseSchema.model_construct(
        id=6, name="N", lang="en", name_locales={}, created_at=now, changed_at=now
    )
    nationalities_catalog_repository.get_by_id.return_value = existing

    with pytest.raises(ValueError):
        await nationalities_catalog_service.update_nationality(
            6, UpdateNationalitySchema.model_construct(lang="ru")
        )


@pytest.mark.asyncio
async def test_update_nationality_name_conflict(nationalities_catalog_service, nationalities_catalog_repository):
    now = datetime.now(timezone.utc)
    existing = NationalityCatalogFullResponseSchema.model_construct(
        id=6, name="Old", lang="en", name_locales={}, created_at=now, changed_at=now
    )
    nationalities_catalog_repository.get_by_id.return_value = existing
    nationalities_catalog_repository.get_by_default_name.return_value = True

    with pytest.raises(InstanceAlreadyExistsError):
        await nationalities_catalog_service.update_nationality(
            6, UpdateNationalitySchema.model_construct(name="New")
        )


@pytest.mark.asyncio
async def test_update_nationality_locale_conflict(nationalities_catalog_service, nationalities_catalog_repository):
    now = datetime.now(timezone.utc)
    existing = NationalityCatalogFullResponseSchema.model_construct(
        id=6, name="Name", lang="en", name_locales={"ru": "R"}, created_at=now, changed_at=now
    )
    nationalities_catalog_repository.get_by_id.return_value = existing
    nationalities_catalog_repository.get_by_default_name.return_value = False

    dto = UpdateNationalitySchema.model_construct(name_locales={"ru": "R2", "en": "X"})

    async def exists_locale(code, val):
        return code == "en" and val == "X"

    nationalities_catalog_repository.get_by_locale.side_effect = exists_locale

    with pytest.raises(InstanceAlreadyExistsError):
        await nationalities_catalog_service.update_nationality(6, dto)


@pytest.mark.asyncio
async def test_update_nationality_success(nationalities_catalog_service, nationalities_catalog_repository):
    now = datetime.now(timezone.utc)
    existing = NationalityCatalogFullResponseSchema.model_construct(
        id=6, name="Old", lang="en", name_locales={}, created_at=now, changed_at=now
    )
    nationalities_catalog_repository.get_by_id.return_value = existing
    nationalities_catalog_repository.get_by_default_name.return_value = False
    nationalities_catalog_repository.get_by_locale.return_value = False
    fake_updated = NationalityCatalogFullResponseSchema.model_construct(
        id=6, name="New", lang="en", name_locales={}, created_at=existing.created_at, changed_at=existing.changed_at
    )
    nationalities_catalog_repository.update_nationality.return_value = fake_updated

    out = await nationalities_catalog_service.update_nationality(6, UpdateNationalitySchema.model_construct(name="New"))
    assert out is fake_updated
    nationalities_catalog_repository.update_nationality.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id_not_found(nationalities_catalog_service, nationalities_catalog_repository):
    nationalities_catalog_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await nationalities_catalog_service.delete_by_id(42)


@pytest.mark.asyncio
async def test_delete_by_id_success(nationalities_catalog_service, nationalities_catalog_repository):
    now = datetime.now(timezone.utc)
    existing = NationalityCatalogFullResponseSchema.model_construct(
        id=9, name="X", lang="en", name_locales={}, created_at=now, changed_at=now
    )
    nationalities_catalog_repository.get_by_id.return_value = existing

    await nationalities_catalog_service.delete_by_id(9)
    nationalities_catalog_repository.delete_by_id.assert_awaited_once_with(9)
