from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4

import pytest

from tests.fixtures import mock_patient_repository_impl


@pytest.mark.asyncio
async def test_get_by_id_found(
        mock_async_db_session,
        dummy_db_patient,
        dummy_domain_patient,
        mock_patient_repository_impl
):
    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = dummy_db_patient
    mock_async_db_session.execute.return_value = result_mock

    result = await mock_patient_repository_impl.get_by_id(dummy_db_patient.id)

    assert result is dummy_domain_patient
    mock_async_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(
        mock_async_db_session,
        mock_patient_repository_impl
):
    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = None
    mock_async_db_session.execute.return_value = result_mock

    result = await mock_patient_repository_impl.get_by_id(uuid4())

    assert result is None
    mock_async_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_iin_found(
        mock_async_db_session,
        dummy_db_patient,
        dummy_domain_patient,
        mock_patient_repository_impl
):
    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = dummy_db_patient
    mock_async_db_session.execute.return_value = result_mock

    result = await mock_patient_repository_impl.get_by_iin(dummy_db_patient.iin)

    assert result is dummy_domain_patient
    mock_async_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_iin_not_found(
        mock_async_db_session,
        dummy_db_patient,
        mock_patient_repository_impl
):
    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = None
    mock_async_db_session.execute.return_value = result_mock

    result = await mock_patient_repository_impl.get_by_iin(dummy_db_patient.iin)

    assert result is None
    mock_async_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_patients_without_filters_and_pagination_params(
        mock_async_db_session,
        dummy_db_patient,
        dummy_domain_patient,
        mock_patient_repository_impl,
):
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [
        dummy_db_patient,
        dummy_db_patient,
        dummy_db_patient
    ]
    mock_async_db_session.execute.return_value = result_mock

    result = await mock_patient_repository_impl.get_patients()

    assert isinstance(result, list)
    assert len(result) == 3
    mock_async_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_patients_with_filters_and_pagination_params(
        mock_async_db_session,
        mock_patient_repository_impl,
        monkeypatch,
):
    # Fake DB users (ORM)
    db_patient_1 = MagicMock()
    db_patient_1.id = 1
    db_patient_1.iin = "040806501543"
    db_patient_1.maiden_name = "Rusakova"

    db_patient_2 = MagicMock()
    db_patient_2.id = 2
    db_patient_2.iin = "111111111111"
    db_patient_2.maiden_name = "Ivanova"

    # Fake domain users
    domain_patient_1 = MagicMock(name="DomainPatient1")
    domain_patient_2 = MagicMock(name="DomainPatient2")

    # Fake mapper
    def fake_mapper(db_obj):
        if db_obj is db_patient_1:
            return domain_patient_1
        if db_obj is db_patient_2:
            return domain_patient_2

        return MagicMock(name="DomainUnknown")

    monkeypatch.setattr(
        "src.apps.patients.infrastructure.repositories.patient_repository.map_patient_db_entity_to_domain",
        fake_mapper,
    )

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [db_patient_1]
    mock_async_db_session.execute.return_value = result_mock

    result = await mock_patient_repository_impl.get_patients(
        filters={
            "patient_full_name_filter": "Ivan Ivanovich Ivanov",
            "iin": "040806501543",
            "profile_status": True,
            "attached_clinic_id": 123,
        },
        page=2,
        limit=10,
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] is domain_patient_1
    mock_async_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_patients_without_full_name_filter(
    mock_async_db_session,
        mock_patient_repository_impl,
):
    # Fake DB user (ORM)
    db_patient_1 = MagicMock()
    db_patient_1.id = 1
    db_patient_1.iin = "040806501543"
    db_patient_1.maiden_name = "Rusakova"

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [db_patient_1]
    mock_async_db_session.execute.return_value = result_mock

    # Passed dictionary without a full_name filter
    result = await mock_patient_repository_impl.get_patients(
        filters={"iin": "040806501543"},
    )

    assert result
    mock_async_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_patient(
    mock_async_db_session,
    mock_patient_repository_impl,
    dummy_db_patient,
    dummy_domain_patient,
    monkeypatch,
):
    # Patch the domain -> DB and DB -> domain mappers:
    monkeypatch.setattr(
        "src.apps.patients.infrastructure.repositories.patient_repository."
        "map_patient_domain_to_db_entity",
        lambda domain: dummy_db_patient,
    )
    monkeypatch.setattr(
        "src.apps.patients.infrastructure.repositories.patient_repository."
        "map_patient_db_entity_to_domain",
        lambda db_obj: dummy_domain_patient,
    )

    # Make sure no M2M lists (so we only get the initial + final reload)
    dummy_domain_patient.financing_sources_ids = []
    dummy_domain_patient.context_attributes_ids = []

    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = dummy_db_patient
    mock_async_db_session.execute.return_value = fake_result

    mock_async_db_session.add = MagicMock()
    mock_async_db_session.flush = AsyncMock()

    result = await mock_patient_repository_impl.create_patient(dummy_domain_patient)

    mock_async_db_session.add.assert_called_once_with(dummy_db_patient)
    assert mock_async_db_session.flush.await_count >= 1
    assert mock_async_db_session.add.call_count == 1
    assert result is dummy_domain_patient



@pytest.mark.asyncio
async def test_update_patient(
    mock_async_db_session,
    mock_patient_repository_impl,
    dummy_db_patient,
    dummy_domain_patient,
    monkeypatch,
):
    # Patch the domain -> DB and DB -> domain mappers:
    monkeypatch.setattr(
        "src.apps.patients.infrastructure.repositories.patient_repository."
        "map_patient_domain_to_db_entity",
        lambda domain: dummy_db_patient,
    )
    monkeypatch.setattr(
        "src.apps.patients.infrastructure.repositories.patient_repository."
        "map_patient_db_entity_to_domain",
        lambda db_obj: dummy_domain_patient,
    )

    # Give our dummy domain a real .id so the WHERE clause matches
    dummy_domain_patient.id = dummy_db_patient.id

    # Stub every execute() to return dummy_db_patient
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = dummy_db_patient
    mock_async_db_session.execute.return_value = fake_result

    mock_async_db_session.flush = AsyncMock()

    result = await mock_patient_repository_impl.update_patient(dummy_domain_patient)

    assert result is dummy_domain_patient

    assert mock_async_db_session.execute.call_count >= 2
    assert mock_async_db_session.flush.await_count >= 1



@pytest.mark.asyncio
async def test_delete_by_id(
        mock_async_db_session,
        mock_patient_repository_impl,
        dummy_db_patient,
):
    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = dummy_db_patient
    mock_async_db_session.execute.return_value = result_mock

    mock_async_db_session.delete = AsyncMock()

    await mock_patient_repository_impl.delete_by_id(dummy_db_patient.id)

    mock_async_db_session.execute.assert_called_once()
    mock_async_db_session.delete.assert_called_once_with(dummy_db_patient)



