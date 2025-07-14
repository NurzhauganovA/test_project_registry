from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AuthServiceRepositoryInterface(ABC):
    @abstractmethod
    async def get_permissions(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Request to Auth Service to get a list of user permissions
        based on their access_token.

        :param access_token: User access token

        :return: List of permissions
        :raises AuthServiceError: Error from the Auth Service itself
        :raises AuthServiceConnectionError: If Auth Service is down

        Expected response format: List[Dict[str, Any]], for example:
            [
                {"resource_name": str, "resource_id": str},
                ...
            ]
        """
        pass
