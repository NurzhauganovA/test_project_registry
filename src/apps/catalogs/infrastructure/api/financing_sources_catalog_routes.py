from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.financing_sources_catalog_request_schemas import (
    AddFinancingSourceSchema,
    UpdateFinancingSourceSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.financing_sources_catalog_response_schemas import (
    FinancingSourceFullResponseSchema,
    FinancingSourcePartialResponseSchema,
    MultipleFinancingSourcesSchema,
)
from src.apps.catalogs.services.financing_sources_catalog_service import (
    FinancingSourceCatalogService,
)
from src.shared.schemas.pagination_schemas import PaginationParams

financing_sources_catalog_router = APIRouter(
    prefix="/financing_sources_catalog",
)


@financing_sources_catalog_router.get(
    "/client/{financing_source_id}",
    response_model=FinancingSourcePartialResponseSchema,
)
@inject
async def get_by_id_for_client(
    financing_source_id: int,
    service: FinancingSourceCatalogService = Depends(
        Provide[CatalogsContainer.financing_sources_catalog_service]
    ),
) -> FinancingSourcePartialResponseSchema:
    financing_source: FinancingSourcePartialResponseSchema = await service.get_by_id(
        financing_source_id, include_all_locales=False
    )
    return financing_source


@financing_sources_catalog_router.get(
    "/admin/{financing_source_id}",
    response_model=FinancingSourceFullResponseSchema,
)
@inject
async def get_by_id_for_admin(
    financing_source_id: int,
    service: FinancingSourceCatalogService = Depends(
        Provide[CatalogsContainer.financing_sources_catalog_service]
    ),
) -> FinancingSourceFullResponseSchema:
    financing_source: FinancingSourceFullResponseSchema = await service.get_by_id(
        financing_source_id, include_all_locales=True
    )
    return financing_source


@financing_sources_catalog_router.get(
    "/admin", response_model=MultipleFinancingSourcesSchema
)
@inject
async def get_financing_sources_for_admin(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    code: Optional[str] = Query(default=None, description="Filter by code"),
    pagination_params: PaginationParams = Depends(),
    service: FinancingSourceCatalogService = Depends(
        Provide[CatalogsContainer.financing_sources_catalog_service]
    ),
) -> MultipleFinancingSourcesSchema:
    financing_sources: MultipleFinancingSourcesSchema = (
        await service.get_financing_sources(
            pagination_params=pagination_params,
            name_filter=name,
            code_filter=code,
            include_all_locales=True,
        )
    )
    return financing_sources


@financing_sources_catalog_router.get(
    "/client", response_model=MultipleFinancingSourcesSchema
)
@inject
async def get_financing_sources_for_client(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    code: Optional[str] = Query(default=None, description="Filter by code"),
    pagination_params: PaginationParams = Depends(),
    service: FinancingSourceCatalogService = Depends(
        Provide[CatalogsContainer.financing_sources_catalog_service]
    ),
) -> MultipleFinancingSourcesSchema:
    financing_sources: MultipleFinancingSourcesSchema = (
        await service.get_financing_sources(
            pagination_params=pagination_params,
            name_filter=name,
            code_filter=code,
            include_all_locales=False,
        )
    )
    return financing_sources


@financing_sources_catalog_router.post(
    "", response_model=FinancingSourceFullResponseSchema, status_code=201
)
@inject
async def add_financing_source(
    request_dto: AddFinancingSourceSchema,
    service: FinancingSourceCatalogService = Depends(
        Provide[CatalogsContainer.financing_sources_catalog_service]
    ),
) -> FinancingSourceFullResponseSchema:
    return await service.add_financing_source(request_dto)


@financing_sources_catalog_router.patch(
    "/{financing_source_id}",
    response_model=FinancingSourceFullResponseSchema,
)
@inject
async def update_financing_source(
    financing_source_id: int,
    request_dto: UpdateFinancingSourceSchema,
    service: FinancingSourceCatalogService = Depends(
        Provide[CatalogsContainer.financing_sources_catalog_service]
    ),
) -> FinancingSourceFullResponseSchema:
    updated = await service.update_financing_source(financing_source_id, request_dto)
    return updated


@financing_sources_catalog_router.delete("/{financing_source_id}", status_code=204)
@inject
async def delete_by_id(
    financing_source_id: int,
    service: FinancingSourceCatalogService = Depends(
        Provide[CatalogsContainer.financing_sources_catalog_service]
    ),
) -> None:
    await service.delete_by_id(financing_source_id)
