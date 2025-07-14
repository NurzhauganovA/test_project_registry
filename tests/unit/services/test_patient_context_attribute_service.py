from datetime import datetime, UTC
import math

import pytest

from src.apps.catalogs.infrastructure.api.schemas.requests.patient_context_attributes_catalog_request_schemas import (
    AddPatientContextAttributeSchema,
    UpdatePatientContextAttributeSchema
)
from src.apps.catalogs.infrastructure.api.schemas.responses.patient_context_attributes_catalog_response_schemas import (
    PatientContextAttributeCatalogFullResponseSchema,
    PatientContextAttributeCatalogPartialResponseSchema, 
    MultiplePatientContextAttributesSchema
)
from src.apps.catalogs.services.patient_context_attribute_service import PatientContextAttributeService
from src.shared.exceptions import NoInstanceFoundError, InstanceAlreadyExistsError
from src.shared.schemas.pagination_schemas import PaginationParams


@pytest.mark.asyncio
async def test___get_localized_name_various_cases():
    Full = PatientContextAttributeCatalogFullResponseSchema
    obj = Full(id=1, name="Orig", lang="en", name_locales={"ru": "Рус"}, created_at=datetime.now(UTC) ,
               changed_at=datetime.now(UTC))
    got = PatientContextAttributeService._PatientContextAttributeService__get_localized_name(obj)
    assert got == "Orig"

    obj = Full(id=2, name="Orig", lang="ru", name_locales={"en": "Translated"}, created_at=datetime.now(UTC),
               changed_at=datetime.now(UTC))
    assert PatientContextAttributeService._PatientContextAttributeService__get_localized_name(obj) == "Translated"

    obj = Full(id=3, name="Orig", lang="en", name_locales={}, created_at=datetime.now(UTC),
               changed_at=datetime.now(UTC))
    assert PatientContextAttributeService._PatientContextAttributeService__get_localized_name(obj) == "Orig"

    obj = Full(id=4, name="Orig", lang="fr", name_locales={}, created_at=datetime.now(UTC) ,
               changed_at=datetime.now(UTC))
    assert PatientContextAttributeService._PatientContextAttributeService__get_localized_name(obj) == "Orig"


@pytest.mark.asyncio
async def test_get_by_id_not_found_raises(patient_context_attribute_service, patient_context_attributes_repository):
    patient_context_attributes_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await patient_context_attribute_service.get_by_id(123, include_all_locales=False)


@pytest.mark.asyncio
async def test_get_by_id_include_all_locales_returns_full(patient_context_attribute_service, patient_context_attributes_repository):
    full = PatientContextAttributeCatalogFullResponseSchema(
        id=7, name="N", lang="en", name_locales={}, created_at=datetime.now(UTC) , changed_at=datetime.now(UTC) 
    )
    patient_context_attributes_repository.get_by_id.return_value = full

    result = await patient_context_attribute_service.get_by_id(7, include_all_locales=True)

    assert result is full


@pytest.mark.asyncio
async def test_get_by_id_localized_partial(patient_context_attribute_service, patient_context_attributes_repository):
    full = PatientContextAttributeCatalogFullResponseSchema(
        id=8,
        name="Orig",
        lang="ru",
        name_locales={"en": "EnName"},
        created_at=datetime(2025, 1, 1, 0, 0, 0),
        changed_at=datetime(2025, 1, 2, 0, 0, 0),
    )
    patient_context_attributes_repository.get_by_id.return_value = full

    partial = await patient_context_attribute_service.get_by_id(8, include_all_locales=False)
    assert isinstance(partial, PatientContextAttributeCatalogPartialResponseSchema)
    assert partial.id == 8
    assert partial.lang == "en"
    assert partial.name == "EnName"
    assert partial.created_at == full.created_at
    assert partial.changed_at == full.changed_at


@pytest.mark.asyncio
async def test_get_patient_context_attributes_pagination_and_locales(patient_context_attribute_service, patient_context_attributes_repository):
    now = datetime.now(UTC) 

    full_items = [
        PatientContextAttributeCatalogFullResponseSchema(id=1, name="A", lang="ru", name_locales={"en": "A_en"},
                                                         created_at=now, changed_at=now),
        PatientContextAttributeCatalogFullResponseSchema(id=2, name="B", lang="en", name_locales={}, created_at=now,
                                                         changed_at=now),
    ]
    patient_context_attributes_repository.get_patient_context_attributes.return_value = full_items
    patient_context_attributes_repository.get_total_number_of_patient_context_attributes.return_value = 5

    params = PaginationParams(page=1, limit=2)

    result = await patient_context_attribute_service.get_patient_context_attributes(params, name_filter="x", include_all_locales=False)
    assert isinstance(result, MultiplePatientContextAttributesSchema)
    assert len(result.items) == 2

    assert result.items[0].name == "A_en"

    assert result.pagination.current_page == 1
    assert result.pagination.per_page == 2
    assert result.pagination.total_items == 5
    assert result.pagination.total_pages == math.ceil(5 / 2)
    assert result.pagination.has_next is True
    assert result.pagination.has_prev is False

    result2 = await patient_context_attribute_service.get_patient_context_attributes(params, name_filter=None, include_all_locales=True)
    assert result2.items == full_items


@pytest.mark.asyncio
async def test_add_patient_context_attribute_name_conflict(patient_context_attribute_service, patient_context_attributes_repository):
    dto = AddPatientContextAttributeSchema.model_construct(name="X", name_locales={"en": "Y"})
    patient_context_attributes_repository.get_by_default_name.return_value = True

    with pytest.raises(InstanceAlreadyExistsError):
        await patient_context_attribute_service.add_patient_context_attribute(dto)
    patient_context_attributes_repository.add_patient_context_attribute.assert_not_called()


@pytest.mark.asyncio
async def test_add_patient_context_attribute_locale_conflict(patient_context_attribute_service, patient_context_attributes_repository):
    dto = AddPatientContextAttributeSchema.model_construct(name="X", name_locales={"en": "Y", "ru": "R"})
    patient_context_attributes_repository.get_by_default_name.return_value = False

    async def exists(code, val):
        return code == "en" and val == "Y"

    patient_context_attributes_repository.get_by_locale.side_effect = exists

    with pytest.raises(InstanceAlreadyExistsError):
        await patient_context_attribute_service.add_patient_context_attribute(dto)
    patient_context_attributes_repository.add_patient_context_attribute.assert_not_called()


@pytest.mark.asyncio
async def test_add_patient_context_attribute_success(patient_context_attribute_service, patient_context_attributes_repository):
    dto = AddPatientContextAttributeSchema.model_construct(name="X", name_locales={"en": "Y"})
    patient_context_attributes_repository.get_by_default_name.return_value = False
    patient_context_attributes_repository.get_by_locale.return_value = False
    fake_full = PatientContextAttributeCatalogFullResponseSchema(
        id=10, name="X", lang="en", name_locales={"en": "Y"}, created_at=datetime.now(UTC) , changed_at=datetime.now(UTC) 
    )
    patient_context_attributes_repository.add_patient_context_attribute.return_value = fake_full

    out = await patient_context_attribute_service.add_patient_context_attribute(dto)
    assert out is fake_full
    patient_context_attributes_repository.add_patient_context_attribute.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_update_patient_context_attribute_not_found(patient_context_attribute_service, patient_context_attributes_repository):
    patient_context_attributes_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await patient_context_attribute_service.update_patient_context_attribute(5, UpdatePatientContextAttributeSchema.model_construct())


@pytest.mark.asyncio
async def test_update_patient_context_attribute_bad_lang(patient_context_attribute_service, patient_context_attributes_repository):
    existing = PatientContextAttributeCatalogFullResponseSchema(
        id=6, name="N", lang="en", name_locales={}, created_at=datetime.now(UTC) , changed_at=datetime.now(UTC) 
    )
    patient_context_attributes_repository.get_by_id.return_value = existing

    with pytest.raises(ValueError):
        await patient_context_attribute_service.update_patient_context_attribute(6, UpdatePatientContextAttributeSchema.model_construct(lang="ru"))


@pytest.mark.asyncio
async def test_update_patient_context_attribute_name_conflict(patient_context_attribute_service, patient_context_attributes_repository):
    existing = PatientContextAttributeCatalogFullResponseSchema(
        id=6, name="Old", lang="en", name_locales={}, created_at=datetime.now(UTC) , changed_at=datetime.now(UTC) 
    )
    patient_context_attributes_repository.get_by_id.return_value = existing
    patient_context_attributes_repository.get_by_default_name.return_value = True

    with pytest.raises(InstanceAlreadyExistsError):
        await patient_context_attribute_service.update_patient_context_attribute(6, UpdatePatientContextAttributeSchema.model_construct(name="New"))


@pytest.mark.asyncio
async def test_update_patient_context_attribute_locale_conflict(patient_context_attribute_service, patient_context_attributes_repository):
    existing = PatientContextAttributeCatalogFullResponseSchema(
        id=6, name="Name", lang="en", name_locales={"ru": "R"},
        created_at=datetime.now(UTC) , changed_at=datetime.now(UTC) 
    )
    patient_context_attributes_repository.get_by_id.return_value = existing
    patient_context_attributes_repository.get_by_default_name.return_value = False

    dto = UpdatePatientContextAttributeSchema.model_construct(name_locales={"ru": "R2", "en": "X"})

    async def exists(code, val):
        return code == "en" and val == "X"

    patient_context_attributes_repository.get_by_locale.side_effect = exists

    with pytest.raises(InstanceAlreadyExistsError):
        await patient_context_attribute_service.update_patient_context_attribute(6, dto)


@pytest.mark.asyncio
async def test_update_patient_context_attribute_success(patient_context_attribute_service, patient_context_attributes_repository):
    existing = PatientContextAttributeCatalogFullResponseSchema(
        id=6, name="Old", lang="en", name_locales={},
        created_at=datetime.now(UTC) , changed_at=datetime.now(UTC) 
    )
    patient_context_attributes_repository.get_by_id.return_value = existing
    patient_context_attributes_repository.get_by_default_name.return_value = False
    patient_context_attributes_repository.get_by_locale.return_value = False
    fake_updated = PatientContextAttributeCatalogFullResponseSchema(
        id=6, name="New", lang="en", name_locales={}, created_at=existing.created_at, changed_at=existing.changed_at
    )
    patient_context_attributes_repository.update_patient_context_attribute.return_value = fake_updated

    out = await patient_context_attribute_service.update_patient_context_attribute(6, UpdatePatientContextAttributeSchema.model_construct(name="New"))
    assert out is fake_updated
    patient_context_attributes_repository.update_patient_context_attribute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id_not_found(patient_context_attribute_service, patient_context_attributes_repository):
    patient_context_attributes_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await patient_context_attribute_service.delete_by_id(42)


@pytest.mark.asyncio
async def test_delete_by_id_success(patient_context_attribute_service, patient_context_attributes_repository):
    existing = PatientContextAttributeCatalogFullResponseSchema(
        id=9, name="X", lang="en", name_locales={}, created_at=datetime.now(UTC) , changed_at=datetime.now(UTC) 
    )
    patient_context_attributes_repository.get_by_id.return_value = existing

    await patient_context_attribute_service.delete_by_id(9)
    patient_context_attributes_repository.delete_by_id.assert_awaited_once_with(9)
