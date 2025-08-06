from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from src.apps.platform_rules.infrastructure.api.schemas.responses.platform_rules_schemas import (
    ResponsePlatformRuleSchema,
)
from src.apps.platform_rules.interfaces.platform_rules_repository_interface import (
    PlatformRulesRepositoryInterface,
)
from src.apps.registry.domain.enums import AppointmentStatusEnum
from src.apps.registry.domain.models.appointment import AppointmentDomain
from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.exceptions import (
    NoInstanceFoundError,
    ScheduleExceedsMaxAllowedPeriod,
    ScheduleInvalidUpdateDatesError,
    ScheduleNameIsAlreadyTakenError,
    UserRoleIsNotSchedulableError,
)
from src.apps.registry.infrastructure.api.schemas.requests.filters.schedule_filter_params import (
    ScheduleFilterParams,
)
from src.apps.registry.infrastructure.api.schemas.requests.schedule_day_schemas import (
    CreateScheduleDaySchema,
    ScheduleDayTemplateSchema,
)
from src.apps.registry.infrastructure.api.schemas.requests.schedule_schemas import (
    CreateScheduleSchema,
    UpdateScheduleSchema,
)
from src.apps.registry.interfaces.repository_interfaces import (
    AppointmentRepositoryInterface,
    ScheduleDayRepositoryInterface,
    ScheduleRepositoryInterface,
)
from src.apps.registry.interfaces.uow_interface import UnitOfWorkInterface
from src.apps.registry.services.schedule_day_service import ScheduleDayService
from src.apps.users.domain.models.user import UserDomain
from src.apps.users.services.user_service import UserService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.core.settings import project_settings
from src.shared.exceptions import ApplicationError
from src.shared.schemas.pagination_schemas import PaginationParams


class ScheduleService:
    def __init__(
        self,
        uow: UnitOfWorkInterface,
        logger: LoggerService,
        schedule_repository: ScheduleRepositoryInterface,
        appointment_repository: AppointmentRepositoryInterface,
        schedule_day_repository: ScheduleDayRepositoryInterface,
        schedule_day_service: ScheduleDayService,
        user_service: UserService,
        platform_rules_repository: PlatformRulesRepositoryInterface,
    ):
        self._uow = uow
        self._logger = logger
        self._schedule_repository = schedule_repository
        self._appointment_repository = appointment_repository
        self._schedule_day_repository = schedule_day_repository
        self._schedule_day_service = schedule_day_service
        self._user_service = user_service
        self._platform_rules_repository = platform_rules_repository

    @staticmethod
    def _to_time(val):
        if isinstance(val, time) or val is None:
            return val
        if isinstance(val, str):
            return time.fromisoformat(val)

        raise ValueError(f"Unexpected time format: {val!r}")

    @staticmethod
    def _generate_days_for_schedule(
        schedule_id: UUID,
        period_start: date,
        period_end: date,
        week_days_template: List[ScheduleDayTemplateSchema],
        reduced_days: Optional[List[dict]] = None,
    ) -> List[CreateScheduleDaySchema]:
        """
        Generates a list of days for the schedule, applying week template and platform rules.

        Args:
            schedule_id (UUID): Schedule UUID (same for all days)
            period_start (date): Period start date
            period_end (date): Period end date
            week_days_template (List[ScheduleDayTemplateSchema]): List of patterns for each day of the week
            reduced_days (Optional[List[dict]]): Rules for 'reduced' days (from platform rules)

        Returns:
            List[CreateScheduleDaySchema]: List of days
        """
        default_template = {
            "is_active": True,
            "work_start_time": time.fromisoformat("08:00:00"),
            "work_end_time": time.fromisoformat("17:00:00"),
            "break_start_time": time.fromisoformat("13:00:00"),
            "break_end_time": time.fromisoformat("14:00:00"),
        }
        # Templates by days of the week
        template_by_day: Dict[int, dict] = {
            tpl.day_of_week: tpl.model_dump() for tpl in week_days_template
        }

        # Convert the reduced_days list to a dictionary by date
        reduced_by_date: Dict[date, dict] = {}
        if reduced_days:
            for entry in reduced_days:
                dt = entry["date"]
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt).date()
                reduced_by_date[dt] = entry

        result: List[CreateScheduleDaySchema] = []
        current_date = period_start

        while current_date <= period_end:
            dow = current_date.weekday() + 1
            override_entry = reduced_by_date.get(current_date)

            if override_entry:
                # If the day is completely disabled
                if not override_entry.get("is_active", True):
                    template_data = default_template.copy()
                    template_data["is_active"] = False
                else:
                    # Substitute redefined times or take from template/default
                    base = template_by_day.get(dow, default_template)
                    template_data = {
                        "is_active": True,
                        "work_start_time": override_entry.get("work_start_time")
                        or base["work_start_time"],
                        "work_end_time": override_entry.get("work_end_time")
                        or base["work_end_time"],
                        "break_start_time": override_entry.get("break_start_time")
                        or base["break_start_time"],
                        "break_end_time": override_entry.get("break_end_time")
                        or base["break_end_time"],
                    }
            else:
                # Common template
                template_data = template_by_day.get(dow, default_template).copy()

            # Convert string fields to time
            work_start = ScheduleService._to_time(template_data.get("work_start_time"))
            work_end = ScheduleService._to_time(template_data.get("work_end_time"))
            br_start = ScheduleService._to_time(template_data.get("break_start_time"))
            br_end = ScheduleService._to_time(template_data.get("break_end_time"))

            # If it “intersects” with the working day, we remove the pause
            if br_start and br_end and work_start and work_end:
                if br_start < work_start or br_end > work_end:
                    br_start = None
                    br_end = None

            # Preparing final values
            template_data["work_start_time"] = work_start
            template_data["work_end_time"] = work_end
            template_data["break_start_time"] = br_start
            template_data["break_end_time"] = br_end

            # Assembling the schema
            day_schema = CreateScheduleDaySchema(
                schedule_id=schedule_id,
                date=current_date,
                day_of_week=dow,
                is_active=template_data["is_active"],
                work_start_time=template_data["work_start_time"],
                work_end_time=template_data["work_end_time"],
                break_start_time=template_data["break_start_time"],
                break_end_time=template_data["break_end_time"],
            )
            result.append(day_schema)
            current_date += timedelta(days=1)

        return result

    async def _move_appointments_to_waiting_list(
        self, appointments: List[AppointmentDomain]
    ):
        for appointment in appointments:
            appointment.status = AppointmentStatusEnum.CANCELLED
            await self._appointment_repository.update(appointment)

    @staticmethod
    def _is_provided_role_schedulable(role_name: str) -> bool:
        """
        Checks whether the given user role is allowed to have a schedule.

        Args:
            role_name (str): The name of the user role to check.

        Returns:
            bool: True if the role is allowed for scheduling, False otherwise.
        """
        return role_name in project_settings.SCHEDULABLE_USER_ROLES

    async def get_by_id(self, schedule_id: UUID) -> List[ScheduleDomain | UserDomain]:
        """
        Retrieves a schedule by its ID.

        :return: Schedule and User (doctor) domain objects.
        """
        schedule = await self._schedule_repository.get_by_id(schedule_id)
        if not schedule:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Schedule with ID: %(ID)s not found.") % {"ID": schedule_id},
            )

        doctor = await self._user_service.get_by_id(schedule.doctor_id)

        return [schedule, doctor]

    async def get_schedules(
        self,
        pagination_params: PaginationParams,
        filter_params: ScheduleFilterParams,
    ) -> Tuple[List[Tuple[ScheduleDomain, UserDomain]], int]:
        """
        Gets a list of graphs taking into account filtering and pagination.

        :param pagination_params: Pagination parameters (page number, page size)
        :param filter_params: Graph filtering parameters
        (by doctor's full name, schedule name, area, status, etc.)

        :return: Tuple with a list of schedule domain models corresponding to filters with their doctors
        and total number of schedules in the DB as integer.
        """
        filters: dict = filter_params.to_dict(exclude_none=True)

        schedules = await self._schedule_repository.get_schedules(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        total_amount_of_records: int = (
            await self._schedule_repository.get_total_number_of_schedules()
        )

        result = []
        for schedule in schedules:
            doctor = await self._user_service.get_by_id(schedule.doctor_id)
            result.append((schedule, doctor))

        return result, total_amount_of_records

    async def create_schedule(
        self, doctor_id: UUID, create_schema: CreateScheduleSchema
    ) -> List[ScheduleDomain | UserDomain]:
        """
        Creates a schedule, checks that the schedule does not overlap with an existing one,
        generates schedule days from a template, creates a domain model and saves it.
        All GET queries are executed outside the UOW.

        :return: List of ScheduleDomain and UserDomain (doctor) objects.
        """
        # Check if a doctor exists
        existing_user = await self._user_service.get_by_id(doctor_id)
        if not existing_user:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("User with ID: %(ID)s not found or not a doctor.")
                % {"ID": doctor_id},
            )

        # Check if at least one of the provided client roles is schedulable
        if not any(
            self._is_provided_role_schedulable(role_name)
            for role_name in existing_user.client_roles
        ):
            raise UserRoleIsNotSchedulableError(
                status_code=409,
                detail=_(
                    "Schedule creation for a user with the provided set of client roles is prohibited."
                ),
            )

        # Check if a user already has a schedule with the same schedule name
        schedule_with_same_name = await self._schedule_repository.get_schedules(
            filters={
                "name_filter": create_schema.schedule_name,
                "doctor_id_filter": doctor_id,
            },
            limit=1,
        )
        if schedule_with_same_name:
            raise ScheduleNameIsAlreadyTakenError(
                status_code=409,
                detail=_(
                    "Schedule with name: '%(NAME)s' for this specialist is already taken."
                )
                % {"NAME": create_schema.schedule_name},
            )

        schedule_domain = ScheduleDomain(
            doctor_id=doctor_id,
            schedule_name=create_schema.schedule_name,
            period_start=create_schema.period_start,
            period_end=create_schema.period_end,
            is_active=create_schema.is_active,
            appointment_interval=create_schema.appointment_interval,
        )

        user_domain = await self._user_service.get_by_id(doctor_id)

        # Max period for schedule. Being installed from the Admin Panel.
        raw_max_schedule_period_days: Optional[ResponsePlatformRuleSchema] = (
            await self._platform_rules_repository.get_by_key("MAX_SCHEDULE_PERIOD")
        )

        async with self._uow:
            # Check if the schedule doesn't exceed a max period
            max_schedule_period_days = 30  # Default value
            if raw_max_schedule_period_days:
                try:
                    potential_days: int = raw_max_schedule_period_days.rule_data[
                        "value"
                    ]
                    if potential_days > 0:
                        max_schedule_period_days = potential_days
                    else:
                        self._logger.warning(
                            f"Platform rule 'MAX_SCHEDULE_PERIOD' has non-positive value "
                            f"'{raw_max_schedule_period_days}'. Using default {max_schedule_period_days}."
                        )
                except (ValueError, TypeError):
                    self._logger.warning(
                        f"Platform rule 'MAX_SCHEDULE_PERIOD' is invalid type or format:"
                        f" '{raw_max_schedule_period_days}'. Using default: {max_schedule_period_days}."
                    )

            period_duration = schedule_domain.period_end - schedule_domain.period_start
            if period_duration.days > max_schedule_period_days:
                raise ScheduleExceedsMaxAllowedPeriod(
                    status_code=409,
                    detail=_(
                        "Schedule period exceeds the maximum allowed period of: %(MAX_VALUE)s days."
                    )
                    % {"MAX_VALUE": max_schedule_period_days},
                )

            just_created_schedule = await self._uow.schedule_repository.add(
                schedule_domain
            )

            # Generate schedule days using the provided week-days template
            reduced_days_rule = await self._platform_rules_repository.get_by_key(
                "REDUCED_DAYS"
            )
            reduced_days = (
                reduced_days_rule.rule_data.get("days", [])
                if reduced_days_rule
                else None
            )

            days: List[CreateScheduleDaySchema] = self._generate_days_for_schedule(
                just_created_schedule.id,
                just_created_schedule.period_start,
                just_created_schedule.period_end,
                create_schema.week_days_template,
                reduced_days=reduced_days,
            )

            for day_schema in days:
                await self._uow.schedule_day_repository.add(day_schema)

        return [just_created_schedule, user_domain]

    async def update_schedule(
        self, schedule_id: UUID, update_schema: UpdateScheduleSchema
    ) -> List[ScheduleDomain | UserDomain]:
        """
        Updates an existing schedule, including:
          - changing basic info (only provided fields),
          - adjusting the period if new dates provided (the new period must be nested within the original),
          - updating associated JSONB fields if provided,
          - updating schedule days for the specified days if provided.

        If any day within the new period has active appointments, updating it is forbidden.
        All GET queries are executed outside UOW.

        :return: List of ScheduleDomain and UserDomain (doctor) objects.
        """
        # Check if the schedule exists
        schedule = await self._schedule_repository.get_by_id(schedule_id)
        if not schedule:
            raise NoInstanceFoundError(
                status_code=404,
                detail=f"Schedule with ID: {schedule_id} not found.",
            )
        if schedule.id is None:
            self._logger.warning("Internal error: schedule.id is missing after fetch.")
            raise ApplicationError(
                status_code=500,
                detail="Something went wrong. Please, try again later.",
            )

        doctor_domain: UserDomain = await self._user_service.get_by_id(
            schedule.doctor_id
        )

        # Check if a user already has a schedule with the same schedule name if it's provided
        if update_schema.schedule_name:
            schedule_with_same_name = await self._schedule_repository.get_schedules(
                filters={
                    "name_filter": update_schema.schedule_name,
                    "doctor_id_filter": schedule.doctor_id,
                },
                limit=1,
            )
            if schedule_with_same_name:
                raise ScheduleNameIsAlreadyTakenError(
                    status_code=409,
                    detail=_(
                        "Schedule with name: '%(NAME)s' for this specialist is already taken."
                    )
                    % {"NAME": update_schema.schedule_name},
                )

        new_start = update_schema.period_start or schedule.period_start
        new_end = update_schema.period_end or schedule.period_end

        if new_end < new_start:
            raise ScheduleInvalidUpdateDatesError(
                status_code=409,
                detail="New schedule end date cannot be earlier than new start date.",
            )

        # Check if the schedule doesn't exceed a max period
        if update_schema.period_start or update_schema.period_end:
            raw_max_schedule_period_days: Optional[ResponsePlatformRuleSchema] = (
                await self._platform_rules_repository.get_by_key("MAX_SCHEDULE_PERIOD")
            )

            max_schedule_period_days = 30  # Default value
            if raw_max_schedule_period_days:
                try:
                    potential_days: int = raw_max_schedule_period_days.rule_data[
                        "value"
                    ]
                    if potential_days > 0:
                        max_schedule_period_days = potential_days
                    else:
                        self._logger.warning(
                            f"Platform rule 'MAX_SCHEDULE_PERIOD' has non-positive value "
                            f"'{raw_max_schedule_period_days.rule_data.get('value')}'. "
                            f"Using default {max_schedule_period_days}."
                        )
                except (ValueError, TypeError):
                    self._logger.warning(
                        f"Platform rule 'MAX_SCHEDULE_PERIOD' is invalid type or format:"
                        f" '{raw_max_schedule_period_days.rule_data.get('value')}'. "
                        f"Using default: {max_schedule_period_days}."
                    )

            period_duration = new_end - new_start
            if period_duration.days > max_schedule_period_days:
                raise ScheduleExceedsMaxAllowedPeriod(
                    status_code=409,
                    detail=_(
                        "New schedule period exceeds the maximum allowed period of: %(MAX_VALUE)s days."
                    )
                    % {"MAX_VALUE": max_schedule_period_days},
                )

        # Check if 'is_active' field value changes from True to False
        is_deactivating = (
            "is_active" in update_schema.model_fields_set
            and schedule.is_active
            and update_schema.is_active is False
        )

        # Updating fields...
        for field, value in update_schema.model_dump(exclude_unset=True).items():
            setattr(schedule, field, value)

        # We get all current days of the schedule
        existing_days = await self._schedule_day_repository.get_all_by_schedule_id(
            schedule.id, limit=1000, page=1
        )
        existing_dates = {day.date for day in existing_days}

        # Generate the required days for the entire new range (if the schedule was extended)
        reduced_days_rule = await self._platform_rules_repository.get_by_key(
            "REDUCED_DAYS"
        )
        reduced_days = (
            reduced_days_rule.rule_data.get("days", []) if reduced_days_rule else None
        )

        days_to_add = []
        current_date = new_start
        while current_date <= new_end:
            if current_date not in existing_dates:
                day_of_week = current_date.isoweekday()
                # Looking for a template among the existing days of the schedule
                existing_template = next(
                    (day for day in existing_days if day.day_of_week == day_of_week),
                    None,
                )
                if existing_template:
                    week_days_template = [existing_template]
                else:
                    week_days_template = []

                generated_days = self._generate_days_for_schedule(
                    schedule.id,
                    current_date,
                    current_date,
                    week_days_template,
                    reduced_days=reduced_days,
                )
                day_schema = generated_days[0]

                days_to_add.append(day_schema)
            current_date += timedelta(days=1)

        # Delete the existing schedule's days (if the schedule was shortened)
        days_to_delete: List[UUID] = []
        for day in existing_days:
            if day.date < new_start or day.date > new_end:
                days_to_delete.append(day.id)

        async with self._uow:
            if is_deactivating:
                for day in existing_days:
                    appointments = (
                        await self._appointment_repository.get_appointments_by_day_id(
                            day.id
                        )
                    )
                    booked_appointments = [
                        appointment
                        for appointment in appointments
                        if appointment.status == AppointmentStatusEnum.BOOKED
                    ]

                    if booked_appointments:
                        await self._move_appointments_to_waiting_list(
                            booked_appointments
                        )

            updated_schedule = await self._uow.schedule_repository.update(schedule)

            for day_schema in days_to_add:
                await self._uow.schedule_day_repository.add(day_schema)

            for day_id in days_to_delete:
                appointments = (
                    await self._appointment_repository.get_appointments_by_day_id(
                        day_id
                    )
                )
                booked_appointments = [
                    appointment
                    for appointment in appointments
                    if appointment.status == AppointmentStatusEnum.BOOKED
                ]

                if booked_appointments:
                    await self._move_appointments_to_waiting_list(booked_appointments)

                await self._uow.schedule_day_repository.delete_by_id(day_id)

        return [updated_schedule, doctor_domain]

    async def delete(self, schedule_id: UUID) -> None:
        """
        Deletes a schedule and all associated days.
        """
        schedule = await self._uow.schedule_repository.get_by_id(schedule_id)
        if not schedule:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Schedule with ID: %(ID)s not found.") % {"ID": schedule_id},
            )

        days = await self._schedule_day_repository.get_all_by_schedule_id(
            schedule_id, limit=1000, page=1
        )
        for day in days:
            appointments = (
                await self._appointment_repository.get_appointments_by_day_id(day.id)
            )
            booked_appointments = [
                appointment
                for appointment in appointments
                if appointment.status == AppointmentStatusEnum.BOOKED
            ]
            if booked_appointments:
                await self._move_appointments_to_waiting_list(booked_appointments)

        async with self._uow:
            await self._schedule_repository.delete(schedule_id)

        async with self._uow:
            # Delete the schedule itself
            await self._schedule_repository.delete(schedule_id)
