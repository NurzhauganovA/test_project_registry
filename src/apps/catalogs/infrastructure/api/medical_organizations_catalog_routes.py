from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.filters.medical_organizations_catalog_filters import (
    MedicalOrganizationsCatalogFilterParams,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.medical_organizations_catalog_schemas import (
    AddMedicalOrganizationSchema,
    UpdateMedicalOrganizationSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.medical_organizations_catalog_schemas import (
    MedicalOrganizationCatalogFullResponseSchema,
    MedicalOrganizationCatalogPartialResponseSchema,
    MultipleMedicalOrganizationsSchema,
)
from src.apps.catalogs.services.medical_organizations_catalog_service import (
    MedicalOrganizationsCatalogService,
)
from src.shared.schemas.pagination_schemas import PaginationParams

medical_organizations_router = APIRouter(
    prefix="/medical_organizations_catalog",
)


@medical_organizations_router.get(
    "/client/{organization_id}",
    response_model=MedicalOrganizationCatalogPartialResponseSchema,
)
@inject
async def get_by_id_for_client(
    organization_id: int,
    service: MedicalOrganizationsCatalogService = Depends(
        Provide[CatalogsContainer.medical_organizations_catalog_service]
    ),
) -> MedicalOrganizationCatalogPartialResponseSchema:
    return await service.get_by_id(organization_id, include_all_locales=False)


@medical_organizations_router.get(
    "/admin/{organization_id}",
    response_model=MedicalOrganizationCatalogFullResponseSchema,
)
@inject
async def get_by_id_for_admin(
    organization_id: int,
    service: MedicalOrganizationsCatalogService = Depends(
        Provide[CatalogsContainer.medical_organizations_catalog_service]
    ),
) -> MedicalOrganizationCatalogFullResponseSchema:
    return await service.get_by_id(organization_id, include_all_locales=True)


@medical_organizations_router.get(
    "/admin", response_model=MultipleMedicalOrganizationsSchema
)
@inject
async def get_medical_organizations_for_admin(
    filter_params: MedicalOrganizationsCatalogFilterParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    service: MedicalOrganizationsCatalogService = Depends(
        Provide[CatalogsContainer.medical_organizations_catalog_service]
    ),
) -> MultipleMedicalOrganizationsSchema:
    return await service.get_medical_organizations(
        pagination_params=pagination_params,
        filter_params=filter_params,
        include_all_locales=True,
    )


@medical_organizations_router.get(
    "/client", response_model=MultipleMedicalOrganizationsSchema
)
@inject
async def get_medical_organizations_for_client(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    organization_code: Optional[str] = Query(
        default=None, description="Filter by internal code"
    ),
    address: Optional[str] = Query(default=None, description="Filter by address"),
    pagination_params: PaginationParams = Depends(),
    service: MedicalOrganizationsCatalogService = Depends(
        Provide[CatalogsContainer.medical_organizations_catalog_service]
    ),
) -> MultipleMedicalOrganizationsSchema:
    filters = MedicalOrganizationsCatalogFilterParams(
        name_filter=name,
        organization_code_filter=organization_code,
        address_filter=address,
    )
    return await service.get_medical_organizations(
        pagination_params=pagination_params,
        filter_params=filters,
        include_all_locales=False,
    )


@medical_organizations_router.post(
    "",
    response_model=MedicalOrganizationCatalogFullResponseSchema,
    status_code=201,
)
@inject
async def add_medical_organization(
    request_dto: AddMedicalOrganizationSchema,
    service: MedicalOrganizationsCatalogService = Depends(
        Provide[CatalogsContainer.medical_organizations_catalog_service]
    ),
) -> MedicalOrganizationCatalogFullResponseSchema:
    return await service.add_medical_organization(request_dto)


@medical_organizations_router.patch(
    "/{organization_id}",
    response_model=MedicalOrganizationCatalogFullResponseSchema,
)
@inject
async def update_medical_organization(
    organization_id: int,
    request_dto: UpdateMedicalOrganizationSchema,
    service: MedicalOrganizationsCatalogService = Depends(
        Provide[CatalogsContainer.medical_organizations_catalog_service]
    ),
) -> MedicalOrganizationCatalogFullResponseSchema:
    return await service.update_medical_organization(organization_id, request_dto)


@medical_organizations_router.delete("/{organization_id}", status_code=204)
@inject
async def delete_by_id(
    organization_id: int,
    service: MedicalOrganizationsCatalogService = Depends(
        Provide[CatalogsContainer.medical_organizations_catalog_service]
    ),
) -> None:
    await service.delete_by_id(organization_id)
