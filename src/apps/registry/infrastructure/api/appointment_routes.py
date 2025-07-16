import math
from typing import Annotated, List
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.patients.infrastructure.api.schemas.responses.patient_response_schemas import (
    ResponsePatientSchema,
)
from src.apps.patients.mappers import map_patient_domain_to_response_schema
from src.apps.registry.container import RegistryContainer
from src.apps.registry.infrastructure.api.schemas.requests.appointment_schemas import (
    CreateAppointmentSchema,
    UpdateAppointmentSchema,
)
from src.apps.registry.infrastructure.api.schemas.requests.filters.appointment_filter_params import (
    AppointmentFilterParams,
)
from src.apps.registry.infrastructure.api.schemas.responses.appointment_schemas import (
    MultipleAppointmentsResponseSchema,
    ResponseAppointmentSchema,
)
from src.apps.registry.mappers import map_appointment_domain_to_response_schema
from src.apps.registry.services.appointment_service import AppointmentService
from src.apps.users.infrastructure.schemas.user_schemas import UserSchema
from src.apps.users.mappers import map_user_domain_to_schema
from src.shared.dependencies.check_user_permissions import check_user_permissions
from src.shared.dependencies.resources_map import (
    AvailableResourcesEnum,
    AvailableScopesEnum,
)
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)

appointments_router = APIRouter()


@appointments_router.get(
    "/appointments/{appointment_id}",
    response_model=ResponseAppointmentSchema,
)
@inject
async def get_by_id(
    appointment_id: int,
    appointment_service: AppointmentService = Depends(
        Provide[RegistryContainer.appointment_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.APPOINTMENTS,
                    "scopes": [AvailableScopesEnum.READ],
                },
            ],
        )
    ),
) -> ResponseAppointmentSchema:
    appointment, patient, doctor, end_time, appointment_date = (
        await appointment_service.get_by_id(appointment_id=appointment_id)
    )
    patient_response_schema = (
        map_patient_domain_to_response_schema(patient) if patient else None
    )
    doctor_response_schema = map_user_domain_to_schema(doctor)
    appointment_date = appointment_date

    response_schema = map_appointment_domain_to_response_schema(
        appointment=appointment,
        appointment_end_time=end_time,
        appointment_date=appointment_date,
        patient_schema=patient_response_schema,
        doctor_schema=doctor_response_schema,
    )

    return response_schema


@appointments_router.get(
    "/appointments",
    response_model=MultipleAppointmentsResponseSchema,
)
@inject
async def get_appointments(
    filter_params: Annotated[AppointmentFilterParams, Depends()],
    appointment_service: AppointmentService = Depends(
        Provide[RegistryContainer.appointment_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.APPOINTMENTS,
                    "scopes": [AvailableScopesEnum.READ],
                },
            ],
        )
    ),
    pagination_params: PaginationParams = Depends(),
) -> MultipleAppointmentsResponseSchema:
    results, total_appointments_amount = await appointment_service.get_appointments(
        filter_params=filter_params,
        pagination_params=pagination_params,
    )

    # Calculate pagination metadata
    page: int = pagination_params.page or 1  # for mypy
    limit: int = pagination_params.limit or 30  # for mypy
    total_pages = math.ceil(total_appointments_amount / limit) if limit else 1
    has_next = page < total_pages
    has_prev = page > 1

    pagination_metadata = PaginationMetaDataSchema(
        current_page=page,
        per_page=limit,
        total_items=total_appointments_amount,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    response_schemas: List[ResponseAppointmentSchema] = []
    for appointment, patient, doctor, end_time, appointment_date in results:
        patient_schema: ResponsePatientSchema | None = (
            map_patient_domain_to_response_schema(patient) if patient else None
        )
        doctor_schema: UserSchema = map_user_domain_to_schema(doctor)

        response_schemas.append(
            map_appointment_domain_to_response_schema(
                appointment=appointment,
                appointment_end_time=end_time,
                appointment_date=appointment_date,
                patient_schema=patient_schema,
                doctor_schema=doctor_schema,
            )
        )

    final_response_schema_with_pagination = MultipleAppointmentsResponseSchema(
        items=response_schemas, pagination=pagination_metadata
    )

    return final_response_schema_with_pagination


@appointments_router.patch(
    "/appointments/{appointment_id}",
    response_model=ResponseAppointmentSchema,
)
@inject
async def update_appointment(
    appointment_id: int,
    update_data: UpdateAppointmentSchema,
    appointment_service: AppointmentService = Depends(
        Provide[RegistryContainer.appointment_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.APPOINTMENTS,
                    "scopes": [AvailableScopesEnum.UPDATE],
                },
            ],
        )
    ),
) -> ResponseAppointmentSchema:
    appointment, patient, doctor, end_time, appointment_date = (
        await appointment_service.update_appointment(
            appointment_id,
            update_data,
        )
    )

    patient_schema: ResponsePatientSchema | None = (
        map_patient_domain_to_response_schema(patient) if patient else None
    )
    doctor_schema: UserSchema = map_user_domain_to_schema(doctor)

    response_schema = map_appointment_domain_to_response_schema(
        appointment=appointment,
        appointment_end_time=end_time,
        appointment_date=appointment_date,
        patient_schema=patient_schema,
        doctor_schema=doctor_schema,
    )

    return response_schema


@appointments_router.post(
    "/days/{schedule_day_id}/appointments",
    response_model=ResponseAppointmentSchema,
    status_code=201,
)
@inject
async def create_appointment(
    schedule_day_id: UUID,
    create_data: CreateAppointmentSchema,
    appointment_service: AppointmentService = Depends(
        Provide[RegistryContainer.appointment_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.APPOINTMENTS,
                    "scopes": [AvailableScopesEnum.CREATE],
                },
            ],
        )
    ),
) -> ResponseAppointmentSchema:
    appointment, patient, doctor, end_time, appointment_date = (
        await appointment_service.create_appointment(
            schedule_day_id,
            create_data,
        )
    )

    patient_schema: ResponsePatientSchema | None = (
        map_patient_domain_to_response_schema(patient) if patient else None
    )
    doctor_schema: UserSchema = map_user_domain_to_schema(doctor)

    response_schema = map_appointment_domain_to_response_schema(
        appointment=appointment,
        appointment_end_time=end_time,
        appointment_date=appointment_date,
        patient_schema=patient_schema,
        doctor_schema=doctor_schema,
    )

    return response_schema


@appointments_router.delete("/appointments/{appointment_id}", status_code=204)
@inject
async def delete_appointment(
    appointment_id: int,
    appointment_service: AppointmentService = Depends(
        Provide[RegistryContainer.appointment_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.APPOINTMENTS,
                    "scopes": [AvailableScopesEnum.DELETE],
                },
            ],
        )
    ),
) -> None:
    await appointment_service.delete_by_id(appointment_id=appointment_id)
