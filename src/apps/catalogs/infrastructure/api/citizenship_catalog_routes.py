from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.citizenship_catalog_request_schemas import (
    AddCitizenshipSchema,
    UpdateCitizenshipSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.citizenship_catalog_response_schemas import (
    CitizenshipCatalogFullResponseSchema,
    CitizenshipCatalogPartialResponseSchema,
    MultipleCitizenshipSchema,
)
from src.apps.catalogs.services.citizenship_catalog_service import (
    CitizenshipCatalogService,
)
from src.shared.schemas.pagination_schemas import PaginationParams

citizenship_catalog_router = APIRouter(
    prefix="/citizenship_catalog",
)


@citizenship_catalog_router.get(
    "/admin/{citizenship_id}", response_model=CitizenshipCatalogFullResponseSchema
)
@inject
async def get_by_id_for_admin(
    citizenship_id: int,
    service: CitizenshipCatalogService = Depends(
        Provide[CatalogsContainer.citizenship_catalog_service]
    ),
) -> CitizenshipCatalogFullResponseSchema:
    # fmt: off
    citizenship: CitizenshipCatalogFullResponseSchema = await service.get_by_id(  # type: ignore
        citizenship_id, include_all_locales=True
    )
    # fmt: on

    return citizenship


@citizenship_catalog_router.get(
    "/client/{citizenship_id}", response_model=CitizenshipCatalogPartialResponseSchema
)
@inject
async def get_by_id_for_client(
    citizenship_id: int,
    service: CitizenshipCatalogService = Depends(
        Provide[CatalogsContainer.citizenship_catalog_service]
    ),
) -> CitizenshipCatalogPartialResponseSchema:
    # fmt: off
    citizenship: CitizenshipCatalogPartialResponseSchema = await service.get_by_id(  # type: ignore
        citizenship_id, include_all_locales=False
    )
    # fmt: on
    return citizenship


@citizenship_catalog_router.get("/admin", response_model=MultipleCitizenshipSchema)
@inject
async def get_citizenship_records_for_admin(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    country_code: Optional[str] = Query(
        default=None, description="Filter by country code (ISO)"
    ),
    pagination_params: PaginationParams = Depends(),
    service: CitizenshipCatalogService = Depends(
        Provide[CatalogsContainer.citizenship_catalog_service]
    ),
) -> MultipleCitizenshipSchema:
    citizenship_records: MultipleCitizenshipSchema = (
        await service.get_citizenship_records(
            pagination_params=pagination_params,
            name_filter=name,
            country_code_filter=country_code,
            include_all_locales=True,
        )
    )

    return citizenship_records


@citizenship_catalog_router.get("/client", response_model=MultipleCitizenshipSchema)
@inject
async def get_citizenship_records_for_client(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    country_code: Optional[str] = Query(
        default=None, description="Filter by country code (ISO)"
    ),
    pagination_params: PaginationParams = Depends(),
    service: CitizenshipCatalogService = Depends(
        Provide[CatalogsContainer.citizenship_catalog_service]
    ),
) -> MultipleCitizenshipSchema:
    citizenship_records: MultipleCitizenshipSchema = (
        await service.get_citizenship_records(
            pagination_params=pagination_params,
            name_filter=name,
            country_code_filter=country_code,
            include_all_locales=False,
        )
    )

    return citizenship_records


@citizenship_catalog_router.post(
    "", response_model=CitizenshipCatalogFullResponseSchema, status_code=201
)
@inject
async def add_citizenship(
    request_dto: AddCitizenshipSchema,
    service: CitizenshipCatalogService = Depends(
        Provide[CatalogsContainer.citizenship_catalog_service]
    ),
) -> CitizenshipCatalogFullResponseSchema:
    return await service.add_citizenship(request_dto)


@citizenship_catalog_router.patch(
    "/{citizenship_id}", response_model=CitizenshipCatalogFullResponseSchema
)
@inject
async def update_citizenship(
    citizenship_id: int,
    request_dto: UpdateCitizenshipSchema,
    service: CitizenshipCatalogService = Depends(
        Provide[CatalogsContainer.citizenship_catalog_service]
    ),
) -> CitizenshipCatalogFullResponseSchema:
    # Update existing citizenship
    updated = await service.update_citizenship(citizenship_id, request_dto)

    return updated


@citizenship_catalog_router.delete("/{citizenship_id}", status_code=204)
@inject
async def delete_citizenship(
    citizenship_id: int,
    service: CitizenshipCatalogService = Depends(
        Provide[CatalogsContainer.citizenship_catalog_service]
    ),
) -> None:
    # Delete existing citizenship
    await service.delete_by_id(citizenship_id)
