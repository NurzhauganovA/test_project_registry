import math

import pytest

from src.apps.catalogs.infrastructure.api.schemas.requests.medical_organizations_catalog_schemas import (
    UpdateMedicalOrganizationSchema
)
from src.apps.catalogs.infrastructure.api.schemas.responses.medical_organizations_catalog_schemas import (
    MedicalOrganizationCatalogFullResponseSchema,
    MedicalOrganizationCatalogPartialResponseSchema,
    MultipleMedicalOrganizationsSchema
)
from src.shared.exceptions import InstanceAlreadyExistsError, NoInstanceFoundError
from src.shared.schemas.pagination_schemas import PaginationParams
from src.apps.catalogs.infrastructure.api.schemas.requests.filters.medical_organizations_catalog_filters import (
    MedicalOrganizationsCatalogFilterParams,
)


@pytest.mark.asyncio
async def test_get_by_id_not_found_raises(medical_organizations_service, medical_organizations_repository):
    medical_organizations_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await medical_organizations_service.get_by_id(42)


@pytest.mark.asyncio
async def test_get_by_id_full_returned(medical_organizations_service, medical_organizations_repository, full_medorg):
    medical_organizations_repository.get_by_id.return_value = full_medorg
    out = await medical_organizations_service.get_by_id(1, include_all_locales=True)
    assert out is full_medorg


@pytest.mark.asyncio
async def test_get_by_id_partial_same_lang(medical_organizations_service, medical_organizations_repository, full_medorg):
    medical_organizations_repository.get_by_id.return_value = full_medorg
    partial = await medical_organizations_service.get_by_id(1, include_all_locales=False)
    assert isinstance(partial, MedicalOrganizationCatalogPartialResponseSchema)
    assert partial.name == full_medorg.name
    assert partial.address == full_medorg.address


@pytest.mark.asyncio
async def test_get_by_id_partial_translated(monkeypatch, medical_organizations_service, medical_organizations_repository, full_medorg):
    monkeypatch.setattr(
        "src.apps.catalogs.services.medical_organizations_catalog_service.get_locale",
        lambda: "ru",
    )
    medical_organizations_repository.get_by_id.return_value = full_medorg

    partial = await medical_organizations_service.get_by_id(1, include_all_locales=False)
    assert partial.name == full_medorg.name_locales["ru"]
    assert partial.address == full_medorg.address_locales["ru"]


@pytest.mark.asyncio
async def test_get_medical_organizations_pagination_partial(medical_organizations_service, medical_organizations_repository, full_medorg):
    medical_organizations_repository.get_medical_organizations.return_value = [full_medorg, full_medorg]
    medical_organizations_repository.get_total_number_of_medical_organizations.return_value = 5

    params = PaginationParams(page=2, limit=2)
    filters = MedicalOrganizationsCatalogFilterParams(name_filter="X")

    result: MultipleMedicalOrganizationsSchema = await medical_organizations_service.get_medical_organizations(
        pagination_params=params,
        filter_params=filters,
        include_all_locales=False,
    )
    assert len(result.items) == 2

    assert result.pagination.current_page == 2
    assert result.pagination.total_pages == math.ceil(5 / 2)

    assert all(isinstance(item, MedicalOrganizationCatalogPartialResponseSchema) for item in result.items)


@pytest.mark.asyncio
async def test_get_medical_organizations_full(medical_organizations_service, medical_organizations_repository, full_medorg):
    medical_organizations_repository.get_medical_organizations.return_value = [full_medorg]
    medical_organizations_repository.get_total_number_of_medical_organizations.return_value = 1

    params = PaginationParams(page=1, limit=10)
    filters = MedicalOrganizationsCatalogFilterParams()

    result = await medical_organizations_service.get_medical_organizations(
        pagination_params=params,
        filter_params=filters,
        include_all_locales=True,
    )
    assert isinstance(result.items[0], MedicalOrganizationCatalogFullResponseSchema)
    assert result.pagination.total_items == 1


@pytest.mark.asyncio
async def test_add_name_conflict(medical_organizations_service, medical_organizations_repository, add_medorg_schema, full_medorg):
    medical_organizations_repository.get_by_default_name.return_value = full_medorg
    with pytest.raises(InstanceAlreadyExistsError):
        await medical_organizations_service.add_medical_organization(add_medorg_schema)


@pytest.mark.asyncio
async def test_add_code_conflict(medical_organizations_service, medical_organizations_repository, add_medorg_schema, full_medorg):
    medical_organizations_repository.get_by_default_name.return_value = None
    medical_organizations_repository.get_by_organization_code.return_value = full_medorg
    with pytest.raises(InstanceAlreadyExistsError):
        await medical_organizations_service.add_medical_organization(add_medorg_schema)


@pytest.mark.asyncio
async def test_add_locale_conflict(medical_organizations_service, medical_organizations_repository, add_medorg_schema, full_medorg):
    medical_organizations_repository.get_by_default_name.return_value = None
    medical_organizations_repository.get_by_organization_code.return_value = None
    medical_organizations_repository.get_by_name_locale.return_value = full_medorg
    with pytest.raises(InstanceAlreadyExistsError):
        await medical_organizations_service.add_medical_organization(add_medorg_schema)


@pytest.mark.asyncio
async def test_add_success(medical_organizations_service, medical_organizations_repository, add_medorg_schema, full_medorg):
    medical_organizations_repository.get_by_default_name.return_value = None
    medical_organizations_repository.get_by_organization_code.return_value = None
    medical_organizations_repository.get_by_name_locale.return_value = None
    medical_organizations_repository.add_medical_organization.return_value = full_medorg

    out = await medical_organizations_service.add_medical_organization(add_medorg_schema)
    assert out is full_medorg
    medical_organizations_repository.add_medical_organization.assert_awaited_once_with(add_medorg_schema)


@pytest.mark.asyncio
async def test_update_not_found(medical_organizations_service, medical_organizations_repository, update_medorg_schema):
    medical_organizations_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await medical_organizations_service.update_medical_organization(99, update_medorg_schema)


@pytest.mark.asyncio
async def test_update_bad_lang(medical_organizations_service, medical_organizations_repository, full_medorg):
    medical_organizations_repository.get_by_id.return_value = full_medorg
    bad = UpdateMedicalOrganizationSchema.model_construct(lang="kk")
    with pytest.raises(ValueError):
        await medical_organizations_service.update_medical_organization(1, bad)


@pytest.mark.asyncio
async def test_update_name_conflict(medical_organizations_service, medical_organizations_repository, full_medorg):
    medical_organizations_repository.get_by_id.return_value = full_medorg
    other = full_medorg.model_copy(update={"id": 2})
    medical_organizations_repository.get_by_default_name.return_value = other
    schema = UpdateMedicalOrganizationSchema.model_construct(name="NameEn")
    with pytest.raises(InstanceAlreadyExistsError):
        await medical_organizations_service.update_medical_organization(1, schema)


@pytest.mark.asyncio
async def test_update_code_conflict(medical_organizations_service, medical_organizations_repository, full_medorg):
    medical_organizations_repository.get_by_id.return_value = full_medorg
    medical_organizations_repository.get_by_default_name.return_value = None
    other = full_medorg.model_copy(update={"id": 2})
    medical_organizations_repository.get_by_organization_code.return_value = other
    schema = UpdateMedicalOrganizationSchema.model_construct(organization_code="CODE1")
    with pytest.raises(InstanceAlreadyExistsError):
        await medical_organizations_service.update_medical_organization(1, schema)


@pytest.mark.asyncio
async def test_update_locale_conflict(medical_organizations_service, medical_organizations_repository, full_medorg):
    medical_organizations_repository.get_by_id.return_value = full_medorg
    medical_organizations_repository.get_by_default_name.return_value = None
    medical_organizations_repository.get_by_organization_code.return_value = None
    medical_organizations_repository.get_by_name_locale.return_value = full_medorg
    schema = UpdateMedicalOrganizationSchema.model_construct(name_locales={"ru": "NameRu"})
    with pytest.raises(InstanceAlreadyExistsError):
        await medical_organizations_service.update_medical_organization(1, schema)


@pytest.mark.asyncio
async def test_update_success(medical_organizations_service, medical_organizations_repository, full_medorg, update_medorg_schema):
    medical_organizations_repository.get_by_id.return_value = full_medorg
    medical_organizations_repository.get_by_default_name.return_value = None
    medical_organizations_repository.get_by_organization_code.return_value = None
    medical_organizations_repository.get_by_name_locale.return_value = None

    updated = full_medorg.model_copy(update={"name": "NewName"})
    medical_organizations_repository.update_medical_organization.return_value = updated

    out = await medical_organizations_service.update_medical_organization(1, update_medorg_schema)
    assert out is updated
    medical_organizations_repository.update_medical_organization.assert_awaited_once_with(1, update_medorg_schema)


@pytest.mark.asyncio
async def test_delete_not_found(medical_organizations_service, medical_organizations_repository):
    medical_organizations_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await medical_organizations_service.delete_by_id(5)


@pytest.mark.asyncio
async def test_delete_success(medical_organizations_service, medical_organizations_repository, full_medorg):
    medical_organizations_repository.get_by_id.return_value = full_medorg
    await medical_organizations_service.delete_by_id(1)
    medical_organizations_repository.delete_by_id.assert_awaited_once_with(1)
