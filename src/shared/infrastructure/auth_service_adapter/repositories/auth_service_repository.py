from typing import Any, Dict, List

from httpx import AsyncClient, ConnectError, HTTPStatusError

from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import AuthServiceConnectionError, AuthServiceError
from src.shared.infrastructure.auth_service_adapter.interfaces.auth_service_repository_interface import (
    AuthServiceRepositoryInterface,
)


class AuthServiceRepositoryImpl(AuthServiceRepositoryInterface):
    """
    Repository for communication with Auth Service (ecosystem's microservice).
    """

    def __init__(self, http_client: AsyncClient, base_url: str, logger: LoggerService):
        self._http_client = http_client
        self._logger = logger
        self.base_url = base_url

    async def get_permissions(self, access_token: str) -> List[Dict[str, Any]]:
        if not self.base_url:
            self._logger.critical("- AUTH_SERVICE_BASE_URL is not set!")
            raise AuthServiceConnectionError(
                status_code=503,
                detail=_("Something went wrong. Please, try again later."),
            )

        base_url = self.base_url

        url = f"{base_url}/users/permissions"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = await self._http_client.get(url, headers=headers)
            response.raise_for_status()

        except HTTPStatusError as exc:
            raise AuthServiceError(
                status_code=exc.response.status_code, detail=exc.response.text
            ) from exc

        except ConnectError as exc:
            error_message = "Auth Service is not available."
            self._logger.critical(f"HTTP 503 - {error_message}")
            raise AuthServiceConnectionError(
                status_code=503,
                detail=_("Something went wrong. Please, try again later."),
            ) from exc

        data = response.json()
        if not isinstance(data, list):
            self._logger.error(
                "The data received from the Auth Service is not as expected "
                "(List). From: auth_service_repository.get_permissions()."
            )
            raise AuthServiceError(
                status_code=500,
                detail=_("Something went wrong. Please, try again later."),
            )

        return data
