from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.filters.identity_documents_catalog_filters import (
    IdentityDocumentsCatalogFilterParams,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.identity_documents_catalog_request_schemas import (
    AddIdentityDocumentRequestSchema,
    UpdateIdentityDocumentRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.identity_documents_catalog_response_schemas import (
    IdentityDocumentResponseSchema,
    MultipleIdentityDocumentsCatalogResponseSchema,
)
from src.apps.catalogs.services.identity_documents_catalog_service import (
    IdentityDocumentsCatalogService,
)
from src.shared.dependencies.check_user_permissions import check_user_permissions
from src.shared.dependencies.resources_map import (
    AvailableResourcesEnum,
    AvailableScopesEnum,
)
from src.shared.schemas.pagination_schemas import PaginationParams

identity_documents_router = APIRouter(
    prefix="/identity_documents",
    tags=["Identity Documents"],
)


@identity_documents_router.get(
    "/{document_id}",
    response_model=IdentityDocumentResponseSchema,
    summary="Get identity document by ID",
)
@inject
async def get_by_id(
    document_id: int,
    service: IdentityDocumentsCatalogService = Depends(
        Provide[CatalogsContainer.identity_documents_catalog_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.IDENTITY_DOCUMENTS_CATALOG,
                    "scopes": [AvailableScopesEnum.READ],
                }
            ]
        )
    ),
) -> IdentityDocumentResponseSchema:
    return await service.get_by_id(document_id)


@identity_documents_router.get(
    "",
    response_model=MultipleIdentityDocumentsCatalogResponseSchema,
    summary="Get list of identity documents with filters and pagination",
)
@inject
async def get_identity_documents(
    filters: IdentityDocumentsCatalogFilterParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    service: IdentityDocumentsCatalogService = Depends(
        Provide[CatalogsContainer.identity_documents_catalog_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.IDENTITY_DOCUMENTS_CATALOG,
                    "scopes": [AvailableScopesEnum.READ],
                }
            ]
        )
    ),
) -> MultipleIdentityDocumentsCatalogResponseSchema:
    return await service.get_identity_documents(pagination_params, filters)


@identity_documents_router.post(
    "",
    response_model=IdentityDocumentResponseSchema,
    status_code=201,
    summary="Add a new identity document",
)
@inject
async def add_identity_document(
    request_dto: AddIdentityDocumentRequestSchema,
    service: IdentityDocumentsCatalogService = Depends(
        Provide[CatalogsContainer.identity_documents_catalog_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.IDENTITY_DOCUMENTS_CATALOG,
                    "scopes": [AvailableScopesEnum.CREATE],
                }
            ]
        )
    ),
) -> IdentityDocumentResponseSchema:
    return await service.add_identity_document(request_dto)


@identity_documents_router.patch(
    "/{document_id}",
    response_model=IdentityDocumentResponseSchema,
    summary="Update identity document by ID",
)
@inject
async def update_identity_document(
    document_id: int,
    request_dto: UpdateIdentityDocumentRequestSchema,
    service: IdentityDocumentsCatalogService = Depends(
        Provide[CatalogsContainer.identity_documents_catalog_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.IDENTITY_DOCUMENTS_CATALOG,
                    "scopes": [AvailableScopesEnum.UPDATE],
                }
            ]
        )
    ),
) -> IdentityDocumentResponseSchema:
    return await service.update_identity_document(document_id, request_dto)


@identity_documents_router.delete(
    "/{document_id}",
    status_code=204,
    summary="Delete identity document by ID",
)
@inject
async def delete_by_id(
    document_id: int,
    service: IdentityDocumentsCatalogService = Depends(
        Provide[CatalogsContainer.identity_documents_catalog_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.IDENTITY_DOCUMENTS_CATALOG,
                    "scopes": [AvailableScopesEnum.DELETE],
                }
            ]
        )
    ),
) -> None:
    await service.delete_by_id(document_id)
