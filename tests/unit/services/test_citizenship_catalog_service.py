import pytest
from src.shared.exceptions import NoInstanceFoundError, InstanceAlreadyExistsError
from src.shared.schemas.pagination_schemas import PaginationParams
from src.apps.catalogs.infrastructure.api.schemas.requests.citizenship_catalog_request_schemas import (
    AddCitizenshipSchema, UpdateCitizenshipSchema
)
from src.core.settings import project_settings


@pytest.mark.asyncio
async def test___get_localized_name_returns_name_or_locale(citizenship_service, dummy_citizenship_full):
    svc = citizenship_service
    result = svc._CitizenshipCatalogService__get_localized_name(dummy_citizenship_full)
    assert result == dummy_citizenship_full.name

    dummy_citizenship_full.lang = "en"
    dummy_citizenship_full.name_locales = {"ru": "Русский"}
    from src.apps.catalogs.services import citizenship_catalog_service
    original_get_locale = citizenship_catalog_service.get_locale
    citizenship_catalog_service.get_locale = lambda: "ru"
    try:
        result = svc._CitizenshipCatalogService__get_localized_name(dummy_citizenship_full)
        assert result == "Русский"
    finally:
        citizenship_catalog_service.get_locale = original_get_locale


@pytest.mark.asyncio
async def test_get_by_id_returns_partial_or_full(citizenship_service, mock_citizenship_repository,
                                                 dummy_citizenship_full):
    result = await citizenship_service.get_by_id(1, include_all_locales=True)
    assert result == dummy_citizenship_full

    result = await citizenship_service.get_by_id(1, include_all_locales=False)
    assert result.id == dummy_citizenship_full.id
    assert hasattr(result, "name")
    assert hasattr(result, "lang")


@pytest.mark.asyncio
async def test_get_by_id_raises_if_not_found(citizenship_service, mock_citizenship_repository):
    mock_citizenship_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await citizenship_service.get_by_id(999)


@pytest.mark.asyncio
async def test_get_citizenship_records_pagination_and_locales(citizenship_service, mock_citizenship_repository,
                                                              dummy_citizenship_full):
    params = PaginationParams(page=1, limit=1)
    result = await citizenship_service.get_citizenship_records(params, include_all_locales=False)
    assert result.pagination.total_items == 1
    assert len(result.items) == 1
    assert hasattr(result.items[0], "name")


@pytest.mark.asyncio
async def test_add_citizenship_name_conflict_raises(citizenship_service, mock_citizenship_repository):
    mock_citizenship_repository.get_by_default_name.return_value = True
    dto = AddCitizenshipSchema.model_construct(name="NameConflict", country_code="CC", lang=project_settings.DEFAULT_LANGUAGE)
    with pytest.raises(InstanceAlreadyExistsError):
        await citizenship_service.add_citizenship(dto)
    mock_citizenship_repository.add_citizenship.assert_not_called()


@pytest.mark.asyncio
async def test_add_citizenship_country_code_conflict_raises(citizenship_service, mock_citizenship_repository):
    mock_citizenship_repository.get_by_default_name.return_value = False
    mock_citizenship_repository.get_by_country_code.return_value = True
    dto = AddCitizenshipSchema.model_construct(name="NewName", country_code="CC", lang=project_settings.DEFAULT_LANGUAGE)
    with pytest.raises(InstanceAlreadyExistsError):
        await citizenship_service.add_citizenship(dto)
    mock_citizenship_repository.add_citizenship.assert_not_called()


@pytest.mark.asyncio
async def test_add_citizenship_locale_conflict_raises(citizenship_service, mock_citizenship_repository):
    mock_citizenship_repository.get_by_default_name.return_value = False
    mock_citizenship_repository.get_by_country_code.return_value = None
    mock_citizenship_repository.get_by_locale.side_effect = lambda code, val: val == "conflict"
    dto = AddCitizenshipSchema.model_construct(name="NewName", country_code="CC", lang=project_settings.DEFAULT_LANGUAGE,
                               name_locales={"en": "conflict"})
    with pytest.raises(InstanceAlreadyExistsError):
        await citizenship_service.add_citizenship(dto)
    mock_citizenship_repository.add_citizenship.assert_not_called()


@pytest.mark.asyncio
async def test_add_citizenship_success(citizenship_service, mock_citizenship_repository, dummy_citizenship_full):
    mock_citizenship_repository.get_by_default_name.return_value = False
    mock_citizenship_repository.get_by_country_code.return_value = None
    mock_citizenship_repository.get_by_locale.return_value = False

    dto = AddCitizenshipSchema.model_construct(name="NewName", country_code="CC", lang=project_settings.DEFAULT_LANGUAGE)
    mock_citizenship_repository.add_citizenship.return_value = dummy_citizenship_full

    result = await citizenship_service.add_citizenship(dto)
    assert result == dummy_citizenship_full
    mock_citizenship_repository.add_citizenship.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_update_citizenship_not_found_raises(citizenship_service, mock_citizenship_repository,
                                                   dummy_citizenship_full):
    mock_citizenship_repository.get_by_id.return_value = None
    dto = UpdateCitizenshipSchema.model_construct(
        country_code="ConflictCode",
        name=None,
        lang=None,
        name_locales=None
    )
    with pytest.raises(NoInstanceFoundError):
        await citizenship_service.update_citizenship(999, dto)


@pytest.mark.asyncio
async def test_update_citizenship_bad_lang_raises(citizenship_service, mock_citizenship_repository,
                                                  dummy_citizenship_full):
    mock_citizenship_repository.get_by_id.return_value = dummy_citizenship_full
    dto = UpdateCitizenshipSchema.model_construct(
        country_code=None,
        name=None,
        lang="ru",
        name_locales=None
    )
    if project_settings.DEFAULT_LANGUAGE != "ru":
        with pytest.raises(ValueError):
            await citizenship_service.update_citizenship(dummy_citizenship_full.id, dto)


@pytest.mark.asyncio
async def test_update_citizenship_name_conflict_raises(citizenship_service, mock_citizenship_repository,
                                                       dummy_citizenship_full):
    mock_citizenship_repository.get_by_id.return_value = dummy_citizenship_full
    mock_citizenship_repository.get_by_default_name.return_value = True
    dto = UpdateCitizenshipSchema.model_construct(
        country_code=None,
        name="ConflictName",
        lang=None,
        name_locales=None
    )
    with pytest.raises(InstanceAlreadyExistsError):
        await citizenship_service.update_citizenship(dummy_citizenship_full.id, dto)


@pytest.mark.asyncio
async def test_update_citizenship_country_code_conflict_raises(citizenship_service, mock_citizenship_repository,
                                                               dummy_citizenship_full):
    mock_citizenship_repository.get_by_id.return_value = dummy_citizenship_full
    mock_citizenship_repository.get_by_default_name.return_value = False
    mock_citizenship_repository.get_by_country_code.return_value = True
    dto = UpdateCitizenshipSchema.model_construct(
        country_code="ConflictCode",
        name=None,
        lang=None,
        name_locales=None
    )

    with pytest.raises(InstanceAlreadyExistsError):
        await citizenship_service.update_citizenship(dummy_citizenship_full.id, dto)


@pytest.mark.asyncio
async def test_update_citizenship_locale_conflict_raises(citizenship_service, mock_citizenship_repository,
                                                         dummy_citizenship_full):
    mock_citizenship_repository.get_by_id.return_value = dummy_citizenship_full
    mock_citizenship_repository.get_by_default_name.return_value = False
    mock_citizenship_repository.get_by_locale.side_effect = lambda code, val: val == "conflict"
    dto = UpdateCitizenshipSchema.model_construct(
        country_code=None,
        name=None,
        lang=None,
        name_locales={"en": "conflict"}
    )
    with pytest.raises(InstanceAlreadyExistsError):
        await citizenship_service.update_citizenship(dummy_citizenship_full.id, dto)


@pytest.mark.asyncio
async def test_update_citizenship_success(citizenship_service, mock_citizenship_repository, dummy_citizenship_full):
    mock_citizenship_repository.get_by_id.return_value = dummy_citizenship_full
    mock_citizenship_repository.get_by_default_name.return_value = False
    mock_citizenship_repository.get_by_country_code.return_value = None
    mock_citizenship_repository.get_by_locale.return_value = False
    mock_citizenship_repository.update_citizenship.return_value = dummy_citizenship_full

    dto = UpdateCitizenshipSchema.model_construct(
        country_code=None,
        name="NewName",
        lang=None,
        name_locales=None
    )

    result = await citizenship_service.update_citizenship(dummy_citizenship_full.id, dto)
    assert result == dummy_citizenship_full
    mock_citizenship_repository.update_citizenship.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id_not_found_raises(citizenship_service, mock_citizenship_repository):
    mock_citizenship_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await citizenship_service.delete_by_id(999)


@pytest.mark.asyncio
async def test_delete_by_id_success(citizenship_service, mock_citizenship_repository, dummy_citizenship_full):
    mock_citizenship_repository.get_by_id.return_value = dummy_citizenship_full
    await citizenship_service.delete_by_id(dummy_citizenship_full.id)
    mock_citizenship_repository.delete_by_id.assert_awaited_once_with(dummy_citizenship_full.id)
