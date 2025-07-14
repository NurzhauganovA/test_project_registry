import pytest

from src.shared.dependencies.check_user_permissions import (
    get_permissions,
    check_user_permissions
)
from src.shared.exceptions import AccessDeniedError
from src.core.i18n import _


@pytest.mark.asyncio
async def test_get_permissions_returns_list_and_passes_token(dummy_auth_service_repository):
    token = "dummy_access_token"
    result = await get_permissions(
        auth_service_repository=dummy_auth_service_repository,
        token=token
    )
    assert dummy_auth_service_repository.called_with == token
    assert result == dummy_auth_service_repository.perms


@pytest.mark.asyncio
async def test_and_passes_if_all_present(dummy_permissions):
    dep = check_user_permissions(
        resources=[
            {"resource_name": "dummy_resource_r"},
            {"resource_name": "dummy_resource_w"},
        ],
        require_all=True,
    )
    await dep(permitted_resources=dummy_permissions)


@pytest.mark.asyncio
async def test_and_fails_if_any_missing(dummy_permissions):
    dep = check_user_permissions(
        resources=[
            {"resource_name": "dummy_resource_r"},
            {"resource_name": "dummy_resource_missing"},
        ],
        require_all=True,
    )
    with pytest.raises(AccessDeniedError) as exc:
        await dep(permitted_resources=dummy_permissions)

    err = exc.value
    assert err.status_code == 403
    assert err.detail == _("Access denied. You're not allowed to proceed this operation.")


@pytest.mark.asyncio
async def test_or_passes_if_any_present(dummy_permissions):
    dep = check_user_permissions(
        resources=[
            {"resource_name": "dummy_resource_r"},
            {"resource_name": "dummy_resource_missing"},
        ],
        require_all=False,
    )
    await dep(permitted_resources=dummy_permissions)


@pytest.mark.asyncio
async def test_or_fails_if_none_present(dummy_permissions):
    dep = check_user_permissions(
        resources=[
            {"resource_name": "dummy_resource_missing"},
        ],
        require_all=False,
    )
    with pytest.raises(AccessDeniedError) as exc:
        await dep(permitted_resources=dummy_permissions)
    err = exc.value
    assert err.status_code == 403


@pytest.mark.asyncio
async def test_and_with_scopes_all_ok(dummy_permissions_with_scopes):
    dep = check_user_permissions(
        resources=[
            {"resource_name": "dummy_resource_r", "scopes": ["read"]},
            {"resource_name": "dummy_resource_w", "scopes": ["write"]},
        ],
        require_all=True,
    )
    await dep(permitted_resources=dummy_permissions_with_scopes)


@pytest.mark.asyncio
async def test_and_with_scopes_fails_if_scope_missing(dummy_permissions_with_scopes):
    dep = check_user_permissions(
        resources=[
            {"resource_name": "dummy_resource_r", "scopes": ["read"]},
            {"resource_name": "dummy_resource_w", "scopes": ["admin"]},
        ],
        require_all=True,
    )
    with pytest.raises(AccessDeniedError):
        await dep(permitted_resources=dummy_permissions_with_scopes)


@pytest.mark.asyncio
async def test_or_with_scopes_passes(dummy_permissions_with_scopes):
    dep = check_user_permissions(
        resources=[
            {"resource_name": "dummy_resource_r", "scopes": ["read"]},
            {"resource_name": "dummy_resource_w", "scopes": ["admin"]},
        ],
        require_all=False,
    )
    await dep(permitted_resources=dummy_permissions_with_scopes)


@pytest.mark.asyncio
async def test_or_with_scopes_fails(dummy_permissions_with_scopes):
    dep = check_user_permissions(
        resources=[
            {"resource_name": "dummy_resource_r", "scopes": ["admin"]},
            {"resource_name": "dummy_resource_w", "scopes": ["admin"]},
        ],
        require_all=False,
    )
    with pytest.raises(AccessDeniedError):
        await dep(permitted_resources=dummy_permissions_with_scopes)
