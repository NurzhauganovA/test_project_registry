from uuid import UUID

from src.apps.users.domain.models.user import UserDomain
from src.apps.users.infrastructure.schemas.user_schemas import UserSchema
from src.apps.users.interfaces.user_repository_interface import UserRepositoryInterface
from src.apps.users.mappers import map_user_schema_to_domain
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import (
    InstanceAlreadyExistsError,
    NoInstanceFoundError,
)


class UserService:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        logger: LoggerService,
    ):
        self._user_repository = user_repository
        self._logger = logger

    async def get_by_id(self, user_id: UUID) -> UserDomain:
        """
        Retrieves a user by their ID

        :raises NoInstanceFoundError: If no user is found with a given ID
        """
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("User with ID: %(ID)s not found." % {"ID": user_id}),
            )

        return user

    async def create(self, dto: UserSchema) -> UserDomain:
        """
        Creates a user

        :param dto: User Pydantic schema

        :raises InstanceAlreadyExistsError: If a user with the same ID already exists
        :return: UserDomain object
        """
        # Check if a user already exists
        existing_user_by_id = await self._user_repository.get_by_id(dto.id)
        if existing_user_by_id:
            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_(
                    "User with ID: %(ID)s already exists."
                    % {"ID": existing_user_by_id.id}
                ),
            )

        existing_user_by_iin = await self._user_repository.get_by_iin(dto.iin)
        if existing_user_by_iin:
            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_(
                    "User with IIN: %(IIN)s already exists."
                    % {"IIN": existing_user_by_iin.iin}
                ),
            )

        # Prepare domain object
        user_domain = map_user_schema_to_domain(dto)

        return await self._user_repository.create(user_domain)

    async def update_user(self, dto: UserSchema) -> UserDomain:
        """
        Updates a user

        :param dto: User Pydantic schema

        :raises NoInstanceFoundError: If a user with given ID doesn't exist
        :return: UserDomain object
        """
        existing_user = await self._user_repository.get_by_id(dto.id)
        if not existing_user:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("User with ID: %(ID)s not found." % {"ID": dto.id}),
            )

        # Prepare a domain object manually
        user_domain = map_user_schema_to_domain(
            user_schema=dto,
            existing=existing_user,
        )

        return await self._user_repository.update(user_domain)

    async def delete_user(self, user_id: UUID) -> None:
        """
        Deletes a user

        :raises NoInstanceFoundError: If a user with a given ID doesn't exist
        """
        # Check if a user doesn't exist
        existing_user = await self._user_repository.get_by_id(user_id)
        if not existing_user:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("User with ID: %(ID)s not found." % {"ID": user_id}),
            )

        await self._user_repository.delete(user_id)
