import math
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.registry.container import RegistryContainer
from src.apps.registry.infrastructure.api.schemas.requests.filters.schedule_filter_params import (
    ScheduleFilterParams,
)
from src.apps.registry.infrastructure.api.schemas.requests.schedule_schemas import (
    CreateScheduleSchema,
    UpdateScheduleSchema,
)
from src.apps.registry.infrastructure.api.schemas.responses.schedule_schemas import (
    MultipleSchedulesResponseSchema,
    ResponseScheduleSchema,
)
from src.apps.registry.services.schedule_service import ScheduleService
from src.apps.users.mappers import map_user_domain_to_schema
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)

schedule_router = APIRouter()


@schedule_router.get("/schedules/{schedule_id}", response_model=ResponseScheduleSchema)
@inject
async def get_schedule_by_id(
    schedule_id: UUID,
    schedule_service: ScheduleService = Depends(
        Provide[RegistryContainer.schedule_service]
    ),
) -> ResponseScheduleSchema:
    schedule, doctor = await schedule_service.get_by_id(schedule_id)
    doctor_response_schema = map_user_domain_to_schema(doctor)
    schedule_response_schema = ResponseScheduleSchema(
        id=schedule.id,
        doctor=doctor_response_schema,
        schedule_name=schedule.schedule_name,
        period_start=schedule.period_start,
        period_end=schedule.period_end,
        is_active=schedule.is_active,
        appointment_interval=schedule.appointment_interval,
        description=schedule.description,
    )

    return schedule_response_schema


@schedule_router.get(
    "/schedules",
    response_model=MultipleSchedulesResponseSchema,
    summary="Get schedules with optional filters",
)
@inject
async def get_schedules(
    pagination_params: PaginationParams = Depends(),
    filter_params: ScheduleFilterParams = Depends(),
    schedule_service: ScheduleService = Depends(
        Provide[RegistryContainer.schedule_service]
    ),
) -> MultipleSchedulesResponseSchema:
    schedules_with_doctors, total_schedules_amount = (
        await schedule_service.get_schedules(
            pagination_params=pagination_params,
            filter_params=filter_params,
        )
    )

    # Calculate pagination metadata
    page: int = pagination_params.page or 1  # for mypy
    limit: int = pagination_params.limit or 30  # for mypy
    total_pages = math.ceil(total_schedules_amount / limit) if limit else 1
    has_next = page < total_pages
    has_prev = page > 1

    pagination_metadata = PaginationMetaDataSchema(
        current_page=page,
        per_page=limit,
        total_items=total_schedules_amount,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    return MultipleSchedulesResponseSchema(
        items=[
            ResponseScheduleSchema(
                id=schedule.id,
                doctor=map_user_domain_to_schema(doctor),
                schedule_name=schedule.schedule_name,
                period_start=schedule.period_start,
                period_end=schedule.period_end,
                is_active=schedule.is_active,
                appointment_interval=schedule.appointment_interval,
                description=schedule.description,
            )
            for schedule, doctor in schedules_with_doctors
        ],
        pagination=pagination_metadata,
    )


@schedule_router.post(
    "/doctors/{doctor_id}/schedules",
    response_model=ResponseScheduleSchema,
    status_code=201,
)
@inject
async def create_schedule(
    doctor_id: UUID,
    create_schema: CreateScheduleSchema,
    schedule_service: ScheduleService = Depends(
        Provide[RegistryContainer.schedule_service]
    ),
) -> ResponseScheduleSchema:
    schedule, doctor = await schedule_service.create_schedule(doctor_id, create_schema)
    doctor_response_schema = map_user_domain_to_schema(doctor)
    schedule_response_schema = ResponseScheduleSchema(
        id=schedule.id,
        doctor=doctor_response_schema,
        schedule_name=schedule.schedule_name,
        period_start=schedule.period_start,
        period_end=schedule.period_end,
        is_active=schedule.is_active,
        appointment_interval=schedule.appointment_interval,
        description=schedule.description,
    )

    return schedule_response_schema


@schedule_router.patch(
    "/schedules/{schedule_id}", response_model=ResponseScheduleSchema
)
@inject
async def update_schedule(
    schedule_id: UUID,
    update_schema: UpdateScheduleSchema,
    schedule_service: ScheduleService = Depends(
        Provide[RegistryContainer.schedule_service]
    ),
) -> ResponseScheduleSchema:
    updated_schedule, doctor = await schedule_service.update_schedule(
        schedule_id, update_schema
    )
    doctor_response_schema = map_user_domain_to_schema(doctor)
    schedule_response_schema = ResponseScheduleSchema(
        id=updated_schedule.id,
        doctor=doctor_response_schema,
        schedule_name=updated_schedule.schedule_name,
        period_start=updated_schedule.period_start,
        period_end=updated_schedule.period_end,
        is_active=updated_schedule.is_active,
        appointment_interval=updated_schedule.appointment_interval,
        description=updated_schedule.description,
    )

    return schedule_response_schema


@schedule_router.delete("/schedules/{schedule_id}", status_code=204)
@inject
async def delete_schedule(
    schedule_id: UUID,
    schedule_service: ScheduleService = Depends(
        Provide[RegistryContainer.schedule_service]
    ),
) -> None:
    await schedule_service.delete(schedule_id)
