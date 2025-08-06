from dependency_injector.wiring import Provide, inject
from mis_eventer_lib.eventer_consumer import EventerListener
from mis_eventer_lib.schemas.event_schema import (
    EventerActionEnum,
    EventerResponseSchema,
)

from src.apps.users.container import UsersContainer
from src.apps.users.infrastructure.schemas.user_schemas import DeleteUserSchema, UserSchema
from src.apps.users.services.user_service import UserService
from src.core.logger import LoggerService, logger
from src.core.settings import project_settings
from src.shared.helpers.decorators import handle_kafka_event
from src.shared.infrastructure.mappers import map_event_payload_to_schema

users_eventer_listener = EventerListener(
    topic=project_settings.kafka.ACTIONS_ON_USERS_KAFKA_TOPIC,
    key="events",
    where={
        "source": {"service": "auth_service"},
        "destination": {"service": "registry_service"},
        "payload": {"model": "users"},
    },
    is_debug=True,
    logger=logger,
)


@users_eventer_listener.get(where={"action": EventerActionEnum.CREATE})
@inject
@handle_kafka_event("create", "users")
async def _handle_create_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: UserService = Provide[UsersContainer.user_service],
    logger: LoggerService = Provide[UsersContainer.logger],
):
    create_schema = map_event_payload_to_schema(schema_data, UserSchema)
    await service.create(create_schema)


@users_eventer_listener.get(where={"action": EventerActionEnum.UPDATE})
@inject
@handle_kafka_event("update", "users")
async def _handle_update_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: UserService = Provide[UsersContainer.user_service],
    logger: LoggerService = Provide[UsersContainer.logger],
):
    update_schema = map_event_payload_to_schema(schema_data, UserSchema)
    await service.update_user(update_schema)


@users_eventer_listener.get(where={"action": EventerActionEnum.DELETE})
@inject
@handle_kafka_event("delete", "users")
async def _handle_delete_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: UserService = Provide[UsersContainer.user_service],
    logger: LoggerService = Provide[UsersContainer.logger],
):
    delete_schema = map_event_payload_to_schema(schema_data, DeleteUserSchema)
    await service.delete_user(delete_schema.id)
