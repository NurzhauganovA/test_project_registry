from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.patient_context_attributes_catalog_request_schemas import (
    AddPatientContextAttributeSchema,
    UpdatePatientContextAttributeSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.patient_context_attributes_catalog_response_schemas import (
    MultiplePatientContextAttributesSchema,
    PatientContextAttributeCatalogFullResponseSchema,
    PatientContextAttributeCatalogPartialResponseSchema,
)
from src.apps.catalogs.services.patient_context_attribute_service import (
    PatientContextAttributeService,
)
from src.shared.schemas.pagination_schemas import PaginationParams

patient_context_attributes_router = APIRouter(
    prefix="/patient_context_attributes_catalog",
)


@patient_context_attributes_router.get(
    "/client/{context_attribute_id}",
    response_model=PatientContextAttributeCatalogPartialResponseSchema,
)
@inject
async def get_by_id_for_client(
    context_attribute_id: int,
    service: PatientContextAttributeService = Depends(
        Provide[CatalogsContainer.patient_context_attributes_service]
    ),
) -> PatientContextAttributeCatalogPartialResponseSchema:
    # fmt: off
    patient_context_attribute: PatientContextAttributeCatalogPartialResponseSchema = (
        await service.get_by_id(context_attribute_id, include_all_locales=False)  # type: ignore
    )
    # fmt: on

    return patient_context_attribute


@patient_context_attributes_router.get(
    "/admin/{context_attribute_id}",
    response_model=PatientContextAttributeCatalogFullResponseSchema,
)
@inject
async def get_by_id_for_admin(
    context_attribute_id: int,
    service: PatientContextAttributeService = Depends(
        Provide[CatalogsContainer.patient_context_attributes_service]
    ),
) -> PatientContextAttributeCatalogFullResponseSchema:
    # fmt: off
    patient_context_attribute: PatientContextAttributeCatalogFullResponseSchema = (
        await service.get_by_id(context_attribute_id, include_all_locales=True)  # type: ignore
    )
    # fmt: on

    return patient_context_attribute


@patient_context_attributes_router.get(
    "/admin", response_model=MultiplePatientContextAttributesSchema
)
@inject
async def get_patient_context_attributes_for_admin(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    pagination_params: PaginationParams = Depends(),
    service: PatientContextAttributeService = Depends(
        Provide[CatalogsContainer.patient_context_attributes_service]
    ),
) -> MultiplePatientContextAttributesSchema:
    patient_context_attributes: MultiplePatientContextAttributesSchema = (
        await service.get_patient_context_attributes(
            pagination_params=pagination_params,
            name_filter=name,
            include_all_locales=True,
        )
    )

    return patient_context_attributes


@patient_context_attributes_router.get(
    "/client", response_model=MultiplePatientContextAttributesSchema
)
@inject
async def get_patient_context_attributes_for_client(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    pagination_params: PaginationParams = Depends(),
    service: PatientContextAttributeService = Depends(
        Provide[CatalogsContainer.patient_context_attributes_service]
    ),
) -> MultiplePatientContextAttributesSchema:
    patient_context_attributes: MultiplePatientContextAttributesSchema = (
        await service.get_patient_context_attributes(
            pagination_params=pagination_params,
            name_filter=name,
            include_all_locales=False,
        )
    )

    return patient_context_attributes


@patient_context_attributes_router.post(
    "", response_model=PatientContextAttributeCatalogFullResponseSchema, status_code=201
)
@inject
async def add_patient_context_attribute(
    request_dto: AddPatientContextAttributeSchema,
    service: PatientContextAttributeService = Depends(
        Provide[CatalogsContainer.patient_context_attributes_service]
    ),
) -> PatientContextAttributeCatalogFullResponseSchema:
    return await service.add_patient_context_attribute(request_dto)


@patient_context_attributes_router.patch(
    "/{context_attribute_id}",
    response_model=PatientContextAttributeCatalogFullResponseSchema,
)
@inject
async def update_patient_context_attribute(
    context_attribute_id: int,
    request_dto: UpdatePatientContextAttributeSchema,
    service: PatientContextAttributeService = Depends(
        Provide[CatalogsContainer.patient_context_attributes_service]
    ),
) -> PatientContextAttributeCatalogFullResponseSchema:
    # Update existing patient context attribute
    updated = await service.update_patient_context_attribute(
        context_attribute_id, request_dto
    )

    return updated


@patient_context_attributes_router.delete("/{context_attribute_id}", status_code=204)
@inject
async def delete_by_id(
    context_attribute_id: int,
    service: PatientContextAttributeService = Depends(
        Provide[CatalogsContainer.patient_context_attributes_service]
    ),
) -> None:
    await service.delete_by_id(context_attribute_id)
