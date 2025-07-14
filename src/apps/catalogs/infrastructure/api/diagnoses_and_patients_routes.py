from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.catalogs.container import CatalogsContainer
from src.apps.catalogs.infrastructure.api.schemas.requests.diagnoses_catalog_request_schemas import (
    AddDiagnosedPatientDiagnosisRecordRequestSchema,
    UpdateDiagnosedPatientDiagnosisRecordRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.filters.diagnoses_and_patients_filters import (
    DiagnosesAndPatientsFilterParams,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import (
    DiagnosedPatientDiagnosisResponseSchema,
    MultipleDiagnosedPatientDiagnosisResponseSchema,
)
from src.apps.catalogs.services.patients_and_diagnoses_service import (
    DiagnosedPatientDiagnosisService,
)
from src.shared.dependencies.check_user_permissions import check_user_permissions
from src.shared.dependencies.resources_map import (
    AvailableResourcesEnum,
    AvailableScopesEnum,
)
from src.shared.schemas.pagination_schemas import PaginationParams

diagnosed_patient_diagnosis_router = APIRouter(
    prefix="/patients_and_diagnoses",
    tags=["Patient's Diagnoses Routes"],
)


@diagnosed_patient_diagnosis_router.get(
    "/{record_id}",
    response_model=DiagnosedPatientDiagnosisResponseSchema,
    summary="Get diagnosed patient diagnosis record by ID",
)
@inject
async def get_by_id(
    record_id: UUID,
    service: DiagnosedPatientDiagnosisService = Depends(
        Provide[CatalogsContainer.diagnosed_patient_diagnosis_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.PATIENTS_DIAGNOSES,
                    "scopes": [AvailableScopesEnum.READ],
                },
            ],
        )
    ),
) -> DiagnosedPatientDiagnosisResponseSchema:
    return await service.get_by_id(record_id)


@diagnosed_patient_diagnosis_router.get(
    "",
    response_model=MultipleDiagnosedPatientDiagnosisResponseSchema,
    summary="Get list of patient diagnosis records",
)
@inject
async def get_patient_and_diagnoses_records(
    filters: DiagnosesAndPatientsFilterParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    service: DiagnosedPatientDiagnosisService = Depends(
        Provide[CatalogsContainer.diagnosed_patient_diagnosis_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.PATIENTS_DIAGNOSES,
                    "scopes": [AvailableScopesEnum.READ],
                },
            ],
        )
    ),
) -> MultipleDiagnosedPatientDiagnosisResponseSchema:
    """
    Get a paginated list of diagnosis records for patients, with optional filters.
    """
    return await service.get_patient_and_diagnoses_records(
        filters=filters,
        pagination_params=pagination_params,
    )


@diagnosed_patient_diagnosis_router.post(
    "",
    response_model=DiagnosedPatientDiagnosisResponseSchema,
    status_code=201,
    summary="Add new diagnosis record for patient",
)
@inject
async def add_patient_diagnosis_record(
    request_dto: AddDiagnosedPatientDiagnosisRecordRequestSchema,
    service: DiagnosedPatientDiagnosisService = Depends(
        Provide[CatalogsContainer.diagnosed_patient_diagnosis_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.PATIENTS_DIAGNOSES,
                    "scopes": [AvailableScopesEnum.CREATE],
                },
            ],
        )
    ),
) -> DiagnosedPatientDiagnosisResponseSchema:
    return await service.add_patient_diagnosis_record(request_dto)


@diagnosed_patient_diagnosis_router.patch(
    "/{record_id}",
    response_model=DiagnosedPatientDiagnosisResponseSchema,
    summary="Update diagnosis record for patient by record ID",
)
@inject
async def update_patient_diagnosis_record(
    record_id: UUID,
    request_dto: UpdateDiagnosedPatientDiagnosisRecordRequestSchema,
    service: DiagnosedPatientDiagnosisService = Depends(
        Provide[CatalogsContainer.diagnosed_patient_diagnosis_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.PATIENTS_DIAGNOSES,
                    "scopes": [AvailableScopesEnum.UPDATE],
                },
            ],
        )
    ),
) -> DiagnosedPatientDiagnosisResponseSchema:
    return await service.update_patient_diagnosis_record(record_id, request_dto)


@diagnosed_patient_diagnosis_router.delete(
    "/{record_id}",
    status_code=204,
    summary="Delete diagnosis record for patient by record ID",
)
@inject
async def delete_by_id(
    record_id: UUID,
    service: DiagnosedPatientDiagnosisService = Depends(
        Provide[CatalogsContainer.diagnosed_patient_diagnosis_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.PATIENTS_DIAGNOSES,
                    "scopes": [AvailableScopesEnum.DELETE],
                },
            ],
        )
    ),
) -> None:
    await service.delete_by_id(record_id)
