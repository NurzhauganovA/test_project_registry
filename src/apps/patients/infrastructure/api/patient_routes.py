import math
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.patients.container import PatientsContainer
from src.apps.patients.domain.patient import PatientDomain
from src.apps.patients.infrastructure.api.schemas.requests.patient_request_schemas import (
    CreatePatientSchema,
    UpdatePatientSchema,
)
from src.apps.patients.infrastructure.api.schemas.requests.patients_filter_params import (
    PatientsFilterParams,
)
from src.apps.patients.infrastructure.api.schemas.responses.patient_response_schemas import (
    MultiplePatientsResponseSchema,
    ResponsePatientSchema,
)
from src.apps.patients.mappers import (
    map_create_schema_to_domain,
    map_patient_domain_to_response_schema,
)
from src.apps.patients.services.patients_service import PatientService
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)

patients_router = APIRouter(prefix="/patients")


@patients_router.get("/{patient_id}", response_model=ResponsePatientSchema)
@inject
async def get_by_id(
    patient_id: UUID,
    service: PatientService = Depends(Provide[PatientsContainer.patients_service]),
) -> ResponsePatientSchema:
    patient: PatientDomain = await service.get_by_id(patient_id)
    return map_patient_domain_to_response_schema(patient)


@patients_router.get("", response_model=MultiplePatientsResponseSchema)
@inject
async def get_patients(
    filter_params: PatientsFilterParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    service: PatientService = Depends(Provide[PatientsContainer.patients_service]),
) -> MultiplePatientsResponseSchema:
    patients, total_number_of_items = await service.get_patients(
        filter_params, pagination_params
    )

    # Calculate pagination metadata
    page: int = pagination_params.page or 1  # for mypy
    limit: int = pagination_params.limit or 30  # for mypy
    total_pages = math.ceil(total_number_of_items / limit) if limit else 1
    has_next = page < total_pages
    has_prev = page > 1

    pagination_metadata = PaginationMetaDataSchema(
        current_page=page,
        per_page=limit,
        total_items=total_number_of_items,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    response_schema = MultiplePatientsResponseSchema(
        items=[map_patient_domain_to_response_schema(patient) for patient in patients],
        pagination=pagination_metadata,
    )

    return response_schema


@patients_router.post(
    "",
    response_model=ResponsePatientSchema,
    status_code=201,
)
@inject
async def create_patient(
    schema: CreatePatientSchema,
    service: PatientService = Depends(Provide[PatientsContainer.patients_service]),
) -> ResponsePatientSchema:
    patient_domain: PatientDomain = map_create_schema_to_domain(schema)
    created: PatientDomain = await service.create_patient(patient_domain)
    return map_patient_domain_to_response_schema(created)


@patients_router.patch("/{patient_id}", response_model=ResponsePatientSchema)
@inject
async def update_patient(
    patient_id: UUID,
    schema: UpdatePatientSchema,
    service: PatientService = Depends(Provide[PatientsContainer.patients_service]),
) -> ResponsePatientSchema:
    updated: PatientDomain = await service.update_patient(patient_id, schema)
    return map_patient_domain_to_response_schema(updated)


@patients_router.delete("/{patient_id}", status_code=204)
@inject
async def delete_by_id(
    patient_id: UUID,
    service: PatientService = Depends(Provide[PatientsContainer.patients_service]),
) -> None:
    await service.delete_patient(patient_id)
