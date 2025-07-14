import math
import datetime
import pytest

from src.apps.catalogs.infrastructure.api.schemas.requests.patient_context_attributes_catalog_request_schemas import (
    AddPatientContextAttributeSchema,
    UpdatePatientContextAttributeSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.patient_context_attributes_catalog_response_schemas import (
    PatientContextAttributeCatalogFullResponseSchema,
    PatientContextAttributeCatalogPartialResponseSchema,
    MultiplePatientContextAttributesSchema,
)
from src.shared.schemas.pagination_schemas import PaginationParams
from src.shared.exceptions import NoInstanceFoundError, InstanceAlreadyExistsError


@pytest.mark.asyncio
async def test_get_by_id_not_found(patient_context_attribute_service, patient_context_attributes_repository):
    patient_context_attributes_repository.get_by_id.return_value = None

    with pytest.raises(NoInstanceFoundError):
        await patient_context_attribute_service.get_by_id(123, include_all_locales=False)


@pytest.mark.asyncio
async def test_get_by_id_include_all_locales(patient_context_attribute_service, patient_context_attributes_repository):
    now = datetime.datetime.now(datetime.UTC)
    full = PatientContextAttributeCatalogFullResponseSchema.model_construct(
        id=7,
        name="Name",
        lang="en",
        name_locales={},
        created_at=now,
        changed_at=now,
    )
    patient_context_attributes_repository.get_by_id.return_value = full

    out = await patient_context_attribute_service.get_by_id(7, include_all_locales=True)
    assert out is full
    patient_context_attributes_repository.get_by_id.assert_awaited_once_with(7)


@pytest.mark.asyncio
async def test_get_by_id_partial(patient_context_attribute_service, patient_context_attributes_repository):
    now = datetime.datetime.now(datetime.UTC)
    full = PatientContextAttributeCatalogFullResponseSchema.model_construct(
        id=8,
        name="Orig",
        lang="ru",
        name_locales={"en": "Translated"},
        created_at=now,
        changed_at=now,
    )
    patient_context_attributes_repository.get_by_id.return_value = full

    out = await patient_context_attribute_service.get_by_id(8, include_all_locales=False)
    assert isinstance(out, PatientContextAttributeCatalogPartialResponseSchema)
    assert out.id == 8
    assert out.lang == "en"              
    assert out.name == "Translated"
    assert out.created_at == now
    assert out.changed_at == now


@pytest.mark.asyncio
async def test_get_patient_context_attributes_pagination(patient_context_attribute_service, patient_context_attributes_repository):
    now = datetime.datetime.now(datetime.UTC)
    full_items = [
        PatientContextAttributeCatalogFullResponseSchema.model_construct(
            id=1, name="A", lang="ru", name_locales={"en": "A_en"}, created_at=now, changed_at=now
        ),
        PatientContextAttributeCatalogFullResponseSchema.model_construct(
            id=2, name="B", lang="en", name_locales={}, created_at=now, changed_at=now
        ),
    ]
    patient_context_attributes_repository.get_patient_context_attributes.return_value = full_items
    patient_context_attributes_repository.get_total_number_of_patient_context_attributes.return_value = 5

    params = PaginationParams(page=1, limit=2)
    result = await patient_context_attribute_service.get_patient_context_attributes(
        pagination_params=params,
        name_filter="anything",
        include_all_locales=False,
    )

    assert isinstance(result, MultiplePatientContextAttributesSchema)
    assert len(result.items) == 2

    assert result.items[0].name == "A_en"

    assert result.pagination.current_page == 1
    assert result.pagination.per_page == 2
    assert result.pagination.total_items == 5
    assert result.pagination.total_pages == math.ceil(5 / 2)
    assert result.pagination.has_next is True
    assert result.pagination.has_prev is False
    
    result2 = await patient_context_attribute_service.get_patient_context_attributes(
        pagination_params=params,
        name_filter=None,
        include_all_locales=True,
    )
    assert result2.items == full_items


@pytest.mark.asyncio
async def test_add_patient_context_attribute_conflicts_and_success(
    patient_context_attribute_service, patient_context_attributes_repository
):
    dto1 = AddPatientContextAttributeSchema.model_construct(
        name="X",
        lang="en",
        name_locales={"ru": "Y"},
    )
    patient_context_attributes_repository.get_by_default_name.return_value = True

    with pytest.raises(InstanceAlreadyExistsError):
        await patient_context_attribute_service.add_patient_context_attribute(dto1)
    patient_context_attributes_repository.add_patient_context_attribute.assert_not_called()

    patient_context_attributes_repository.get_by_default_name.return_value = False

    async def exists_side(locale, val):
        return locale == "ru" and val == "Y"

    patient_context_attributes_repository.get_by_locale.side_effect = exists_side

    with pytest.raises(InstanceAlreadyExistsError):
        await patient_context_attribute_service.add_patient_context_attribute(dto1)
    patient_context_attributes_repository.add_patient_context_attribute.assert_not_called()

    patient_context_attributes_repository.get_by_locale.side_effect = lambda *_: False
    fake_full = PatientContextAttributeCatalogFullResponseSchema.model_construct(
        id=10, name="X", lang="en", name_locales={"ru": "Y"}, created_at=datetime.datetime.utcnow(), changed_at=datetime.datetime.utcnow()
    )
    patient_context_attributes_repository.add_patient_context_attribute.return_value = fake_full

    out = await patient_context_attribute_service.add_patient_context_attribute(dto1)
    assert out is fake_full
    patient_context_attributes_repository.add_patient_context_attribute.assert_awaited_once_with(dto1)


@pytest.mark.asyncio
async def test_update_patient_context_attribute_all_branches(
    patient_context_attribute_service, patient_context_attributes_repository
):
    patient_context_attributes_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await patient_context_attribute_service.update_patient_context_attribute(5, UpdatePatientContextAttributeSchema.model_construct())

    existing = PatientContextAttributeCatalogFullResponseSchema.model_construct(
        id=6, name="N", lang="en", name_locales={}, created_at=datetime.datetime.utcnow(), changed_at=datetime.datetime.utcnow()
    )
    patient_context_attributes_repository.get_by_id.return_value = existing

    with pytest.raises(ValueError):
        await patient_context_attribute_service.update_patient_context_attribute(
            6,
            UpdatePatientContextAttributeSchema.model_construct(lang="ru")
        )

    patient_context_attributes_repository.get_by_default_name.return_value = True
    with pytest.raises(InstanceAlreadyExistsError):
        await patient_context_attribute_service.update_patient_context_attribute(
            6,
            UpdatePatientContextAttributeSchema.model_construct(name="Other")
        )

    patient_context_attributes_repository.get_by_default_name.return_value = False
    async def locale_exists(lang_code, val):
        return lang_code == "ru" and val == "R2"
    patient_context_attributes_repository.get_by_locale.side_effect = locale_exists

    existing.name_locales = {"ru": "R"}
    with pytest.raises(InstanceAlreadyExistsError):
        await patient_context_attribute_service.update_patient_context_attribute(
            6,
            UpdatePatientContextAttributeSchema.model_construct(name_locales={"ru": "R2"})
        )

    patient_context_attributes_repository.get_by_locale.side_effect = lambda *a: False
    fake_updated = PatientContextAttributeCatalogFullResponseSchema.model_construct(
        id=6, name="Updated", lang="en", name_locales={}, created_at=existing.created_at, changed_at=existing.changed_at
    )
    patient_context_attributes_repository.update_patient_context_attribute.return_value = fake_updated

    out = await patient_context_attribute_service.update_patient_context_attribute(
        6,
        UpdatePatientContextAttributeSchema.model_construct(name="Updated")
    )
    assert out is fake_updated
    patient_context_attributes_repository.update_patient_context_attribute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id(patient_context_attribute_service, patient_context_attributes_repository):
    patient_context_attributes_repository.get_by_id.return_value = None
    with pytest.raises(NoInstanceFoundError):
        await patient_context_attribute_service.delete_by_id(42)

    existing = PatientContextAttributeCatalogFullResponseSchema.model_construct(
        id=9, name="X", lang="en", name_locales={}, created_at=datetime.datetime.utcnow(), changed_at=datetime.datetime.utcnow()
    )
    patient_context_attributes_repository.get_by_id.return_value = existing

    await patient_context_attribute_service.delete_by_id(9)
    patient_context_attributes_repository.delete_by_id.assert_awaited_once_with(9)
