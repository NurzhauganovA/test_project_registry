import math
import datetime
import pytest

from src.shared.exceptions import InstanceAlreadyExistsError, NoInstanceFoundError
from src.shared.schemas.pagination_schemas import PaginationParams
from src.apps.catalogs.infrastructure.api.schemas.requests.financing_sources_catalog_request_schemas import (
    AddFinancingSourceSchema,
    UpdateFinancingSourceSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.financing_sources_catalog_response_schemas import (
    FinancingSourceFullResponseSchema,
    FinancingSourcePartialResponseSchema,
    MultipleFinancingSourcesSchema,
)


@pytest.mark.asyncio
async def test_get_by_id_not_found(financing_sources_catalog_service, mock_financing_sources_catalog_repository):
    mock_financing_sources_catalog_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await financing_sources_catalog_service.get_by_id(123, include_all_locales=True)


@pytest.mark.asyncio
async def test_get_by_id_include_all(financing_sources_catalog_service, mock_financing_sources_catalog_repository, dummy_full_financing_source_schema):
    mock_financing_sources_catalog_repository.get_by_id.return_value = dummy_full_financing_source_schema

    out = await financing_sources_catalog_service.get_by_id(7, include_all_locales=True)
    assert out is dummy_full_financing_source_schema


@pytest.mark.asyncio
async def test_get_by_id_partial_default_locale(financing_sources_catalog_service, mock_financing_sources_catalog_repository, dummy_full_financing_source_schema):
    mock_financing_sources_catalog_repository.get_by_id.return_value = dummy_full_financing_source_schema

    partial = await financing_sources_catalog_service.get_by_id(7, include_all_locales=False)
    assert isinstance(partial, FinancingSourcePartialResponseSchema)
    assert partial.id == dummy_full_financing_source_schema.id
    assert partial.lang == "ru"
    assert partial.name == dummy_full_financing_source_schema.name_locales["ru"]
    assert partial.financing_source_code == dummy_full_financing_source_schema.financing_source_code
    assert partial.created_at == dummy_full_financing_source_schema.created_at
    assert partial.changed_at == dummy_full_financing_source_schema.changed_at


@pytest.mark.asyncio
async def test_get_financing_sources_pagination_and_locales(financing_sources_catalog_service, mock_financing_sources_catalog_repository):
    now = datetime.datetime(2025, 6, 1, tzinfo=datetime.timezone.utc)
    f1 = FinancingSourceFullResponseSchema.model_construct(
        id=1, name="A", financing_source_code="C1", lang="en",
        name_locales={"ru": "A_ru"}, created_at=now, changed_at=now
    )
    f2 = FinancingSourceFullResponseSchema.model_construct(
        id=2, name="B", financing_source_code="C2", lang="ru",
        name_locales={}, created_at=now, changed_at=now
    )
    mock_financing_sources_catalog_repository.get_financing_sources.return_value = [f1, f2]
    mock_financing_sources_catalog_repository.get_total_number_of_financing_sources.return_value = 5

    params = PaginationParams(page=1, limit=2)

    # Partial mode
    result = await financing_sources_catalog_service.get_financing_sources(
        pagination_params=params,
        name_filter=None,
        code_filter=None,
        include_all_locales=False,
    )
    assert isinstance(result, MultipleFinancingSourcesSchema)
    assert len(result.items) == 2
    assert all(isinstance(it, FinancingSourcePartialResponseSchema) for it in result.items)

    meta = result.pagination
    assert meta.current_page == 1
    assert meta.per_page == 2
    assert meta.total_items == 5
    assert meta.total_pages == math.ceil(5 / 2)
    assert meta.has_next is True
    assert meta.has_prev is False

    # Full mode
    result2 = await financing_sources_catalog_service.get_financing_sources(
        pagination_params=params,
        name_filter=None,
        code_filter=None,
        include_all_locales=True,
    )
    assert result2.items == [f1, f2]


@pytest.mark.asyncio
async def test_add_financing_source_conflicts_and_success(financing_sources_catalog_service, mock_financing_sources_catalog_repository):
    dto = AddFinancingSourceSchema.model_construct(
        name="X", financing_source_code="XX1", lang="en", name_locales={"ru": "Y"},
    )
    # conflict: name
    mock_financing_sources_catalog_repository.get_by_default_name.return_value = True
    with pytest.raises(InstanceAlreadyExistsError):
        await financing_sources_catalog_service.add_financing_source(dto)

    # conflict: code
    mock_financing_sources_catalog_repository.get_by_default_name.return_value = None
    mock_financing_sources_catalog_repository.get_by_financing_source_code.return_value = True
    with pytest.raises(InstanceAlreadyExistsError):
        await financing_sources_catalog_service.add_financing_source(dto)

    # conflict: locale
    mock_financing_sources_catalog_repository.get_by_financing_source_code.return_value = None
    mock_financing_sources_catalog_repository.get_by_name_locale.return_value = True
    with pytest.raises(InstanceAlreadyExistsError):
        await financing_sources_catalog_service.add_financing_source(dto)

    # success
    mock_financing_sources_catalog_repository.get_by_name_locale.return_value = None
    fake = FinancingSourceFullResponseSchema.model_construct(
        id=9, name="X", financing_source_code="XX1", lang="en",
        name_locales={"ru": "Y"},
        created_at=datetime.datetime.now(datetime.UTC), changed_at=datetime.datetime.now(datetime.UTC)
    )
    mock_financing_sources_catalog_repository.add_financing_source.return_value = fake

    out = await financing_sources_catalog_service.add_financing_source(dto)
    assert out is fake


@pytest.mark.asyncio
async def test_update_patient_context_attribute_all_branches(financing_sources_catalog_service, mock_financing_sources_catalog_repository):
    dto = UpdateFinancingSourceSchema.model_construct()

    # not found
    mock_financing_sources_catalog_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await financing_sources_catalog_service.update_financing_source(1, dto)

    # bad lang
    existing = FinancingSourceFullResponseSchema.model_construct(
        id=1, name="N", financing_source_code="C", lang="en",
        name_locales={}, created_at=datetime.datetime.now(datetime.UTC), changed_at=datetime.datetime.now(datetime.UTC)
    )
    mock_financing_sources_catalog_repository.get_by_id.return_value = existing
    bad = UpdateFinancingSourceSchema.model_construct(lang="kk")
    with pytest.raises(ValueError):
        await financing_sources_catalog_service.update_financing_source(1, bad)

    # name conflict
    ok_name = UpdateFinancingSourceSchema.model_construct(name="Other")
    mock_financing_sources_catalog_repository.get_by_default_name.return_value = True
    with pytest.raises(InstanceAlreadyExistsError):
        await financing_sources_catalog_service.update_financing_source(1, ok_name)

    # code conflict
    mock_financing_sources_catalog_repository.get_by_default_name.return_value = False
    ok_code = UpdateFinancingSourceSchema.model_construct(financing_source_code="ZZZ")
    mock_financing_sources_catalog_repository.get_by_financing_source_code.return_value = True
    with pytest.raises(InstanceAlreadyExistsError):
        await financing_sources_catalog_service.update_financing_source(1, ok_code)

    # locale conflict
    mock_financing_sources_catalog_repository.get_by_financing_source_code.return_value = False
    existing.name_locales = {"ru": "A"}
    ok_locale = UpdateFinancingSourceSchema.model_construct(name_locales={"ru": "B"})
    mock_financing_sources_catalog_repository.get_by_name_locale.return_value = True
    with pytest.raises(InstanceAlreadyExistsError):
        await financing_sources_catalog_service.update_financing_source(1, ok_locale)

    # success
    mock_financing_sources_catalog_repository.get_by_name_locale.return_value = False
    fake_upd = FinancingSourceFullResponseSchema.model_construct(
        id=1, name="Upd", financing_source_code="C", lang="en",
        name_locales={}, created_at=existing.created_at, changed_at=existing.changed_at
    )
    mock_financing_sources_catalog_repository.update_financing_source.return_value = fake_upd

    out = await financing_sources_catalog_service.update_financing_source(1, ok_name)
    assert out is fake_upd


@pytest.mark.asyncio
async def test_delete_by_id(financing_sources_catalog_service, mock_financing_sources_catalog_repository):
    # not found
    mock_financing_sources_catalog_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await financing_sources_catalog_service.delete_by_id(5)

    # found
    fake = FinancingSourceFullResponseSchema.model_construct(
        id=5, name="X", financing_source_code="C", lang="en",
        name_locales={}, created_at=datetime.datetime.now(datetime.UTC), changed_at=datetime.datetime.now(datetime.UTC)
    )
    mock_financing_sources_catalog_repository.get_by_id.return_value = fake

    await financing_sources_catalog_service.delete_by_id(5)
    mock_financing_sources_catalog_repository.delete_by_id.assert_awaited_once_with(5)
