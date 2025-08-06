from dependency_injector.wiring import Provide, inject
from mis_eventer_lib.eventer_consumer import EventerListener
from mis_eventer_lib.schemas.event_schema import (
    EventerActionEnum,
    EventerResponseSchema,
)

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.medical_organizations_catalog_schemas import (
    AddMedicalOrganizationSchema,
    DeleteMedicalOrganizationSchema,
    UpdateMedicalOrganizationSchema,
)
from src.apps.catalogs.services.medical_organizations_catalog_service import MedicalOrganizationsCatalogService
from src.core.logger import LoggerService
from src.core.settings import project_settings
from src.shared.helpers.decorators import handle_kafka_event
from src.shared.infrastructure.mappers import map_event_payload_to_schema

medical_organizations_catalog_event_handler = EventerListener(
    topic=project_settings.kafka.ACTIONS_ON_CATALOGS_KAFKA_TOPIC,
    key="events",
    where={
        "source": {"service": "admin_service"},
        "destination": {"service": "registry_service"},
        "payload": {"model": "cat_medical_organizations"},
    },
)


@medical_organizations_catalog_event_handler.get(where={"action": EventerActionEnum.CREATE})
@inject
@handle_kafka_event("create", "cat_medical_organizations")
async def _handle_create_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: MedicalOrganizationsCatalogService = Provide[CatalogsContainer.medical_organizations_catalog_service],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    create_schema = map_event_payload_to_schema(schema_data, AddMedicalOrganizationSchema)
    await service.add_medical_organization(create_schema)


@medical_organizations_catalog_event_handler.get(where={"action": EventerActionEnum.UPDATE})
@inject
@handle_kafka_event("update", "cat_medical_organizations")
async def _handle_update_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: MedicalOrganizationsCatalogService = Provide[CatalogsContainer.medical_organizations_catalog_service],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    update_schema = map_event_payload_to_schema(schema_data, UpdateMedicalOrganizationSchema)
    await service.update_medical_organization(update_schema.id, update_schema)


@medical_organizations_catalog_event_handler.get(where={"action": EventerActionEnum.DELETE})
@inject
@handle_kafka_event("delete", "cat_medical_organizations")
async def _handle_delete_event(
    _raw_message: bytes,
    schema_data: EventerResponseSchema,
    service: MedicalOrganizationsCatalogService = Provide[CatalogsContainer.medical_organizations_catalog_service],
    logger: LoggerService = Provide[CatalogsContainer.logger],
):
    delete_schema = map_event_payload_to_schema(schema_data, DeleteMedicalOrganizationSchema)
    await service.delete_by_id(delete_schema.id)

