import datetime
import uuid

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.apps.users.domain.enums import ActionsOnUserEnum
from src.apps.users.domain.models.user import UserDomain
from src.apps.users.infrastructure.schemas.user_schemas import UserSchema
from src.apps.users.services.user_service import UserService
from src.shared.exceptions import InvalidActionTypeError, NoInstanceFoundError, InstanceAlreadyExistsError


@pytest.mark.asyncio
async def test_get_by_id_success(dummy_user_repo, dummy_user_id, dummy_user_domain, dummy_logger):
    dummy_user_repo.get_by_id.return_value = dummy_user_domain
    service = UserService(dummy_user_repo, dummy_logger)

    result = await service.get_by_id(dummy_user_id)

    dummy_user_repo.get_by_id.assert_awaited_once_with(dummy_user_id)
    assert result is dummy_user_domain


@pytest.mark.asyncio
async def test_get_by_id_not_found_raises(dummy_user_repo, dummy_user_id, dummy_logger):
    dummy_user_repo.get_by_id.return_value = None
    service = UserService(dummy_user_repo, dummy_logger)

    with pytest.raises(NoInstanceFoundError) as exc:
        await service.get_by_id(dummy_user_id)

    err = exc.value
    assert err.status_code == 404
    assert str(dummy_user_id) in err.detail


@pytest.mark.asyncio
async def test_create_user_success(
        dummy_user_repo,
        dummy_user_domain,
        dummy_user_schema,
        dummy_logger
):
    dummy_user_repo.get_by_id.return_value = None
    dummy_user_repo.get_by_iin.return_value = None
    dummy_user_repo.create = AsyncMock(return_value='created record')

    service = UserService(dummy_user_repo, dummy_logger)

    # Patch the mapper
    with patch(
            "src.apps.users.services.user_service.map_user_schema_to_domain",
            return_value=dummy_user_domain
    ):
        result = await service.create(dummy_user_schema)

    # Ensure that all pre-checks were called
    dummy_user_repo.get_by_id.assert_awaited_once_with(dummy_user_schema.id)
    dummy_user_repo.get_by_iin.assert_awaited_once_with(dummy_user_schema.iin)

    dummy_user_repo.create.assert_awaited_once_with(dummy_user_domain)

    assert result == 'created record'


@pytest.mark.asyncio
async def test_create_user_duplicate_id_raises(
        dummy_user_repo,
        dummy_user_domain,
        dummy_user_schema,
        dummy_logger
):
    dummy_user_repo.get_by_id.return_value = dummy_user_domain
    service = UserService(dummy_user_repo, dummy_logger)

    with pytest.raises(InstanceAlreadyExistsError) as exc:
        await service.create(dummy_user_schema)

    err = exc.value
    assert err.status_code == 409
    assert str(dummy_user_domain.id) in err.detail


@pytest.mark.asyncio
async def test_create_user_duplicate_iin_raises(
        dummy_user_repo,
        dummy_user_domain,
        dummy_user_schema,
        dummy_logger
):
    dummy_user_repo.get_by_id.return_value = None
    dummy_user_repo.get_by_iin.return_value = dummy_user_domain
    service = UserService(dummy_user_repo, dummy_logger)

    with pytest.raises(InstanceAlreadyExistsError) as exc:
        await service.create(dummy_user_schema)

    err = exc.value
    assert err.status_code == 409
    assert dummy_user_domain.iin in err.detail


@pytest.mark.asyncio
async def test_update_user_not_found_raises(
        dummy_user_repo,
        dummy_user_id,
        dummy_logger,
        dummy_user_schema,
        dummy_user_domain
):
    dummy_user_repo.get_by_id.return_value = None
    service = UserService(dummy_user_repo, dummy_logger)

    with pytest.raises(NoInstanceFoundError):
        await service.update_user(dummy_user_schema)


@pytest.mark.asyncio
async def test_update_user_success(
        dummy_user_repo,
        dummy_user_domain,
        dummy_user_schema,
        dummy_logger
):
    dummy_user_repo.get_by_id.return_value = dummy_user_domain
    dummy_user_repo.update = AsyncMock(return_value="updated record")
    service = UserService(dummy_user_repo, dummy_logger)

    # Patch the mapper
    with patch(
            "src.apps.users.services.user_service.map_user_schema_to_domain",
            return_value=dummy_user_domain
    ):
        result = await service.update_user(dummy_user_schema)

    # Ensure that all pre-checks were called
    dummy_user_repo.get_by_id.assert_awaited_once_with(dummy_user_schema.id)

    assert result == "updated record"


@pytest.mark.asyncio
async def test_delete_user_not_found_raises(dummy_user_repo, dummy_user_id, dummy_logger):
    dummy_user_repo.get_by_id.return_value = None
    service = UserService(dummy_user_repo, dummy_logger)

    with pytest.raises(NoInstanceFoundError):
        await service.delete_user(dummy_user_id)


@pytest.mark.asyncio
async def test_delete_user_success(dummy_user_repo, dummy_user_domain, dummy_logger):
    dummy_user_repo.get_by_id.return_value = dummy_user_domain
    service = UserService(dummy_user_repo, dummy_logger)

    await service.delete_user(dummy_user_domain.id)

    dummy_user_repo.get_by_id.assert_awaited_once_with(dummy_user_domain.id)
    dummy_user_repo.delete.assert_awaited_once_with(dummy_user_domain.id)
