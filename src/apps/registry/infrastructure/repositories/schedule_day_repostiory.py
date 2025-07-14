from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select

from src.apps.registry.infrastructure.api.schemas.requests.schedule_day_schemas import (
    CreateScheduleDaySchema,
    UpdateScheduleDaySchema,
)
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    ResponseScheduleDaySchema,
)
from src.apps.registry.infrastructure.db_models.models import ScheduleDay
from src.apps.registry.interfaces.repository_interfaces import (
    ScheduleDayRepositoryInterface,
)
from src.apps.registry.mappers import map_schedule_day_db_entity_to_schema
from src.shared.infrastructure.base import BaseRepository


class ScheduleDayRepositoryImpl(BaseRepository, ScheduleDayRepositoryInterface):
    async def get_total_number_of_schedule_days(self) -> int:
        query = select(func.count(ScheduleDay.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(self, id: UUID) -> Optional[ResponseScheduleDaySchema]:
        result = await self._async_db_session.execute(
            select(ScheduleDay).where(ScheduleDay.id == id)
        )
        schedule_day = result.scalar_one_or_none()
        if schedule_day:
            return map_schedule_day_db_entity_to_schema(schedule_day)

        return None

    async def get_by_schedule_and_day_of_week(
        self, schedule_id: UUID, day_of_week: int
    ) -> Optional[ResponseScheduleDaySchema]:
        result = await self._async_db_session.execute(
            select(ScheduleDay).where(
                ScheduleDay.schedule_id == schedule_id,
                ScheduleDay.day_of_week == day_of_week,
            )
        )
        schedule_day = result.scalar_one_or_none()
        if schedule_day:
            return map_schedule_day_db_entity_to_schema(schedule_day)

        return None

    async def get_by_schedule_and_date(
        self, schedule_id: UUID, day_date: date
    ) -> Optional[ResponseScheduleDaySchema]:
        result = await self._async_db_session.execute(
            select(ScheduleDay)
            .where(ScheduleDay.schedule_id == schedule_id)
            .where(ScheduleDay.date == day_date)
        )
        schedule_day = result.scalar_one_or_none()
        if schedule_day:
            return map_schedule_day_db_entity_to_schema(schedule_day)

        return None

    async def get_all_by_schedule_id(
        self, schedule_id: UUID, limit: int = 30, page: int = 1
    ) -> List[ResponseScheduleDaySchema]:
        offset = (page - 1) * limit
        result = await self._async_db_session.execute(
            select(ScheduleDay)
            .where(ScheduleDay.schedule_id == schedule_id)
            .order_by(ScheduleDay.date)
            .limit(limit)
            .offset(offset)
        )
        schedule_days = result.scalars().all()

        return [map_schedule_day_db_entity_to_schema(sd) for sd in schedule_days]

    async def add(
        self, create_day_schema: CreateScheduleDaySchema
    ) -> ResponseScheduleDaySchema:
        new_day = ScheduleDay(
            schedule_id=create_day_schema.schedule_id,
            day_of_week=create_day_schema.day_of_week,
            is_active=create_day_schema.is_active,
            work_start_time=create_day_schema.work_start_time,
            work_end_time=create_day_schema.work_end_time,
            break_start_time=create_day_schema.break_start_time,
            break_end_time=create_day_schema.break_end_time,
            date=create_day_schema.date,
        )
        self._async_db_session.add(new_day)
        await self._async_db_session.flush()

        return map_schedule_day_db_entity_to_schema(new_day)

    async def update(
        self, day_id: UUID, schema: UpdateScheduleDaySchema
    ) -> ResponseScheduleDaySchema:
        result = await self._async_db_session.execute(
            select(ScheduleDay).where(ScheduleDay.id == day_id)
        )
        schedule_day = result.scalar_one_or_none()

        # Updating fields...
        schedule_day.is_active = schema.is_active
        schedule_day.work_start_time = schema.work_start_time
        schedule_day.work_end_time = schema.work_end_time
        schedule_day.break_start_time = schema.break_start_time
        schedule_day.break_end_time = schema.break_end_time

        self._async_db_session.add(schedule_day)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(schedule_day)

        return map_schedule_day_db_entity_to_schema(schedule_day)

    async def delete_by_id(self, id: UUID) -> None:
        result = await self._async_db_session.execute(
            select(ScheduleDay).where(ScheduleDay.id == id)
        )
        schedule_day = result.scalar_one_or_none()

        await self._async_db_session.delete(schedule_day)
        await self._async_db_session.flush()
