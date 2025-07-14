import datetime
from unittest.mock import MagicMock, AsyncMock

import pytest

from src.apps.catalogs.infrastructure.api.schemas.requests.filters.insurance_info_catalog_filters import (
    InsuranceInfoCatalogFilterParams
)
from src.apps.catalogs.mappers import (
    map_insurance_info_db_entity_to_response_schema,
    map_insurance_info_create_schema_to_db_entity,
    map_insurance_info_update_schema_to_db_entity
)


@pytest.mark.asyncio
async def test_get_total_number_of_insurance_info_records(
        insurance_info_catalog_repository_impl,
        mock_async_db_session
):
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = 42
    mock_async_db_session.execute.return_value = mock_result

    total = await insurance_info_catalog_repository_impl.get_total_number_of_insurance_info_records()

    mock_async_db_session.execute.assert_called_once()
    mock_result.scalar_one.assert_called_once()
    assert total == 42


@pytest.mark.asyncio
async def test_get_by_id_found(
        insurance_info_catalog_repository_impl,
        mock_async_db_session,
        mock_insurance_info_db_entity
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_insurance_info_db_entity
    mock_async_db_session.execute.return_value = mock_result

    record_id = mock_insurance_info_db_entity.id

    response = await insurance_info_catalog_repository_impl.get_by_id(record_id)

    mock_async_db_session.execute.assert_called_once()
    mock_result.scalar_one_or_none.assert_called_once()

    assert response is not None
    assert response.policy_number == mock_insurance_info_db_entity.policy_number
    assert response.company == mock_insurance_info_db_entity.company
    assert response.valid_from == mock_insurance_info_db_entity.valid_from
    assert response.valid_till == mock_insurance_info_db_entity.valid_till
    assert response.comment == mock_insurance_info_db_entity.comment


@pytest.mark.asyncio
async def test_get_by_id_NOT_found(
        insurance_info_catalog_repository_impl,
        mock_async_db_session
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_async_db_session.execute.return_value = mock_result

    response = await insurance_info_catalog_repository_impl.get_by_id(1)

    mock_async_db_session.execute.assert_called_once()
    mock_result.scalar_one_or_none.assert_called_once()

    assert response is None


@pytest.mark.asyncio
async def test_get_insurance_info_records_WITHOUT_filters(
        insurance_info_catalog_repository_impl,
        mock_async_db_session,
        mock_insurance_info_db_entity
):
    # Prepare mock response
    db_patient_1 = mock_insurance_info_db_entity
    db_patient_2 = mock_insurance_info_db_entity

    # Make them different
    db_patient_2.id = 2

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [db_patient_1, db_patient_2]
    mock_async_db_session.execute.return_value = mock_result

    # Initialize filters object
    empty_filters = InsuranceInfoCatalogFilterParams(
        patient_id_filter=None,
        financing_source_id_filter=None,
        policy_number_filter=None,
        company_name_filter=None,
        valid_from_filter=None,
        valid_till_filter=None
    )

    response = await insurance_info_catalog_repository_impl.get_insurance_info_records(
        filters=empty_filters,
    )

    mock_async_db_session.execute.assert_called_once()
    mock_result.scalars.return_value.all.assert_called_once()

    assert response is not None
    assert type(response) is list
    assert len(response) == 2


@pytest.mark.asyncio
async def test_get_insurance_info_records_WITH_filters(
        insurance_info_catalog_repository_impl,
        mock_async_db_session,
        mock_insurance_info_db_entity
):
    # Prepare mock response
    db_patient_1 = mock_insurance_info_db_entity
    db_patient_2 = mock_insurance_info_db_entity

    # Make them different
    db_patient_2.id = 2
    db_patient_2.company = 'Different Dummy Company Limited'

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [db_patient_2]
    mock_async_db_session.execute.return_value = mock_result

    # Initialize filters object
    filters = InsuranceInfoCatalogFilterParams(
        patient_id_filter=None,
        financing_source_id_filter=None,
        policy_number_filter=None,
        company_name_filter='Different Dummy Company Limited ',
        valid_from_filter=datetime.date(2025, 6, 5),
        valid_till_filter=datetime.date(2026, 6, 5)
    )

    response = await insurance_info_catalog_repository_impl.get_insurance_info_records(
        filters=filters,
    )

    mock_async_db_session.execute.assert_called_once()
    mock_result.scalars.return_value.all.assert_called_once()

    assert response is not None
    assert type(response) is list
    assert len(response) == 1
    expected_response = map_insurance_info_db_entity_to_response_schema(db_patient_2)
    assert response[0] == expected_response


@pytest.mark.asyncio
async def test_add_insurance_info_record(
    insurance_info_catalog_repository_impl,
    mock_async_db_session,
    mock_add_insurance_info_catalog_schema
):
    mock_async_db_session.add = MagicMock()
    mock_async_db_session.flush = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    async def set_id(obj):
        obj.id = 123

    mock_async_db_session.refresh = AsyncMock(side_effect=set_id)

    response = await insurance_info_catalog_repository_impl.add_insurance_info_record(
        mock_add_insurance_info_catalog_schema
    )

    mock_async_db_session.add.assert_called_once()
    mock_async_db_session.flush.assert_called_once()
    mock_async_db_session.refresh.assert_called_once()
    mock_async_db_session.commit.assert_called_once()

    expected_obj = map_insurance_info_create_schema_to_db_entity(mock_add_insurance_info_catalog_schema)
    expected_obj.id = 123
    expected_response = map_insurance_info_db_entity_to_response_schema(expected_obj)

    assert response == expected_response


@pytest.mark.asyncio
async def test_update_insurance_info_record(
    insurance_info_catalog_repository_impl,
    mock_async_db_session,
    mock_insurance_info_db_entity,
    mock_update_insurance_info_catalog_schema
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_insurance_info_db_entity
    mock_async_db_session.execute.return_value = mock_result

    mock_async_db_session.flush = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    async def set_id(obj):
        obj.id = mock_insurance_info_db_entity.id

    mock_async_db_session.refresh = AsyncMock(side_effect=set_id)

    response = await insurance_info_catalog_repository_impl.update_insurance_info_record(
        mock_insurance_info_db_entity.id,
        mock_update_insurance_info_catalog_schema
    )

    mock_async_db_session.execute.assert_called_once()
    mock_async_db_session.flush.assert_called_once()
    mock_async_db_session.refresh.assert_called_once()
    mock_async_db_session.commit.assert_called_once()

    expected_obj = map_insurance_info_update_schema_to_db_entity(
        mock_insurance_info_db_entity,
        mock_update_insurance_info_catalog_schema
    )
    expected_obj.id = mock_insurance_info_db_entity.id
    expected_response = map_insurance_info_db_entity_to_response_schema(expected_obj)

    assert response == expected_response


@pytest.mark.asyncio
async def test_delete_by_id(
    insurance_info_catalog_repository_impl,
    mock_async_db_session
):
    mock_async_db_session.execute = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    await insurance_info_catalog_repository_impl.delete_by_id(1)

    mock_async_db_session.execute.assert_called_once()
    mock_async_db_session.commit.assert_called_once()


