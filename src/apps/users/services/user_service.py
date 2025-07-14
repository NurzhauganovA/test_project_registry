from typing import Union
from uuid import UUID

from src.apps.users.domain.enums import ActionsOnUserEnum
from src.apps.users.domain.models.user import UserDomain
from src.apps.users.infrastructure.schemas.user_schemas import UserSchema
from src.apps.users.interfaces.user_repository_interface import UserRepositoryInterface
from src.apps.users.mappers import map_user_schema_to_domain
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import (
    InstanceAlreadyExistsError,
    InvalidActionTypeError,
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

        incoming_specializations = dto.get_specializations_as_dict()
        final_specializations = (
            incoming_specializations
            if incoming_specializations
            else existing_user.specializations
        )

        # Prepare a domain object manually
        user_domain = UserDomain(
            id=dto.id,
            first_name=dto.first_name or existing_user.first_name,
            last_name=dto.last_name or existing_user.last_name,
            middle_name=dto.middle_name or existing_user.middle_name,
            iin=dto.iin or existing_user.iin,
            date_of_birth=dto.date_of_birth or existing_user.date_of_birth,
            client_roles=dto.client_roles or existing_user.client_roles,
            enabled=dto.enabled or existing_user.enabled,
            served_patient_types=dto.served_patient_types
            or existing_user.served_patient_types,
            served_referral_types=dto.served_referral_types
            or existing_user.served_referral_types,
            served_referral_origins=dto.served_referral_origins
            or existing_user.served_referral_origins,
            served_payment_types=dto.served_payment_types
            or existing_user.served_payment_types,
            attachment_data=dto.attachment_data or existing_user.attachment_data,
            specializations=final_specializations or existing_user.specializations,
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

    async def handle_event(
        self, action: ActionsOnUserEnum, user_data: Union[UserSchema, UUID]
    ) -> UserDomain | None:
        """
        Handle an event from Kafka. Calls the appropriate
        method for each action type.

        :param action: ActionsOnUserEnum: create, update and delete
        :param user_data: User Pydantic schema or theirs UUID

        :raises InvalidActionTypeError: If an unsupported action type is provided
        """
        if action == ActionsOnUserEnum.CREATE:
            if not isinstance(user_data, UserSchema):
                return None

            await self.create(user_data)
            return None

        elif action == ActionsOnUserEnum.UPDATE:
            if not isinstance(user_data, UserSchema):
                return None

            await self.update_user(user_data)
            return None

        elif action == ActionsOnUserEnum.DELETE:
            # If a Pydantic model has arrived, we take .id from it, otherwise we expect UUID right away
            if isinstance(user_data, UserSchema):
                uid = user_data.id
                # if there is no id in the scheme, just exit
                if uid is None:
                    return None
            else:
                # here user_data is already UUID due to the declared Union
                uid = user_data

            await self.delete_user(uid)
            return None

        else:
            raise InvalidActionTypeError(
                status_code=500,
                detail=_(
                    "Couldn't handle an event. Unsupported action type: '%(ACTION)s'."
                )
                % {"ACTION": action},
            )
