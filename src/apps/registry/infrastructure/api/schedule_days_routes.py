import math
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.registry.container import RegistryContainer
from src.apps.registry.infrastructure.api.schemas.requests.schedule_day_schemas import (
    UpdateScheduleDaySchema,
)
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    MultipleScheduleDaysResponseSchema,
    ResponseScheduleDaySchema,
)
from src.apps.registry.services.schedule_day_service import ScheduleDayService
from src.shared.dependencies.check_user_permissions import check_user_permissions
from src.shared.dependencies.resources_map import (
    AvailableResourcesEnum,
    AvailableScopesEnum,
)
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)

schedule_days_router = APIRouter()


@schedule_days_router.get(
    "/schedules/days/{day_id}", response_model=ResponseScheduleDaySchema
)
@inject
async def get_by_id(
    day_id: UUID,
    schedule_day_service: ScheduleDayService = Depends(
        Provide[RegistryContainer.schedule_day_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.SCHEDULES,
                    "scopes": [AvailableScopesEnum.READ],
                },
            ],
        )
    ),
) -> ResponseScheduleDaySchema:
    schedule_day = await schedule_day_service.get_by_id(id=day_id)

    return ResponseScheduleDaySchema(
        id=schedule_day.id,
        schedule_id=schedule_day.schedule_id,
        day_of_week=schedule_day.day_of_week,
        is_active=schedule_day.is_active,
        work_start_time=schedule_day.work_start_time,
        work_end_time=schedule_day.work_end_time,
        break_start_time=schedule_day.break_start_time,
        break_end_time=schedule_day.break_end_time,
        date=schedule_day.date,
    )


@schedule_days_router.get(
    "/schedules/{schedule_id}/days", response_model=MultipleScheduleDaysResponseSchema
)
@inject
async def get_all_by_schedule_id(
    schedule_id: UUID,
    pagination_params: PaginationParams = Depends(),
    schedule_day_service: ScheduleDayService = Depends(
        Provide[RegistryContainer.schedule_day_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.SCHEDULES,
                    "scopes": [AvailableScopesEnum.READ],
                },
            ],
        )
    ),
) -> MultipleScheduleDaysResponseSchema:
    schedule_days, total_schedule_days_amount = (
        await schedule_day_service.get_all_by_schedule_id(
            schedule_id=schedule_id,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )
    )

    # Calculate pagination metadata
    page: int = pagination_params.page or 1  # for mypy
    limit: int = pagination_params.limit or 30  # for mypy
    total_pages = math.ceil(total_schedule_days_amount / limit) if limit else 1
    has_next = page < total_pages
    has_prev = page > 1

    pagination_metadata = PaginationMetaDataSchema(
        current_page=page,
        per_page=limit,
        total_items=total_schedule_days_amount,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    return MultipleScheduleDaysResponseSchema(
        items=[
            ResponseScheduleDaySchema(
                id=schedule_day.id,
                schedule_id=schedule_day.schedule_id,
                day_of_week=schedule_day.day_of_week,
                is_active=schedule_day.is_active,
                work_start_time=schedule_day.work_start_time,
                work_end_time=schedule_day.work_end_time,
                break_start_time=schedule_day.break_start_time,
                break_end_time=schedule_day.break_end_time,
                date=schedule_day.date,
            )
            for schedule_day in schedule_days
        ],
        pagination=pagination_metadata,
    )


@schedule_days_router.patch(
    "/schedules/days/{day_id}", response_model=ResponseScheduleDaySchema
)
@inject
async def update(
    day_id: UUID,
    update_schema: UpdateScheduleDaySchema,
    schedule_day_service: ScheduleDayService = Depends(
        Provide[RegistryContainer.schedule_day_service]
    ),
    _: None = Depends(
        check_user_permissions(
            resources=[
                {
                    "resource_name": AvailableResourcesEnum.SCHEDULES,
                    "scopes": [AvailableScopesEnum.UPDATE],
                },
            ],
        )
    ),
) -> ResponseScheduleDaySchema:
    return await schedule_day_service.update(
        day_id=day_id,
        update_data=update_schema,
    )
