import uuid
import datetime
import pytest
from unittest.mock import MagicMock

from src.apps.users.domain.models.user import UserDomain
from src.apps.users.infrastructure.repositories.user_repository import (
    SQLAlchemyUserRepository
)


@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_async_db_session, dummy_logger):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = None
    mock_async_db_session.execute.return_value = fake_result

    result = await repo.get_by_id(uuid.uuid4())
    assert result is None
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_found(mock_async_db_session, dummy_db_user, dummy_user_domain, dummy_logger):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = dummy_db_user
    mock_async_db_session.execute.return_value = fake_result

    result = await repo.get_by_id(dummy_db_user.id)
    assert result is dummy_user_domain
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_iin_not_found(mock_async_db_session, dummy_logger):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = None
    mock_async_db_session.execute.return_value = fake_result

    result = await repo.get_by_iin("000000000000")
    assert result is None
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_iin_found(mock_async_db_session, dummy_db_user, dummy_user_domain, dummy_logger):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = dummy_db_user
    mock_async_db_session.execute.return_value = fake_result

    result = await repo.get_by_iin(dummy_db_user.iin)
    assert result is dummy_user_domain
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_calls_commit_and_refresh(dummy_logger, mock_async_db_session, dummy_user_domain, dummy_db_user):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)

    result = await repo.create(dummy_user_domain)

    mock_async_db_session.add.assert_called_once_with(dummy_db_user)
    mock_async_db_session.commit.assert_awaited_once()
    mock_async_db_session.refresh.assert_awaited_once_with(dummy_db_user)

    assert result is dummy_user_domain


@pytest.mark.asyncio
async def test_update_modifies_fields_and_returns_domain(
        mock_async_db_session,
        dummy_user_domain,
        dummy_db_user,
        dummy_logger,
        patch_map_entity_to_domain
):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)

    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = dummy_db_user
    mock_async_db_session.execute.return_value = fake_result

    new_domain = UserDomain(
        id=dummy_user_domain.id,
        first_name="Alice",
        last_name="Wonderland",
        middle_name="L",
        iin="987654321098",
        date_of_birth=datetime.date(1985, 5, 5),
        client_roles=["editor"],
        enabled=False,
        served_patient_types=['adult', 'child'],
        served_referral_types=['with_referral', 'without_referral'],
        served_referral_origins=["from_external_organization", "self_registration"],
        served_payment_types = ["GOBMP", "DMS", "OSMS", "paid"],
        specializations=[
            {
                "name": "Therapist",
                "id": str(uuid.uuid4())
            }
        ],
        attachment_data=dummy_user_domain.attachment_data,
    )

    result = await repo.update(new_domain)

    assert dummy_db_user.first_name == "Alice"
    assert dummy_db_user.last_name == "Wonderland"
    assert dummy_db_user.middle_name == "L"
    assert dummy_db_user.iin == "987654321098"
    assert dummy_db_user.date_of_birth == datetime.date(1985, 5, 5)
    assert dummy_db_user.client_roles == ["editor"]
    assert dummy_db_user.enabled is False

    mock_async_db_session.commit.assert_awaited_once()
    mock_async_db_session.refresh.assert_awaited_once_with(dummy_db_user)

    assert result is dummy_user_domain


@pytest.mark.asyncio
async def test_delete_calls_session_delete(dummy_logger, mock_async_db_session, dummy_db_user):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)

    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = dummy_db_user
    mock_async_db_session.execute.return_value = fake_result

    await repo.delete(dummy_db_user.id)

    mock_async_db_session.delete.assert_awaited_once_with(dummy_db_user)
