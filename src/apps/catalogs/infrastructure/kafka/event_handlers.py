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
from src.shared.infrastructure.mappers import map_event_payload_to_schema

eventer_listener = EventerListener(
    topic=project_settings.kafka.ACTIONS_ON_CATALOGS_KAFKA_TOPIC,
    key="events",
    where={
        "source": {"service": "admin_service"},
        "destination": {"service": "registry_service"},
        "payload": {"model": "cat_nationalities"},
    },
)


@eventer_listener.get(where={"action": EventerActionEnum.CREATE})
@inject
async def _handle_create_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: NationalitiesCatalogService = Provide[
        CatalogsContainer.nationalities_catalog_service
    ],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    try:
        create_schema = map_event_payload_to_schema(schema_data, AddNationalitySchema)
        await service.add_nationality(create_schema)
        logger.debug(
            f"Successfully handled '{schema_data.action}' type event for model: 'cat_nationalities'. "
            f"New record with ID: {create_schema.id} has been CREATED."
        )
    except Exception as err:
        logger.critical(
            f"Failed to handle '{schema_data.action}' type event for model: 'cat_nationalities'. {err}",
            exc_info=True,
        )
        return


@eventer_listener.get(where={"action": EventerActionEnum.UPDATE})
@inject
async def _handle_update_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: NationalitiesCatalogService = Provide[
        CatalogsContainer.nationalities_catalog_service
    ],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    try:
        update_schema = map_event_payload_to_schema(
            schema_data, UpdateNationalitySchema
        )
        await service.update_nationality(update_schema.id, update_schema)
        logger.debug(
            f"Successfully handled '{schema_data.action}' type event for model: 'cat_nationalities'. "
            f"Record with ID: {update_schema.id} has been UPDATED."
        )
    except Exception as err:
        logger.critical(
            f"Failed to handle '{schema_data.action}' type event for model: 'cat_nationalities'. {err}",
            exc_info=True,
        )
        return


@eventer_listener.get(where={"action": EventerActionEnum.DELETE})
@inject
async def _handle_delete_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: NationalitiesCatalogService = Provide[
        CatalogsContainer.nationalities_catalog_service
    ],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    try:
        delete_schema = map_event_payload_to_schema(
            schema_data, DeleteNationalitySchema
        )
        await service.delete_by_id(delete_schema.id)
        logger.debug(
            f"Successfully handled '{schema_data.action}' type event for model: 'cat_nationalities'. "
            f"Record with ID: {delete_schema.id} has been DELETED."
        )
    except Exception as err:
        logger.critical(
            f"Failed to handle '{schema_data.action}' type event for model: 'cat_nationalities'. {err}",
            exc_info=True,
        )
        return
