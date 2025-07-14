from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.filters.insurance_info_catalog_filters import (
    InsuranceInfoCatalogFilterParams,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.insurance_info_catalog_request_schemas import (
    AddInsuranceInfoRecordSchema,
    UpdateInsuranceInfoRecordSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.insurance_info_catalog_response_schemas import (
    MultipleInsuranceInfoRecordsSchema,
    ResponseInsuranceInfoRecordSchema,
)
from src.apps.catalogs.services.insurance_info_catalog_service import (
    InsuranceInfoCatalogService,
)
from src.shared.schemas.pagination_schemas import PaginationParams

insurance_info_catalog_router = APIRouter(prefix="/insurance_info_catalog")


@insurance_info_catalog_router.get(
    "/{insurance_info_id}", response_model=ResponseInsuranceInfoRecordSchema
)
@inject
async def get_by_id(
    insurance_info_id: int,
    service: InsuranceInfoCatalogService = Depends(
        Provide[CatalogsContainer.insurance_info_catalog_service]
    ),
) -> ResponseInsuranceInfoRecordSchema:
    return await service.get_by_id(insurance_info_id)


@insurance_info_catalog_router.get(
    "", response_model=MultipleInsuranceInfoRecordsSchema
)
@inject
async def get_insurance_info_records(
    filter_params: InsuranceInfoCatalogFilterParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    service: InsuranceInfoCatalogService = Depends(
        Provide[CatalogsContainer.insurance_info_catalog_service]
    ),
) -> MultipleInsuranceInfoRecordsSchema:
    filters = InsuranceInfoCatalogFilterParams(
        patient_id_filter=filter_params.patient_id,
        financing_source_id_filter=filter_params.financing_source_id,
        policy_number_filter=filter_params.policy_number,
        company_name_filter=filter_params.company,
        valid_from_filter=filter_params.valid_from,
        valid_till_filter=filter_params.valid_till,
    )

    return await service.get_insurance_info_records(pagination_params, filters)


@insurance_info_catalog_router.post(
    "", response_model=ResponseInsuranceInfoRecordSchema, status_code=201
)
@inject
async def add_insurance_info_record(
    request_dto: AddInsuranceInfoRecordSchema,
    service: InsuranceInfoCatalogService = Depends(
        Provide[CatalogsContainer.insurance_info_catalog_service]
    ),
) -> ResponseInsuranceInfoRecordSchema:
    return await service.add_insurance_info_record(request_dto)


@insurance_info_catalog_router.patch(
    "/{insurance_info_id}", response_model=ResponseInsuranceInfoRecordSchema
)
@inject
async def update_insurance_info_record(
    insurance_info_id: int,
    request_dto: UpdateInsuranceInfoRecordSchema,
    service: InsuranceInfoCatalogService = Depends(
        Provide[CatalogsContainer.insurance_info_catalog_service]
    ),
) -> ResponseInsuranceInfoRecordSchema:
    return await service.update_insurance_info_record(insurance_info_id, request_dto)


@insurance_info_catalog_router.delete("/{insurance_info_id}", status_code=204)
@inject
async def delete_by_id(
    insurance_info_id: int,
    service: InsuranceInfoCatalogService = Depends(
        Provide[CatalogsContainer.insurance_info_catalog_service]
    ),
) -> None:
    await service.delete_by_id(insurance_info_id)
