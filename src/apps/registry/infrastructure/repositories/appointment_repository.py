from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import joinedload

from src.apps.registry.domain.models.appointment import AppointmentDomain
from src.apps.registry.infrastructure.db_models.models import Appointment, ScheduleDay
from src.apps.registry.interfaces.repository_interfaces import (
    AppointmentRepositoryInterface,
)
from src.apps.registry.mappers import (
    map_appointment_db_entity_to_domain,
    map_appointment_domain_to_db_entity,
)
from src.shared.infrastructure.base import BaseRepository


class AppointmentRepositoryImpl(BaseRepository, AppointmentRepositoryInterface):
    _filters_map: Dict[str, Callable[[Any], Any]] = {
        "schedule_id": lambda value: AppointmentRepositoryImpl._filter_by_schedule_id(
            value
        ),
        "period_start": lambda value: AppointmentRepositoryImpl._filter_by_period_start(
            value
        ),
        "period_end": lambda value: AppointmentRepositoryImpl._filter_by_period_end(
            value
        ),
        "appointment_status_filter": lambda value: AppointmentRepositoryImpl._filter_by_status(
            value
        ),
    }

    @staticmethod
    def _filter_by_schedule_id(value):
        return ScheduleDay.schedule_id == value

    @staticmethod
    def _filter_by_period_start(value):
        return ScheduleDay.date >= value

    @staticmethod
    def _filter_by_period_end(value):
        return ScheduleDay.date <= value

    @staticmethod
    def _filter_by_status(value):
        return Appointment.status == value

    def _build_filters(self, filters: dict) -> list:
        conditions = []
        for key, value in filters.items():
            if value is None:
                continue

            filter_function = self._filters_map.get(key)
            if filter_function:
                conditions.append(filter_function(value))

        return conditions

    async def get_total_number_of_appointments(self) -> int:
        query = select(func.count(Appointment.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(self, id: int) -> Optional[AppointmentDomain]:
        result = await self._async_db_session.execute(
            select(Appointment).where(Appointment.id == id)
        )
        appointment = result.scalar_one_or_none()
        if appointment:
            return map_appointment_db_entity_to_domain(appointment)

        return None

    async def get_appointments_by_day_id(
        self, schedule_day_id: UUID
    ) -> List[AppointmentDomain]:
        result = await self._async_db_session.execute(
            select(Appointment)
            .where(Appointment.schedule_day_id == schedule_day_id)
            .order_by(Appointment.time)
        )
        db_rows = result.scalars().all()

        return [map_appointment_db_entity_to_domain(row) for row in db_rows]

    async def get_by_schedule_id(
        self, schedule_id: UUID, page: int = 1, limit: int = 30
    ) -> List[AppointmentDomain]:
        offset = (page - 1) * limit

        stmt = (
            select(Appointment)
            .join(Appointment.schedule_day)
            .where(ScheduleDay.schedule_id == schedule_id)
            .options(joinedload(Appointment.schedule_day))
            .order_by(ScheduleDay.date, Appointment.time)
            .offset(offset)
            .limit(limit)
        )

        result = await self._async_db_session.execute(stmt)
        rows = result.scalars().all()

        return [map_appointment_db_entity_to_domain(row) for row in rows]

    async def get_appointments(
        self,
        filters: dict,
        limit: int = 30,
        page: int = 1,
    ):
        stmt = (
            select(Appointment)
            .join(Appointment.schedule_day)
            .options(joinedload(Appointment.schedule_day))
            .order_by(ScheduleDay.date, Appointment.time)
        )

        conditions = self._build_filters(filters)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.limit(limit).offset((page - 1) * limit)

        result = await self._async_db_session.execute(stmt)
        rows = result.scalars().all()

        return [map_appointment_db_entity_to_domain(row) for row in rows]

    async def add(self, appointment: AppointmentDomain) -> AppointmentDomain:
        db_entity = map_appointment_domain_to_db_entity(appointment)

        self._async_db_session.add(db_entity)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_entity)

        return map_appointment_db_entity_to_domain(db_entity)

    async def update(self, appointment: AppointmentDomain) -> AppointmentDomain:
        result = await self._async_db_session.execute(
            select(Appointment).where(Appointment.id == appointment.id)
        )
        existing = result.scalar_one_or_none()

        db_entity = map_appointment_domain_to_db_entity(appointment)

        fields_to_update = [
            "schedule_day_id",
            "time",
            "patient_id",
            "phone_number",
            "address",
            "status",
            "type",
            "financing_sources_ids",
            "reason",
            "additional_services",
            "office_number",
            "cancelled_at",
        ]

        # Updating fields...
        for field in fields_to_update:
            setattr(existing, field, getattr(db_entity, field))

        self._async_db_session.add(existing)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(existing)

        return map_appointment_db_entity_to_domain(existing)

    async def delete_by_id(self, id: int) -> None:
        result = await self._async_db_session.execute(
            select(Appointment).where(Appointment.id == id)
        )
        existing = result.scalar_one_or_none()

        await self._async_db_session.delete(existing)
        await self._async_db_session.commit()
