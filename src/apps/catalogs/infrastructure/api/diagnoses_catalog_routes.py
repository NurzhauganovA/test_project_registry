from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.diagnoses_catalog_request_schemas import (
    AddDiagnosisRequestSchema,
    UpdateDiagnosisRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import (
    DiagnosesCatalogResponseSchema,
    MultipleDiagnosesCatalogResponseSchema,
)
from src.apps.catalogs.services.diagnoses_catalogue_service import (
    DiagnosesCatalogService,
)
from src.shared.dependencies.check_user_permissions import check_user_permissions
from src.shared.dependencies.resources_map import (
    AvailableResourcesEnum,
    AvailableScopesEnum,
)
from src.shared.schemas.pagination_schemas import PaginationParams

diagnoses_catalog_router = APIRouter(
    prefix="/diagnoses_catalog",
    tags=["Diagnoses Catalog Routes"],
)


@diagnoses_catalog_router.get(
    "/{diagnosis_id}",
    response_model=DiagnosesCatalogResponseSchema,
    summary="Get diagnosis by ID",
)
@inject
async def get_by_id(
    diagnosis_id: int,
    service: DiagnosesCatalogService = Depends(
        Provide[CatalogsContainer.diagnoses_catalog_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.DIAGNOSES_CATALOG,
                    "scopes": [AvailableScopesEnum.READ],
                },
            ],
        )
    ),
) -> DiagnosesCatalogResponseSchema:
    return await service.get_by_id(diagnosis_id)


@diagnoses_catalog_router.get(
    "",
    response_model=MultipleDiagnosesCatalogResponseSchema,
    summary="Get diagnoses list",
)
@inject
async def get_diagnoses(
    diagnosis_code_filter: Optional[str] = Query(
        default=None,
        description="Filter by diagnosis code (case-insensitive, exact match)",
        examples=["МКБ-10", "AC-09"],
    ),
    pagination_params: PaginationParams = Depends(),
    service: DiagnosesCatalogService = Depends(
        Provide[CatalogsContainer.diagnoses_catalog_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.DIAGNOSES_CATALOG,
                    "scopes": [AvailableScopesEnum.READ],
                },
            ],
        )
    ),
) -> MultipleDiagnosesCatalogResponseSchema:
    return await service.get_diagnoses(
        pagination_params=pagination_params,
        diagnosis_code_filter=diagnosis_code_filter,
    )


@diagnoses_catalog_router.post(
    "",
    response_model=DiagnosesCatalogResponseSchema,
    status_code=201,
    summary="Add new diagnosis",
)
@inject
async def add_diagnosis(
    request_dto: AddDiagnosisRequestSchema,
    service: DiagnosesCatalogService = Depends(
        Provide[CatalogsContainer.diagnoses_catalog_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.DIAGNOSES_CATALOG,
                    "scopes": [AvailableScopesEnum.CREATE],
                },
            ],
        )
    ),
) -> DiagnosesCatalogResponseSchema:
    return await service.add_diagnosis(request_dto)


@diagnoses_catalog_router.patch(
    "/{diagnosis_id}",
    response_model=DiagnosesCatalogResponseSchema,
    summary="Update diagnosis by ID",
)
@inject
async def update_diagnosis(
    diagnosis_id: int,
    request_dto: UpdateDiagnosisRequestSchema,
    service: DiagnosesCatalogService = Depends(
        Provide[CatalogsContainer.diagnoses_catalog_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.DIAGNOSES_CATALOG,
                    "scopes": [AvailableScopesEnum.UPDATE],
                },
            ],
        )
    ),
) -> DiagnosesCatalogResponseSchema:
    return await service.update_diagnosis(diagnosis_id, request_dto)


@diagnoses_catalog_router.delete(
    "/{diagnosis_id}",
    status_code=204,
    summary="Delete diagnosis by ID",
)
@inject
async def delete_by_id(
    diagnosis_id: int,
    service: DiagnosesCatalogService = Depends(
        Provide[CatalogsContainer.diagnoses_catalog_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.DIAGNOSES_CATALOG,
                    "scopes": [AvailableScopesEnum.DELETE],
                },
            ],
        )
    ),
) -> None:
    await service.delete_by_id(diagnosis_id)
