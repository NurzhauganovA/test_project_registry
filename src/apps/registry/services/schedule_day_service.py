from datetime import date, datetime, timedelta
from typing import List, Tuple
from uuid import UUID

from src.apps.registry.domain.enums import AppointmentStatusEnum
from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.exceptions import NoInstanceFoundError
from src.apps.registry.infrastructure.api.schemas.requests.schedule_day_schemas import (
    UpdateScheduleDaySchema,
)
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    ResponseScheduleDaySchema,
)
from src.apps.registry.interfaces.repository_interfaces import (
    AppointmentRepositoryInterface,
    ScheduleDayRepositoryInterface,
)
from src.apps.registry.interfaces.uow_interface import UnitOfWorkInterface
from src.core.i18n import _
from src.core.logger import LoggerService


class ScheduleDayService:
    def __init__(
        self,
        uow: UnitOfWorkInterface,
        logger: LoggerService,
        schedule_day_repository: ScheduleDayRepositoryInterface,
        appointment_repository: AppointmentRepositoryInterface,
    ):
        self._uow = uow
        self._logger = logger
        self._repository = schedule_day_repository
        self._appointment_repository = appointment_repository

    async def get_by_id(self, id: UUID) -> ResponseScheduleDaySchema:
        async with self._uow:
            schedule_day = await self._uow.schedule_day_repository.get_by_id(id=id)

            if schedule_day is None:
                raise NoInstanceFoundError(
                    status_code=404,
                    detail=_("Day with ID: %(ID)s not found.") % {"ID": id},
                )

            return schedule_day

    async def get_all_by_schedule_id(
        self, schedule_id: UUID, limit: int = 30, page: int = 1
    ) -> Tuple[List[ResponseScheduleDaySchema], int]:
        async with self._uow:
            days = await self._uow.schedule_day_repository.get_all_by_schedule_id(
                schedule_id=schedule_id, limit=limit, page=page
            )

            total_amount_of_records: int = (
                await self._uow.schedule_day_repository.get_total_number_of_schedule_days()
            )

            return days, total_amount_of_records

    async def update(
        self,
        day_id: UUID,
        update_data: UpdateScheduleDaySchema,
    ) -> ResponseScheduleDaySchema:
        """
        Updates the parameters of one day:
            - Checks for conflicts with existing tricks.
            - Calls the repository for a partial update.
        """
        # Check if the day exists
        day = await self._repository.get_by_id(day_id)
        if not day:
            raise NoInstanceFoundError(
                status_code=404, detail=f"Day with ID: {day_id} not found."
            )

        # Get a day's schedule
        schedule: ScheduleDomain = await self._uow.schedule_repository.get_by_id(
            day.schedule_id
        )
        if not schedule:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Schedule with ID: %(ID)s not found.")
                % {"ID": day.schedule_id},
            )
        appointment_interval = schedule.appointment_interval

        # Get day's appointments
        appointments = await self._appointment_repository.get_appointments_by_day_id(
            schedule_day_id=day.id
        )
        booked_appointments = [
            appointment
            for appointment in appointments
            if appointment.status == AppointmentStatusEnum.BOOKED
        ]

        new_start = update_data.work_start_time or day.work_start_time
        new_end = update_data.work_end_time or day.work_end_time

        break_start_provided = "break_start_time" in update_data.model_fields_set
        break_end_provided = "break_end_time" in update_data.model_fields_set

        if (break_start_provided and update_data.break_start_time is None) or (
            break_end_provided and update_data.break_end_time is None
        ):
            effective_break_start = None
            effective_break_end = None

        elif not break_start_provided and not break_end_provided:
            if day.break_start_time is None or day.break_end_time is None:
                effective_break_start = None
                effective_break_end = None
            else:
                # "cutting" the old break time according to new hours
                break_start_time = max(day.break_start_time, new_start)
                break_end_time = min(day.break_end_time, new_end)
                # If there is no segment after "cutting", we remove break time completely
                if break_start_time >= break_end_time:
                    effective_break_start = None
                    effective_break_end = None
                else:
                    effective_break_start = break_start_time
                    effective_break_end = break_end_time

        else:
            effective_break_start = (
                update_data.break_start_time
                if break_start_provided
                else day.break_start_time
            )

            effective_break_end = (
                update_data.break_end_time if break_end_provided else day.break_end_time
            )

            if booked_appointments and effective_break_start and effective_break_end:
                for booked_appointment in booked_appointments:
                    appointment_start_time = datetime.combine(
                        date.min, booked_appointment.time
                    )
                    appointment_end_time = appointment_start_time + timedelta(
                        minutes=appointment_interval
                    )
                    break_start = datetime.combine(date.min, effective_break_start)
                    break_end = datetime.combine(date.min, effective_break_end)

                    if not (
                        appointment_end_time <= break_start
                        or appointment_start_time >= break_end
                    ):
                        # Cancel the appointment (appointment -> 'Cancel list')
                        async with self._uow:
                            booked_appointment.cancel()
                            await self._uow.appointment_repository.update(
                                booked_appointment
                            )

        # Check if the day is deactivated (is_active changes from True to False)
        is_deactivating = False
        if "is_active" in update_data.model_fields_set:
            new_is_active = update_data.is_active
            if day.is_active and (new_is_active is False):
                is_deactivating = True

        # If deactivation, we cancel all booked appointments
        if is_deactivating and booked_appointments:
            for booked_appointment in booked_appointments:
                async with self._uow:
                    booked_appointment.cancel()
                    await self._uow.appointment_repository.update(booked_appointment)

        update_schema = UpdateScheduleDaySchema(
            is_active=(
                update_data.is_active
                if update_data.is_active is not None
                else day.is_active
            ),
            work_start_time=new_start,
            work_end_time=new_end,
            break_start_time=effective_break_start,
            break_end_time=effective_break_end,
        )

        async with self._uow:
            updated_day = await self._uow.schedule_day_repository.update(
                day_id=day_id,
                schema=update_schema,
            )

            return updated_day

    async def delete(self, day_id: UUID) -> None:
        """
        Deletes a schedule day.
        """
        # Check if the day exists
        day: ResponseScheduleDaySchema | None = await self._repository.get_by_id(day_id)
        if not day:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Day with ID: %(ID)s not found.") % {"ID": day_id},
            )

        # Get day's appointments
        appointments = await self._appointment_repository.get_appointments_by_day_id(
            schedule_day_id=day.id
        )
        booked_appointments = [
            appointment
            for appointment in appointments
            if appointment.status == AppointmentStatusEnum.BOOKED
        ]

        if booked_appointments:
            for booked_appointment in booked_appointments:
                # Cancel the appointment (appointment -> 'Cancel list')
                async with self._uow:
                    booked_appointment.cancel()
                    await self._uow.appointment_repository.update(booked_appointment)

        async with self._uow:
            await self._uow.schedule_day_repository.delete_by_id(day_id)
