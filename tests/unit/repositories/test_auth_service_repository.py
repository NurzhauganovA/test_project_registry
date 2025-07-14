from unittest.mock import MagicMock, AsyncMock
from httpx import ConnectError, HTTPStatusError
from httpx import Request

import pytest

from src.shared.infrastructure.auth_service_adapter.repositories.auth_service_repository import (
    AuthServiceRepositoryImpl
)
from src.core.i18n import _
from src.shared.exceptions import (
    AuthServiceConnectionError,
    AuthServiceError
)


@pytest.mark.asyncio
async def test_base_url_not_set_raises_connection_error(
        mock_http_client,
        dummy_logger
):
    repo = AuthServiceRepositoryImpl(
        http_client=mock_http_client,
        base_url="",
        logger=dummy_logger,
    )

    with pytest.raises(AuthServiceConnectionError) as exc:
        await repo.get_permissions("dummy_access_token")

    dummy_logger.critical.assert_called_once_with(
        "- AUTH_SERVICE_BASE_URL is not set!"
    )
    err = exc.value
    assert err.status_code == 503
    # Check that detail is taken from the translation function
    assert err.detail == _("Something went wrong. Please, try again later.")


@pytest.mark.asyncio
async def test_with_protocol_in_base_url(
        mock_http_client,
        dummy_logger
):
    fake_response = MagicMock()
    fake_response.raise_for_status = MagicMock()
    fake_response.json = MagicMock(return_value=[{"x": 1}])
    mock_http_client.get = AsyncMock(return_value=fake_response)

    repo = AuthServiceRepositoryImpl(
        http_client=mock_http_client,
        base_url="https://auth.example.com",
        logger=dummy_logger,
    )

    result = await repo.get_permissions("dummy_access_token")

    mock_http_client.get.assert_awaited_once_with(
        "https://auth.example.com/users/permissions",
        headers={"Authorization": "Bearer dummy_access_token"},
    )
    assert result == [{"x": 1}]


@pytest.mark.asyncio
async def test_http_status_error_converted_to_auth_service_error(
        mock_http_client,
        dummy_logger
):
    fake_response = MagicMock()
    fake_response.status_code = 401
    fake_response.text = "Unauthorized"
    def raise_for_status():
        raise HTTPStatusError(
            "err",
            request=Request("GET", "url"),
            response=fake_response
        )
    fake_response.raise_for_status = raise_for_status

    mock_http_client.get = AsyncMock(return_value=fake_response)
    repo = AuthServiceRepositoryImpl(
        http_client=mock_http_client,
        base_url="https://auth",
        logger=dummy_logger,
    )

    # Act & Assert
    with pytest.raises(AuthServiceError) as exc:
        await repo.get_permissions("dummy_access_token")
    err = exc.value
    assert err.status_code == 401
    assert err.detail == "Unauthorized"


@pytest.mark.asyncio
async def test_connect_error_converted_to_connection_error(
        mock_http_client,
        dummy_logger
):
    mock_http_client.get = AsyncMock(side_effect=ConnectError("fail"))
    repo = AuthServiceRepositoryImpl(
        http_client=mock_http_client,
        base_url="https://auth",
        logger=dummy_logger,
    )

    with pytest.raises(AuthServiceConnectionError) as exc:
        await repo.get_permissions("dummy_access_token")

    dummy_logger.critical.assert_called_once_with("HTTP 503 - Auth Service is not available.")
    err = exc.value
    assert err.status_code == 503
    assert err.detail == _("Something went wrong. Please, try again later.")


@pytest.mark.asyncio
async def test_non_list_response_raises_auth_service_error(
        mock_http_client,
        dummy_logger
):
    fake_response = MagicMock()
    fake_response.raise_for_status = MagicMock()
    fake_response.json = MagicMock(return_value={"not": "a list"})
    mock_http_client.get = AsyncMock(return_value=fake_response)

    repo = AuthServiceRepositoryImpl(
        http_client=mock_http_client,
        base_url="https://auth",
        logger=dummy_logger,
    )

    with pytest.raises(AuthServiceError) as exc:
        await repo.get_permissions("dummy_access_token")

    dummy_logger.error.assert_called_once_with(
        "The data received from the Auth Service is not as expected "
        "(List). From: auth_service_repository.get_permissions()."
    )
    err = exc.value
    assert err.status_code == 500
    assert err.detail == _("Something went wrong. Please, try again later.")
    