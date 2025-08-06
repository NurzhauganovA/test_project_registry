from dependency_injector.wiring import Provide, inject
from mis_eventer_lib.eventer_consumer import EventerListener
from mis_eventer_lib.schemas.event_schema import (
    EventerActionEnum,
    EventerResponseSchema,
)

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.identity_documents_catalog_request_schemas import (
    AddIdentityDocumentRequestSchema,
    DeleteIdentityDocumentSchema,
    UpdateIdentityDocumentRequestSchema,
)
from src.apps.catalogs.services.identity_documents_catalog_service import IdentityDocumentsCatalogService
from src.core.logger import LoggerService
from src.core.settings import project_settings
from src.shared.helpers.decorators import handle_kafka_event
from src.shared.infrastructure.mappers import map_event_payload_to_schema

identity_documents_catalog_event_handler = EventerListener(
    topic=project_settings.kafka.ACTIONS_ON_CATALOGS_KAFKA_TOPIC,
    key="events",
    where={
        "source": {"service": "admin_service"},
        "destination": {"service": "registry_service"},
        "payload": {"model": "cat_identity_documents"},
    },
)


@identity_documents_catalog_event_handler.get(where={"action": EventerActionEnum.CREATE})
@inject
@handle_kafka_event("create", "cat_identity_documents")
async def _handle_create_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: IdentityDocumentsCatalogService = Provide[CatalogsContainer.identity_documents_catalog_service],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    create_schema = map_event_payload_to_schema(schema_data, AddIdentityDocumentRequestSchema)
    await service.add_identity_document(create_schema)


@identity_documents_catalog_event_handler.get(where={"action": EventerActionEnum.UPDATE})
@inject
@handle_kafka_event("update", "cat_identity_documents")
async def _handle_update_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: IdentityDocumentsCatalogService = Provide[CatalogsContainer.identity_documents_catalog_service],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    update_schema = map_event_payload_to_schema(schema_data, UpdateIdentityDocumentRequestSchema)
    await service.update_identity_document(update_schema.id, update_schema)


@identity_documents_catalog_event_handler.get(where={"action": EventerActionEnum.DELETE})
@inject
@handle_kafka_event("delete", "cat_identity_documents")
async def _handle_delete_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: IdentityDocumentsCatalogService = Provide[CatalogsContainer.identity_documents_catalog_service],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    delete_schema = map_event_payload_to_schema(schema_data, DeleteIdentityDocumentSchema)
    await service.delete_by_id(delete_schema.id)
