from abc import ABC, abstractmethod
from uuid import UUID

from src.apps.users.domain.models.user import UserDomain


class UserRepositoryInterface(ABC):
    """
    Repository for working with users.
    """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserDomain | None:
        pass

    @abstractmethod
    async def get_by_iin(self, iin: str) -> UserDomain | None:
        pass

    @abstractmethod
    async def create(self, user: UserDomain) -> UserDomain:
        pass

    @abstractmethod
    async def update(self, user: UserDomain) -> UserDomain:
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        pass
