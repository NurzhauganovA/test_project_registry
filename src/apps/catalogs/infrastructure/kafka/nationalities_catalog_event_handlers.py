from dependency_injector.wiring import Provide, inject
from mis_eventer_lib.eventer_consumer import EventerListener
from mis_eventer_lib.schemas.event_schema import (
    EventerActionEnum,
    EventerResponseSchema,
)

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.nationalities_catalog_request_schemas import (
    AddNationalitySchema,
    DeleteNationalitySchema,
    UpdateNationalitySchema,
)
from src.apps.catalogs.services.nationalities_catalog_service import (
    NationalitiesCatalogService,
)
from src.core.logger import LoggerService
from src.core.settings import project_settings
from src.shared.helpers.decorators import handle_kafka_event
from src.shared.infrastructure.mappers import map_event_payload_to_schema

nationalities_catalog_eventer_listener = EventerListener(
    topic=project_settings.kafka.ACTIONS_ON_CATALOGS_KAFKA_TOPIC,
    key="events",
    where={
        "source": {"service": "admin_service"},
        "destination": {"service": "registry_service"},
        "payload": {"model": "cat_nationalities"},
    },
)


@nationalities_catalog_eventer_listener.get(where={"action": EventerActionEnum.CREATE})
@inject
@handle_kafka_event("create", "cat_nationalities")
async def _handle_create_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: NationalitiesCatalogService = Provide[CatalogsContainer.nationalities_catalog_service],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    create_schema = map_event_payload_to_schema(schema_data, AddNationalitySchema)
    await service.add_nationality(create_schema)


@nationalities_catalog_eventer_listener.get(where={"action": EventerActionEnum.UPDATE})
@inject
@handle_kafka_event("update", "cat_nationalities")
async def _handle_update_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: NationalitiesCatalogService = Provide[CatalogsContainer.nationalities_catalog_service],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    update_schema = map_event_payload_to_schema(schema_data, UpdateNationalitySchema)
    await service.update_nationality(update_schema.id, update_schema)


@nationalities_catalog_eventer_listener.get(where={"action": EventerActionEnum.DELETE})
@inject
@handle_kafka_event("delete", "cat_nationalities")
async def _handle_delete_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: NationalitiesCatalogService = Provide[CatalogsContainer.nationalities_catalog_service],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    delete_schema = map_event_payload_to_schema(schema_data, DeleteNationalitySchema)
    await service.delete_by_id(delete_schema.id)
