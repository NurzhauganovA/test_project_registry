import datetime
import uuid

import pytest

from unittest.mock import Mock, AsyncMock, MagicMock

from src.apps.registry.domain.enums import AppointmentStatusEnum
from src.apps.registry.infrastructure.db_models.models import Appointment
from src.apps.registry.infrastructure.repositories.appointment_repository import AppointmentRepositoryImpl
from tests.fixtures import mock_async_db_session


@pytest.mark.asyncio
async def test_get_by_id_success(
        mock_async_db_session,
        dummy_domain_appointment,
        dummy_db_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=dummy_db_appointment)
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_id(dummy_db_appointment.id)

    assert result is not None
    assert result.id == dummy_domain_appointment.id


@pytest.mark.asyncio
async def test_get_by_id_not_found(
        mock_async_db_session,
        dummy_domain_appointment,
        dummy_db_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=None)
    mock_async_db_session.execute.return_value = fake_result
    fake_id = 404

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_id(fake_id)

    assert result is None


@pytest.mark.asyncio
async def test_add_appointment(
        mock_async_db_session,
        dummy_domain_appointment,
        dummy_db_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=dummy_db_appointment)
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.add(dummy_domain_appointment)
    result.id = dummy_domain_appointment.id

    assert result is not None
    assert result.id == dummy_domain_appointment.id


@pytest.mark.asyncio
async def test_add_appointment_without_patient(
        mock_async_db_session,
        dummy_domain_appointment,
        dummy_db_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=dummy_db_appointment)
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    dummy_domain_appointment.patient_id = None
    result = await repository.add(dummy_domain_appointment)
    result.id = dummy_domain_appointment.id

    assert result is not None
    assert result.id == dummy_domain_appointment.id


@pytest.mark.asyncio
async def test_update_appointment(
        mock_async_db_session,
        dummy_domain_appointment,
        dummy_db_appointment,
        dummy_logger,
        mocker
) -> None:
    dummy_db_appointment.patient_id = "updated_patient_id"
    dummy_db_appointment.status = AppointmentStatusEnum.CANCELLED

    dummy_domain_appointment.patient_id = "updated_patient_id"
    dummy_domain_appointment.status = AppointmentStatusEnum.CANCELLED

    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=dummy_db_appointment)
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.update(dummy_domain_appointment)

    assert result is not None
    assert result.id == dummy_domain_appointment.id


@pytest.mark.asyncio
async def test_delete_appointment(
        mock_async_db_session,
        dummy_db_appointment,
        dummy_domain_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_result.scalar_one_or_none = Mock(return_value=dummy_db_appointment)
    mock_async_db_session.execute.return_value = fake_result

    mock_async_db_session.delete = AsyncMock()

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    await repository.delete_by_id(dummy_domain_appointment.id)

    mock_async_db_session.delete.assert_called_once_with(dummy_db_appointment)


@pytest.mark.asyncio
async def test_get_by_schedule_success(
        mock_async_db_session,
        dummy_db_appointment,
        dummy_domain_appointment,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock()
    fake_scalars = mocker.MagicMock()
    fake_scalars.all.return_value = [dummy_db_appointment, dummy_db_appointment]
    fake_result.scalars.return_value = fake_scalars
    mock_async_db_session.execute.return_value = fake_result

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_schedule_id(
        dummy_db_appointment.schedule_id,
        page=1,
        limit=10
    )

    assert isinstance(result, list)
    assert result[0].id == dummy_domain_appointment.id
    assert result[1].id == dummy_db_appointment.id


@pytest.mark.asyncio
async def test_get_by_schedule_not_found(
        mock_async_db_session,
        dummy_logger,
        mocker
) -> None:
    fake_result = mocker.MagicMock(return_value=[])
    fake_result.scalars.return_value.all.return_value = fake_result
    mock_async_db_session.execute.return_value = fake_result
    fake_id = uuid.uuid4()

    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_schedule_id(
        fake_id,
        page=1,
        limit=10
    )

    assert isinstance(result, list)
    assert result == []


@pytest.mark.asyncio
async def test_get_appointments_success(
        mock_async_db_session,
        mocker,
        dummy_logger,
) -> None:
    db_appointment_1 = MagicMock(spec=Appointment)
    db_appointment_2 = MagicMock(spec=Appointment)
    appointments_in_db = [db_appointment_1, db_appointment_2]

    fake_result = MagicMock()
    fake_result.scalars.return_value.all.return_value = appointments_in_db
    mock_async_db_session.execute = AsyncMock(return_value=fake_result)

    mock_conditions = [True]
    repository = AppointmentRepositoryImpl(mock_async_db_session, dummy_logger)
    mocker.patch.object(repository, '_build_filters', return_value=mock_conditions)

    mocker.patch(
        'src.apps.registry.infrastructure.repositories.appointment_repository.map_appointment_db_entity_to_domain',
        side_effect=lambda x: f"domain_{x}"
    )

    filters = {"patient_id": "some-uuid"}
    limit = 5
    page = 2
    results = await repository.get_appointments(filters, limit, page)

    mock_async_db_session.execute.assert_awaited_once()
    assert results == [f"domain_{db_appointment_1}", f"domain_{db_appointment_2}"]


@pytest.mark.asyncio
async def test_get_appointments_no_filters(mocker):
    mock_async_db_session = MagicMock()
    mock_logger = MagicMock()
    repository = AppointmentRepositoryImpl(mock_async_db_session, mock_logger)

    db_appointments = []
    fake_result = MagicMock()
    fake_result.scalars.return_value.all.return_value = db_appointments
    mock_async_db_session.execute = AsyncMock(return_value=fake_result)

    mocker.patch.object(repository, '_build_filters', return_value=[])

    mocker.patch(
        'src.apps.registry.infrastructure.repositories.appointment_repository.map_appointment_db_entity_to_domain',
        side_effect=lambda x: f"domain_{x}"
    )

    results = await repository.get_appointments({}, 10, 1)

    mock_async_db_session.execute.assert_awaited_once()
    assert results == []
