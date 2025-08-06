from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.nationalities_catalog_request_schemas import (
    AddNationalitySchema,
    UpdateNationalitySchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.nationalities_catalog_response_schemas import (
    MultipleNationalitiesCatalogSchema,
    NationalityCatalogFullResponseSchema,
    NationalityCatalogPartialResponseSchema,
)
from src.apps.catalogs.services.nationalities_catalog_service import (
    NationalitiesCatalogService,
)
from src.shared.schemas.pagination_schemas import PaginationParams

nationalities_catalog_router = APIRouter(
    prefix="/nationalities_catalog",
)


@nationalities_catalog_router.get(
    "/client/{nationality_id}",
    response_model=NationalityCatalogPartialResponseSchema,
)
@inject
async def get_by_id_for_client(
    nationality_id: int,
    service: NationalitiesCatalogService = Depends(
        Provide[CatalogsContainer.nationalities_catalog_service]
    ),
) -> NationalityCatalogPartialResponseSchema:
    # fmt: off
    nationality: NationalityCatalogPartialResponseSchema = await service.get_by_id(
        nationality_id, include_all_locales=False  # type: ignore
    )
    # fmt: on

    return nationality


@nationalities_catalog_router.get(
    "/admin/{nationality_id}",
    response_model=NationalityCatalogFullResponseSchema,
)
@inject
async def get_by_id_for_admin(
    nationality_id: int,
    service: NationalitiesCatalogService = Depends(
        Provide[CatalogsContainer.nationalities_catalog_service]
    ),
) -> NationalityCatalogFullResponseSchema:
    # fmt: off
    nationality: NationalityCatalogFullResponseSchema = await service.get_by_id(
        nationality_id, include_all_locales=True  # type: ignore
    )
    # fmt: off

    return nationality


@nationalities_catalog_router.get(
    "/admin", response_model=MultipleNationalitiesCatalogSchema
)
@inject
async def get_nationalities_for_admin(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    pagination_params: PaginationParams = Depends(),
    service: NationalitiesCatalogService = Depends(
        Provide[CatalogsContainer.nationalities_catalog_service]
    ),
) -> MultipleNationalitiesCatalogSchema:
    nationalities: MultipleNationalitiesCatalogSchema = await service.get_nationalities(
        pagination_params=pagination_params,
        name_filter=name,
        include_all_locales=True,
    )

    return nationalities


@nationalities_catalog_router.get(
    "/client", response_model=MultipleNationalitiesCatalogSchema
)
@inject
async def get_nationalities_for_client(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    pagination_params: PaginationParams = Depends(),
    service: NationalitiesCatalogService = Depends(
        Provide[CatalogsContainer.nationalities_catalog_service]
    ),
) -> MultipleNationalitiesCatalogSchema:
    nationalities: MultipleNationalitiesCatalogSchema = await service.get_nationalities(
        pagination_params=pagination_params,
        name_filter=name,
        include_all_locales=False,
    )

    return nationalities


@nationalities_catalog_router.post(
    "", response_model=NationalityCatalogFullResponseSchema, status_code=201
)
@inject
async def add_nationality(
    request_dto: AddNationalitySchema,
    service: NationalitiesCatalogService = Depends(
        Provide[CatalogsContainer.nationalities_catalog_service]
    ),
) -> NationalityCatalogFullResponseSchema:
    return await service.add_nationality(request_dto)


@nationalities_catalog_router.patch(
    "/{nationality_id}",
    response_model=NationalityCatalogFullResponseSchema,
)
@inject
async def update_nationality(
    nationality_id: int,
    request_dto: UpdateNationalitySchema,
    service: NationalitiesCatalogService = Depends(
        Provide[CatalogsContainer.nationalities_catalog_service]
    ),
) -> NationalityCatalogFullResponseSchema:
    # Update existing patient context attribute
    updated = await service.update_nationality(nationality_id, request_dto)

    return updated


@nationalities_catalog_router.delete("/{nationality_id}", status_code=204)
@inject
async def delete_by_id(
    nationality_id: int,
    service: NationalitiesCatalogService = Depends(
        Provide[CatalogsContainer.nationalities_catalog_service]
    ),
) -> None:
    await service.delete_by_id(nationality_id)
