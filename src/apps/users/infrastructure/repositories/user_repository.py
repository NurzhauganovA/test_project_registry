from uuid import UUID

from sqlalchemy import select

from src.apps.users.domain.models.user import UserDomain
from src.apps.users.infrastructure.db_models.models import User
from src.apps.users.interfaces.user_repository_interface import UserRepositoryInterface
from src.apps.users.mappers import (
    map_user_db_entity_to_domain,
    map_user_domain_to_db_entity,
)
from src.shared.helpers.decorators import handle_unique_violation, transactional
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyUserRepository(BaseRepository, UserRepositoryInterface):
    """
    SQL Alchemy repository for working with users.
    """

    async def get_by_id(self, user_id: UUID) -> UserDomain | None:
        query = select(User).where(User.id == user_id)
        result = await self._async_db_session.execute(query)
        user = result.scalars().first()

        if not user:
            return None

        return map_user_db_entity_to_domain(user)

    async def get_by_iin(self, iin: str) -> UserDomain | None:
        query = select(User).where(User.iin == iin)
        result = await self._async_db_session.execute(query)
        user = result.scalars().first()

        if not user:
            return None

        return map_user_db_entity_to_domain(user)

    @transactional
    @handle_unique_violation
    async def create(self, user: UserDomain) -> UserDomain:
        user_to_add = map_user_domain_to_db_entity(user)

        self._async_db_session.add(user_to_add)
        await self._async_db_session.commit()
        await self._async_db_session.refresh(user_to_add)

        return map_user_db_entity_to_domain(user_to_add)

    @transactional
    async def update(self, user: UserDomain) -> UserDomain:
        query = select(User).where(User.id == user.id)
        result = await self._async_db_session.execute(query)
        user_to_update = result.scalars().first()

        user_with_updated_fields = map_user_domain_to_db_entity(
            user=user,
            existing_db_entity=user_to_update
        )

        await self._async_db_session.commit()
        await self._async_db_session.refresh(user_with_updated_fields)

        return map_user_db_entity_to_domain(user_with_updated_fields)

    @transactional
    async def delete(self, user_id: UUID) -> None:
        query = select(User).where(User.id == user_id)
        result = await self._async_db_session.execute(query)
        user_to_delete = result.scalars().first()

        await self._async_db_session.delete(user_to_delete)
        await self._async_db_session.commit()
