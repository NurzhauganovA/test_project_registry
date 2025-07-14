from unittest.mock import MagicMock, AsyncMock
from httpx import ConnectError

import pytest

from src.shared.exceptions import (
    RpnIntegrationServiceConnectionError,
    RpnIntegrationServiceError
)
from src.core.i18n import _
from src.shared.infrastructure.rpn_integration_service_adapter.repositories.rpn_integration_service_repository import \
    RpnIntegrationServiceRepositoryImpl


@pytest.mark.asyncio
async def test_base_url_not_set_raises_connection_error(
        dummy_logger,
        mock_http_client
):
    repository = RpnIntegrationServiceRepositoryImpl(
        http_client=mock_http_client,
        base_url="",
        logger=dummy_logger
    )

    with pytest.raises(RpnIntegrationServiceConnectionError) as exc:
        await repository.get_specialist_current_attachment_info("fake_iin")

    dummy_logger.critical.assert_called_once_with(
        "- RPN_INTEGRATION_SERVICE_BASE_URL is not set!"
    )
    err = exc.value
    assert err.status_code == 503
    # Check that detail is taken from the translation function
    assert err.detail == _("Something went wrong. Please, try again later.")


@pytest.mark.asyncio
async def test_rpn_service_is_not_available_and_raises_connection_error(
        dummy_logger,
        mock_http_client
):
    mock_http_client.post = AsyncMock(side_effect=ConnectError("unable to connect"))

    repository = RpnIntegrationServiceRepositoryImpl(
        http_client=mock_http_client,
        base_url="https://example:8010",
        logger=dummy_logger
    )

    with pytest.raises(RpnIntegrationServiceConnectionError) as err:
        await repository.get_specialist_current_attachment_info("fake_iin")

    dummy_logger.critical.assert_called_once_with(
        "HTTP 503 - RPN Integration Service is not available."
    )

    err = err.value
    assert err.detail == _("Something went wrong. Please, try again later.")
    assert err.status_code == 503


@pytest.mark.asyncio
async def test_non_dict_response_raises_auth_service_error(
        mock_http_client,
        dummy_logger
):
    fake_response = MagicMock()
    fake_response.raise_for_status = MagicMock()
    fake_response.json = MagicMock(return_value={
        'data': {
            'record': ['not a dict']
        }
    })

    mock_http_client.post = AsyncMock(return_value=fake_response)

    repository = RpnIntegrationServiceRepositoryImpl(
        http_client=mock_http_client,
        base_url="https://example:8010",
        logger=dummy_logger
    )

    with pytest.raises(RpnIntegrationServiceError) as exc:
        await repository.get_specialist_current_attachment_info("fake_iin")

    dummy_logger.critical.assert_called_once_with(
        "The data received from the RPN Integration Service is not as expected "
        "(Dict). From: auth_service_repository.get_specialist_current_attachment_info()."
    )
    err = exc.value
    assert err.status_code == 500
    assert err.detail == _("Something went wrong. Please, try again later.")
