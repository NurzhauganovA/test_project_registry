import uuid
import datetime
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

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


@pytest.mark.asyncio
async def test_get_by_id_found(mock_async_db_session, dummy_db_user, dummy_user_domain, dummy_logger):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = dummy_db_user
    mock_async_db_session.execute.return_value = fake_result

    # Patch the mapper
    with patch(
            "src.apps.users.infrastructure.repositories.user_repository.map_user_db_entity_to_domain",
            return_value=dummy_user_domain
    ):
        result = await repo.create(dummy_user_domain)

    # Check that return value is 'UserDomain' type
    assert isinstance(result, type(dummy_user_domain))
    assert result.id == dummy_user_domain.id


@pytest.mark.asyncio
async def test_get_by_iin_not_found(mock_async_db_session, dummy_logger):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = None
    mock_async_db_session.execute.return_value = fake_result

    result = await repo.get_by_iin("000000000000")
    assert result is None


@pytest.mark.asyncio
async def test_get_by_iin_found(mock_async_db_session, dummy_db_user, dummy_user_domain, dummy_logger):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = dummy_db_user
    mock_async_db_session.execute.return_value = fake_result

    # Patch the mapper
    with patch(
            "src.apps.users.infrastructure.repositories.user_repository.map_user_db_entity_to_domain",
            return_value=dummy_user_domain
    ):
        result = await repo.create(dummy_user_domain)

    # Check that return value is 'UserDomain' type
    assert isinstance(result, type(dummy_user_domain))
    assert result.id == dummy_user_domain.id


@pytest.mark.asyncio
async def test_create_calls_commit_and_refresh(dummy_logger, mock_async_db_session, dummy_user_domain, dummy_db_user):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)

    # Patch the mappers
    with patch(
            "src.apps.users.infrastructure.repositories.user_repository.map_user_domain_to_db_entity",
            return_value=dummy_db_user
    ), patch(
        "src.apps.users.infrastructure.repositories.user_repository.map_user_db_entity_to_domain",
        return_value=dummy_user_domain
    ):
        result = await repo.create(dummy_user_domain)

    mock_async_db_session.add.assert_called_once_with(dummy_db_user)
    mock_async_db_session.commit.assert_awaited_once()
    mock_async_db_session.refresh.assert_awaited_once_with(dummy_db_user)

    # Check that return value is 'UserDomain' type
    assert isinstance(result, type(dummy_user_domain))


@pytest.mark.asyncio
async def test_update_modifies_fields_and_returns_domain(
        mock_async_db_session,
        dummy_user_domain,
        dummy_db_user,
        dummy_logger,
):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = dummy_db_user
    mock_async_db_session.execute.return_value = AsyncMock(return_value=mock_result)

    # Patch the mappers
    with patch(
            "src.apps.users.infrastructure.repositories.user_repository.map_user_domain_to_db_entity",
            return_value=dummy_db_user
    ), patch(
        "src.apps.users.infrastructure.repositories.user_repository.map_user_db_entity_to_domain",
        return_value=dummy_user_domain
    ):
        result = await repo.create(dummy_user_domain)

    mock_async_db_session.commit.assert_awaited_once()
    mock_async_db_session.refresh.assert_awaited_once_with(dummy_db_user)

    # Check that return value is 'UserDomain' type
    assert isinstance(result, type(dummy_user_domain))


@pytest.mark.asyncio
async def test_delete_calls_session_delete(dummy_logger, mock_async_db_session, dummy_db_user):
    repo = SQLAlchemyUserRepository(mock_async_db_session, dummy_logger)

    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = dummy_db_user
    mock_async_db_session.execute.return_value = fake_result

    await repo.delete(dummy_db_user.id)

    mock_async_db_session.delete.assert_awaited_once_with(dummy_db_user)
