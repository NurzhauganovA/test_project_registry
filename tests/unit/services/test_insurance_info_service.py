import uuid
from datetime import date

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.apps.catalogs.exceptions import InsuranceInfoInvalidDateError
from src.apps.catalogs.infrastructure.api.schemas.requests.insurance_info_catalog_request_schemas import \
    UpdateInsuranceInfoRecordSchema
from src.apps.catalogs.mappers import map_insurance_info_db_entity_to_response_schema
from src.core.i18n import _
from src.shared.exceptions import NoInstanceFoundError


@pytest.mark.asyncio
async def test_get_by_id_success(
    insurance_info_service,
    mock_insurance_info_catalog_repository,
    mock_insurance_info_db_entity,
):
    mock_insurance_info_catalog_repository.get_by_id.return_value = mock_insurance_info_db_entity

    result = await insurance_info_service.get_by_id(mock_insurance_info_db_entity.id)

    mock_insurance_info_catalog_repository.get_by_id.assert_called_once_with(
        mock_insurance_info_db_entity.id
    )
    assert result == mock_insurance_info_db_entity


@pytest.mark.asyncio
async def test_get_by_id_not_found(
    insurance_info_service,
    mock_insurance_info_catalog_repository,
):
    mock_insurance_info_catalog_repository.get_by_id.return_value = None

    with pytest.raises(NoInstanceFoundError) as exc_info:
        await insurance_info_service.get_by_id(999)

    assert str(999) in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_insurance_info_records_success(
    insurance_info_service,
    mock_insurance_info_catalog_repository,
    mock_insurance_info_db_entity,
):
    filters = MagicMock()
    pagination_params = MagicMock(page=1, limit=10)

    mock_insurance_info_catalog_repository.get_insurance_info_records.return_value = [
        map_insurance_info_db_entity_to_response_schema(mock_insurance_info_db_entity)
    ]
    mock_insurance_info_catalog_repository.get_total_number_of_insurance_info_records.return_value = 1

    response = await insurance_info_service.get_insurance_info_records(pagination_params, filters)

    mock_insurance_info_catalog_repository.get_insurance_info_records.assert_called_once_with(
        filters=filters, page=1, limit=10
    )
    mock_insurance_info_catalog_repository.get_total_number_of_insurance_info_records.assert_called_once()

    assert response.pagination.current_page == 1
    assert response.pagination.total_items == 1
    assert response.pagination.total_pages == 1
    assert response.pagination.has_next is False
    assert response.pagination.has_prev is False
    assert len(response.items) == 1
    expected_model = map_insurance_info_db_entity_to_response_schema(mock_insurance_info_db_entity)
    assert response.items[0] == expected_model


@pytest.mark.asyncio
async def test_add_insurance_info_record_success(
    insurance_info_service,
    mock_insurance_info_catalog_repository,
    mock_patients_service,
    mock_financing_sources_catalog_service,
    mock_add_insurance_info_catalog_schema,
):
    mock_patients_service.get_by_id = AsyncMock()
    mock_financing_sources_catalog_service.get_by_id = AsyncMock()
    mock_insurance_info_catalog_repository.add_insurance_info_record = AsyncMock(
        return_value="added_record"
    )

    result = await insurance_info_service.add_insurance_info_record(mock_add_insurance_info_catalog_schema)

    mock_patients_service.get_by_id.assert_called_once_with(
        mock_add_insurance_info_catalog_schema.patient_id
    )
    mock_financing_sources_catalog_service.get_by_id.assert_called_once_with(
        mock_add_insurance_info_catalog_schema.financing_source_id
    )
    mock_insurance_info_catalog_repository.add_insurance_info_record.assert_called_once_with(
        mock_add_insurance_info_catalog_schema
    )

    assert result == "added_record"


@pytest.mark.asyncio
async def test_update_insurance_info_record_success(
    insurance_info_service,
    mock_insurance_info_catalog_repository,
    mock_patients_service,
    mock_financing_sources_catalog_service,
    mock_insurance_info_db_entity,
    mock_update_insurance_info_catalog_schema
):
    mock_insurance_info_catalog_repository.get_by_id.return_value = mock_insurance_info_db_entity
    mock_patients_service.get_by_id = AsyncMock()
    mock_financing_sources_catalog_service.get_by_id = AsyncMock()
    mock_insurance_info_catalog_repository.update_insurance_info_record = AsyncMock(return_value="updated_record")

    mock_update_insurance_info_catalog_schema = UpdateInsuranceInfoRecordSchema(
        **mock_update_insurance_info_catalog_schema.model_dump()
    )

    result = await insurance_info_service.update_insurance_info_record(
        mock_insurance_info_db_entity.id,
        mock_update_insurance_info_catalog_schema,
    )

    mock_insurance_info_catalog_repository.get_by_id.assert_called_once_with(mock_insurance_info_db_entity.id)
    mock_patients_service.get_by_id.assert_called_once_with(mock_update_insurance_info_catalog_schema.patient_id)
    mock_financing_sources_catalog_service.get_by_id.assert_called_once_with(
        mock_update_insurance_info_catalog_schema.financing_source_id
    )
    mock_insurance_info_catalog_repository.update_insurance_info_record.assert_called_once_with(
        mock_insurance_info_db_entity.id,
        mock_update_insurance_info_catalog_schema,
    )
    assert result == "updated_record"


@pytest.mark.asyncio
async def test_update_insurance_info_record_not_found(
    insurance_info_service,
    mock_insurance_info_catalog_repository,
    mock_update_insurance_info_catalog_schema,
):
    mock_insurance_info_catalog_repository.get_by_id.return_value = None

    with pytest.raises(NoInstanceFoundError):
        await insurance_info_service.update_insurance_info_record(
            999,
            mock_update_insurance_info_catalog_schema,
        )


@pytest.mark.asyncio
async def test_update_insurance_info_record_date_validation_error(
    insurance_info_service,
    mock_insurance_info_catalog_repository,
    mock_update_insurance_info_catalog_schema,
    mock_insurance_info_db_entity,
):
    mock_insurance_info_db_entity.valid_from = date(2025, 1, 1)
    mock_insurance_info_db_entity.valid_till = date(2025, 12, 31)

    mock_insurance_info_catalog_repository.get_by_id.return_value = mock_insurance_info_db_entity

    # DTO with dates where valid_till < valid_from — should throw an error
    invalid_update_dto = mock_update_insurance_info_catalog_schema.model_copy(update={
        "valid_from": date(2025, 6, 1),
        "valid_till": date(2025, 5, 1),
    })

    with pytest.raises(InsuranceInfoInvalidDateError) as exc_info:
        await insurance_info_service.update_insurance_info_record(
            mock_insurance_info_db_entity.id,
            invalid_update_dto,
        )

    assert _("'valid_till' date must be equal or greater than 'valid_from' date.") in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_by_id_success(
    insurance_info_service,
    mock_insurance_info_catalog_repository,
    mock_insurance_info_db_entity,
):
    mock_insurance_info_catalog_repository.get_by_id.return_value = mock_insurance_info_db_entity
    mock_insurance_info_catalog_repository.delete_by_id = AsyncMock()

    await insurance_info_service.delete_by_id(mock_insurance_info_db_entity.id)

    mock_insurance_info_catalog_repository.get_by_id.assert_called_once_with(mock_insurance_info_db_entity.id)
    mock_insurance_info_catalog_repository.delete_by_id.assert_called_once_with(mock_insurance_info_db_entity.id)


@pytest.mark.asyncio
async def test_delete_by_id_not_found(
    insurance_info_service,
    mock_insurance_info_catalog_repository,
):
    mock_insurance_info_catalog_repository.get_by_id.return_value = None

    with pytest.raises(NoInstanceFoundError):
        await insurance_info_service.delete_by_id(999)

