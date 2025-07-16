from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from src.apps.catalogs.services.financing_sources_catalog_service import (
    FinancingSourceCatalogService,
)
from src.apps.patients.domain.patient import PatientDomain
from src.apps.patients.services.patients_service import PatientService
from src.apps.registry.domain.enums import (
    AppointmentPatientTypeEnum,
    AppointmentStatusEnum,
)
from src.apps.registry.domain.exceptions import InvalidAppointmentStatusDomainError
from src.apps.registry.domain.exceptions import (
    ScheduleDayIsNotActiveError as ScheduleDayIsNotActiveErrorDomain,
)
from src.apps.registry.domain.models.appointment import AppointmentDomain
from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.exceptions import (
    AppointmentOverlappingError,
    InvalidAppointmentInsuranceTypeError,
    InvalidAppointmentStatusError,
    InvalidAppointmentTimeError,
    NoInstanceFoundError,
    ScheduleDayIsNotActiveError,
    ScheduleDayNotFoundError,
    ScheduleIsNotActiveError,
)
from src.apps.registry.infrastructure.api.schemas.requests.appointment_schemas import (
    AdditionalServiceSchema,
    CreateAppointmentSchema,
    UpdateAppointmentSchema,
)
from src.apps.registry.infrastructure.api.schemas.requests.filters.appointment_filter_params import (
    AppointmentFilterParams,
)
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    ResponseScheduleDaySchema,
)
from src.apps.registry.interfaces.repository_interfaces import (
    AppointmentRepositoryInterface,
    ScheduleDayRepositoryInterface,
    ScheduleRepositoryInterface,
)
from src.apps.registry.interfaces.uow_interface import UnitOfWorkInterface
from src.apps.registry.mappers import (
    map_appointment_create_schema_to_domain,
    map_appointment_update_schema_to_domain,
)
from src.apps.users.domain.models.user import UserDomain
from src.apps.users.interfaces.user_repository_interface import UserRepositoryInterface
from src.apps.users.services.user_service import UserService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import ApplicationError
from src.shared.schemas.pagination_schemas import PaginationParams


class AppointmentService:
    def __init__(
        self,
        uow: UnitOfWorkInterface,
        logger: LoggerService,
        appointment_repository: AppointmentRepositoryInterface,
        schedule_repository: ScheduleRepositoryInterface,
        schedule_day_repository: ScheduleDayRepositoryInterface,
        user_service: UserService,
        patients_service: PatientService,
        financing_sources_catalog_service: FinancingSourceCatalogService,
        user_repository: UserRepositoryInterface,
    ):
        self._uow = uow
        self._logger = logger
        self._appointment_repository = appointment_repository
        self._schedule_repository = schedule_repository
        self._schedule_day_repository = schedule_day_repository
        self._user_service = user_service
        self._patients_service = patients_service
        self._financing_sources_catalog_service = financing_sources_catalog_service
        self._user_repository = user_repository

    @staticmethod
    def __subtract_interval(base_date: date, base_time: time, minutes: int) -> datetime:
        base_datetime = datetime.combine(base_date, base_time)
        return base_datetime - timedelta(minutes=minutes)

    @staticmethod
    def __add_interval(base_date: date, base_time: time, minutes: int) -> datetime:
        base_datetime = datetime.combine(base_date, base_time)
        return base_datetime + timedelta(minutes=minutes)

    @staticmethod
    def _validate_appointment_within_working_hours(
        appointment_start_datetime: datetime,
        appointment_end_datetime: datetime,
        schedule_day,
        appointment_interval_minutes: int,
        requested_start_time: time,
    ) -> None:
        working_day_start_datetime = datetime.combine(
            schedule_day.date, schedule_day.work_start_time
        )
        working_day_end_datetime = datetime.combine(
            schedule_day.date, schedule_day.work_end_time
        )

        if (appointment_start_datetime < working_day_start_datetime) or (
            appointment_end_datetime > working_day_end_datetime
        ):
            raise InvalidAppointmentTimeError(
                status_code=409,
                detail=_(
                    "Selected time from %(start_time)s for %(appointment_interval)d-minute appointment "
                    "is outside working hours (%(work_start_time)s–%(work_end_time)s)."
                )
                % {
                    "start_time": requested_start_time,
                    "appointment_interval": appointment_interval_minutes,
                    "work_start_time": schedule_day.work_start_time,
                    "work_end_time": schedule_day.work_end_time,
                },
            )

    @staticmethod
    def _validate_doctor_profile_dict(
        doctor_dict: Dict,
        key: str,
        exc_class: type[ApplicationError],
        detail: str,
        *,
        status_code: int = 409,
    ):
        if not doctor_dict or not doctor_dict.get(key, False):
            raise exc_class(status_code=status_code, detail=detail)

    @staticmethod
    def _extract_key(obj: Any) -> str:
        return getattr(obj, "value", str(obj))

    @staticmethod
    def _check_appointment_overlapping(
        appointment_start_datetime: datetime,
        appointment_end_datetime: datetime,
        existing_appointments: List[AppointmentDomain],
        schedule_day_date: date,
        appointment_interval_minutes: int,
        current_appointment_id: Optional[int] = None,
    ) -> None:
        for existing_appointment in existing_appointments:
            if (
                current_appointment_id is not None
                and existing_appointment.id == current_appointment_id
            ):
                continue

            if existing_appointment.status == AppointmentStatusEnum.CANCELLED:
                continue

            existing_start = datetime.combine(
                schedule_day_date, existing_appointment.time
            )
            existing_end = existing_start + timedelta(
                minutes=appointment_interval_minutes
            )

            if (appointment_start_datetime < existing_end) and (
                appointment_end_datetime > existing_start
            ):
                raise AppointmentOverlappingError(
                    status_code=409,
                    detail=_("The selected appointment slot is already booked."),
                )

    @staticmethod
    def _check_appointment_exists(
        appointment: Optional[AppointmentDomain], appointment_id: int
    ) -> AppointmentDomain:
        if not appointment:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Appointment with ID: %(ID)s not found.")
                % {"ID": appointment_id},
            )
        return appointment

    @staticmethod
    def _check_schedule_exists(
        schedule: Optional[ScheduleDomain], schedule_id: UUID
    ) -> ScheduleDomain:
        if not schedule:
            raise ScheduleDayNotFoundError(
                status_code=404,
                detail=_("Schedule for day ID %(ID)s not found.") % {"ID": schedule_id},
            )
        return schedule

    @staticmethod
    def _check_schedule_day_exists(
        schedule_day: Optional[ResponseScheduleDaySchema], schedule_day_id: UUID
    ) -> ResponseScheduleDaySchema:
        if not schedule_day:
            raise ScheduleDayNotFoundError(
                status_code=404,
                detail=_("Schedule day with ID %(ID)s not found.")
                % {"ID": schedule_day_id},
            )
        return schedule_day

    @staticmethod
    def __validate_appointment_status(appointment: AppointmentDomain) -> None:
        """
        Performs validation of appointment status consistency by delegating
        to the domain model's `validate_appointment_status` method.

        Note:
            This method ensures that the appointment's status aligns correctly
            with the presence or absence of a patient_id according to business rules:
                - 'appointment' status requires a non-null `patient_id`.
                - 'booked' status requires `patient_id` to be None.

        Raises:
            InvalidAppointmentStatusError: Raised if the domain validation fails,
                wrapping the domain-specific InvalidAppointmentStatusDomainError.
        """
        try:
            appointment.validate_appointment_status()
        except InvalidAppointmentStatusDomainError as err:
            raise InvalidAppointmentStatusError(
                status_code=409, detail=_(err.detail)
            ) from err

    @staticmethod
    async def _load_entities_by_ids(ids: set, load_function):
        results = []
        for entity_id in ids:
            entity = await load_function(entity_id)
            if entity is not None:
                results.append(entity)
        return {entity.id: entity for entity in results}

    @staticmethod
    def _appointment_passes_filters(
        patient: Optional[PatientDomain],
        schedule_day,
        schedule,
        doctors_map: dict[int, UserDomain],
        filter_params: AppointmentFilterParams,
    ) -> bool:
        if filter_params.patient_iin_filter:
            if not patient or patient.iin != filter_params.patient_iin_filter:
                return False

        if schedule_day is None or schedule is None:
            return False

        if (
            filter_params.doctor_id_filter
            and schedule.doctor_id != filter_params.doctor_id_filter
        ):
            return False

        if filter_params.patient_full_name_filter:
            if not patient:
                return False

            full_name = (
                f"{patient.last_name} {patient.first_name} {patient.middle_name or ''}"
                f" {patient.maiden_name or ''}"
            ).lower()
            if filter_params.patient_full_name_filter.lower() not in full_name:
                return False

        if filter_params.doctor_specialization_filter:
            doctor = doctors_map.get(schedule.doctor_id)
            if not doctor:
                return False

            specialization_filter = (
                filter_params.doctor_specialization_filter.strip().lower()
            )
            if not any(
                specialization.get("name", "").strip().lower() == specialization_filter
                for specialization in (doctor.specializations or [])
            ):
                return False

        if filter_params.attached_area_number_filter:
            if not patient or not patient.attachment_data:
                return False

            area_number = patient.attachment_data.get("area_number")
            if area_number != filter_params.attached_area_number_filter:
                return False

        return True

    async def _validate_financing_sources(
        self, financing_sources_ids: List[int]
    ) -> None:
        for fs_id in financing_sources_ids:
            await self._financing_sources_catalog_service.get_by_id(fs_id)

    async def _validate_additional_services(
        self, additional_services: List[AdditionalServiceSchema]
    ) -> None:
        for service in additional_services:
            await self._financing_sources_catalog_service.get_by_id(
                service.financing_source_id
            )

    @staticmethod
    def _check_doctor_support(
        obj: Any, doctor: UserDomain, attribute_name: str, error_message: str
    ) -> None:
        key = AppointmentService._extract_key(obj)
        served = getattr(doctor, attribute_name, [])
        if key not in served:
            raise InvalidAppointmentInsuranceTypeError(
                status_code=409,
                detail=_(error_message),
            )

    async def _validate_time_change(
        self,
        schedule_day_id: UUID,
        schedule_day: ResponseScheduleDaySchema,
        schedule: ScheduleDomain,
        new_time: time,
        current_appointment_id: Optional[int] = None,
    ) -> None:
        """
        Validate the proposed change in appointment time and schedule day.

        This method ensures that the schedule is active, the new appointment time
        fits within the working hours of the schedule day, does not overlap with
        the scheduled break, and does not conflict with existing appointments.

        Args:
            schedule_day_id (UUID): The identifier of the schedule day.
            schedule_day (ResponseScheduleDaySchema): The schedule day details.
            schedule (ScheduleDomain): The schedule information including interval and status.
            new_time (time): The new appointment start time proposed.
            current_appointment_id (Optional[int], optional): The ID of the appointment
                being updated, to exclude it from overlap checks. Defaults to None.

        Raises:
            ScheduleIsNotActiveError: If the associated schedule is inactive.
            InvalidAppointmentTimeError: If the new time is outside working hours or
                overlaps with the break time.
            AppointmentOverlappingError: If the new time overlaps with other existing appointments.
        """
        if not schedule.is_active:
            raise ScheduleIsNotActiveError(
                status_code=409,
                detail=_("Associated schedule is inactive or not found."),
            )

        appointment_interval_minutes = schedule.appointment_interval
        appointment_start_datetime = datetime.combine(schedule_day.date, new_time)
        appointment_end_datetime = appointment_start_datetime + timedelta(
            minutes=appointment_interval_minutes
        )

        self._validate_appointment_within_working_hours(
            appointment_start_datetime,
            appointment_end_datetime,
            schedule_day,
            appointment_interval_minutes,
            new_time,
        )

        if schedule_day.break_start_time and schedule_day.break_end_time:
            break_start_datetime = datetime.combine(
                schedule_day.date, schedule_day.break_start_time
            )
            break_end_datetime = datetime.combine(
                schedule_day.date, schedule_day.break_end_time
            )
            if (appointment_start_datetime < break_end_datetime) and (
                appointment_end_datetime > break_start_datetime
            ):
                raise InvalidAppointmentTimeError(
                    status_code=409,
                    detail=_("The appointment cannot overlap with the break time."),
                )

        existing_appointments = (
            await self._appointment_repository.get_appointments_by_day_id(
                schedule_day_id
            )
        )
        self._check_appointment_overlapping(
            appointment_start_datetime,
            appointment_end_datetime,
            existing_appointments,
            schedule_day.date,
            appointment_interval_minutes,
            current_appointment_id=current_appointment_id,
        )

    async def _validate_patient_and_support(
        self,
        doctor: UserDomain,
        patient_id: Optional[UUID] = None,
    ) -> Optional[PatientDomain]:
        if not patient_id:
            return None

        patient = await self._patients_service.get_by_id(patient_id)
        determined_patient_type = (
            AppointmentPatientTypeEnum.ADULT.value
            if patient.is_adult()
            else AppointmentPatientTypeEnum.CHILD.value
        )

        self._check_doctor_support(
            determined_patient_type,
            doctor,
            "served_patient_types",
            "The specialist does not support the provided patient type.",
        )

        return patient

    @staticmethod
    def __update_status_logic(
        appointment: AppointmentDomain,
        new_status: AppointmentStatusEnum,
        old_status: AppointmentStatusEnum,
        schedule: ScheduleDomain,
        schedule_day: ResponseScheduleDaySchema,
    ) -> None:
        """
        Updates the appointment status based on the new status and executes associated business logic.

        This method handles the transition of the appointment status, applying specific
        behaviors when changing to 'CANCELLED' or 'BOOKED' statuses. For other statuses,
        it simply updates the status field directly.

        Specifically:
          - If the new status is 'CANCELLED' and differs from the old status, the appointment's
            cancel() method is called, which updates status and cancellation timestamp.
          - If the new status is 'BOOKED' and differs from the old status, the appointment's
            book() method is called, which validates schedule and schedule day activity
            before updating the status.
          - For any other new status (not 'CANCELLED' or 'BOOKED'), the status is updated
            directly without invoking domain methods.

        Args:
            appointment (AppointmentDomain): The appointment domain object to update.
            new_status (AppointmentStatusEnum): The new status to apply.
            old_status (AppointmentStatusEnum): The current status before update.
            schedule (ScheduleDomain): The schedule associated with the appointment.
            schedule_day (ResponseScheduleDaySchema): The schedule day details for validation.

        Raises:
            ScheduleIsNotActiveError: If the schedule is inactive during booking.
            ScheduleDayIsNotActiveError: If the schedule day is inactive during booking.
        """
        if new_status and new_status not in (
            AppointmentStatusEnum.CANCELLED,
            AppointmentStatusEnum.BOOKED,
        ):
            appointment.status = new_status

        if (
            new_status == AppointmentStatusEnum.CANCELLED
            and old_status != AppointmentStatusEnum.CANCELLED
        ):
            appointment.cancel()
        elif (
            new_status == AppointmentStatusEnum.BOOKED
            and old_status != AppointmentStatusEnum.BOOKED
        ):
            try:
                appointment.book(schedule, schedule_day)
            except ScheduleIsNotActiveError as err:
                raise ScheduleIsNotActiveError(
                    status_code=409,
                    detail=_("Associated schedule is inactive or not found."),
                ) from err
            except ScheduleDayIsNotActiveErrorDomain as err:
                raise ScheduleDayIsNotActiveError(
                    status_code=409,
                    detail=_("Associated schedule day is inactive or not found."),
                ) from err

    async def get_by_id(
        self, appointment_id: int
    ) -> Tuple[AppointmentDomain, Optional[PatientDomain], UserDomain, time, date]:
        appointment = self._check_appointment_exists(
            await self._appointment_repository.get_by_id(appointment_id),
            appointment_id,
        )

        schedule = self._check_schedule_exists(
            await self._schedule_repository.get_schedule_by_day_id(
                appointment.schedule_day_id
            ),
            appointment.schedule_day_id,
        )

        schedule_day = self._check_schedule_day_exists(
            await self._schedule_day_repository.get_by_id(appointment.schedule_day_id),
            appointment.schedule_day_id,
        )

        doctor: UserDomain = await self._user_service.get_by_id(schedule.doctor_id)
        patient = (
            await self._patients_service.get_by_id(appointment.patient_id)
            if appointment.patient_id
            else None
        )

        appointment_date: date = schedule_day.date

        appointment_end_datetime = self.__add_interval(
            appointment_date, appointment.time, schedule.appointment_interval
        )
        appointment_end_time = appointment_end_datetime.time()

        return appointment, patient, doctor, appointment_end_time, appointment_date

    async def get_appointments(
        self,
        filter_params: AppointmentFilterParams,
        pagination_params: PaginationParams,
    ) -> Tuple[
        List[Tuple[AppointmentDomain, Optional[PatientDomain], UserDomain, time, date]],
        int,
    ]:
        filters_dict = filter_params.to_dict(exclude_none=True)
        appointments = await self._appointment_repository.get_appointments(
            filters=filters_dict,
            limit=pagination_params.limit,
            page=pagination_params.page,
        )

        total_amount_of_records = (
            await self._appointment_repository.get_total_number_of_appointments()
        )

        if not appointments:
            return [], total_amount_of_records

        patient_ids = {
            appointment.patient_id
            for appointment in appointments
            if appointment.patient_id
        }
        schedule_day_ids = {appointment.schedule_day_id for appointment in appointments}

        patients_map = await self._load_entities_by_ids(
            patient_ids, self._patients_service.get_by_id
        )
        schedule_days_map = await self._load_entities_by_ids(
            schedule_day_ids, self._schedule_day_repository.get_by_id
        )

        schedule_ids = {
            schedule_day.schedule_id for schedule_day in schedule_days_map.values()
        }
        schedules_map = await self._load_entities_by_ids(
            schedule_ids, self._schedule_repository.get_by_id
        )

        doctor_ids = {
            schedule.doctor_id
            for schedule in schedules_map.values()
            if schedule.doctor_id
        }
        doctors_map = await self._load_entities_by_ids(
            doctor_ids, self._user_repository.get_by_id
        )

        filtered_results = []
        for appointment in appointments:
            patient = patients_map.get(appointment.patient_id)
            schedule_day = schedule_days_map.get(appointment.schedule_day_id)
            schedule = schedule_day and schedules_map.get(schedule_day.schedule_id)

            if not self._appointment_passes_filters(
                patient, schedule_day, schedule, doctors_map, filter_params
            ):
                continue

            end_datetime = self.__add_interval(
                schedule_day.date, appointment.time, schedule.appointment_interval
            )
            end_time = end_datetime.time()

            doctor = schedule and doctors_map.get(schedule.doctor_id)

            filtered_results.append(
                (appointment, patient, doctor, end_time, schedule_day.date)
            )

        return filtered_results, total_amount_of_records

    async def create_appointment(
        self, schedule_day_id: UUID, schema: CreateAppointmentSchema
    ) -> Tuple[AppointmentDomain, Optional[PatientDomain], UserDomain, time, date]:
        schedule_day = self._check_schedule_day_exists(
            await self._schedule_day_repository.get_by_id(schedule_day_id),
            schedule_day_id,
        )

        schedule = self._check_schedule_exists(
            await self._schedule_repository.get_schedule_by_day_id(schedule_day_id),
            schedule_day_id,
        )
        if not schedule.is_active:
            raise ScheduleIsNotActiveError(
                status_code=409,
                detail=_("Associated schedule is inactive or not found."),
            )

        doctor = await self._user_service.get_by_id(schedule.doctor_id)

        # Check that provided patient exist and doctor supports his type (adult or child etc.)
        await self._validate_patient_and_support(
            patient_id=schema.patient_id, doctor=doctor
        )

        if schema.referral_type:
            AppointmentService._check_doctor_support(
                schema.referral_type,
                doctor,
                "served_referral_types",
                "The specialist does not support the referral type.",
            )
        if schema.referral_origin:
            AppointmentService._check_doctor_support(
                schema.referral_origin,
                doctor,
                "served_referral_origins",
                "The specialist does not support the referral origin type.",
            )

        # Check that all provided financing sources IDs exist
        if schema.financing_sources_ids:
            await self._validate_financing_sources(schema.financing_sources_ids)

        # Check that all provided financing sources IDs INSIDE additional_services exist
        if schema.additional_services:
            await self._validate_additional_services(schema.additional_services)

        if not schedule_day.is_active:
            raise ScheduleIsNotActiveError(
                status_code=409,
                detail=_("Schedule day %(id)s is inactive.") % {"id": schedule_day_id},
            )

        await self._validate_time_change(
            schedule_day_id=schedule_day_id,
            schedule_day=schedule_day,
            schedule=schedule,
            new_time=schema.time,
        )

        appointment = map_appointment_create_schema_to_domain(schema, schedule_day_id)

        # Validate appointment status. If chosen as 'booked' -> 'patient_id' must be None etc.
        self.__validate_appointment_status(appointment)

        async with self._uow:
            created_appointment = await self._uow.appointment_repository.add(
                appointment
            )

        patient = (
            await self._patients_service.get_by_id(schema.patient_id)
            if schema.patient_id
            else None
        )

        appointment_interval = timedelta(minutes=schedule.appointment_interval)
        created_appointment_end_datetime = (
            datetime.combine(schedule_day.date, created_appointment.time)
            + appointment_interval
        )

        return (
            created_appointment,
            patient,
            doctor,
            created_appointment_end_datetime.time(),
            schedule_day.date,
        )

    async def update_appointment(
        self, appointment_id: int, schema: UpdateAppointmentSchema
    ) -> Tuple[AppointmentDomain, Optional[PatientDomain], UserDomain, time, date]:
        appointment = self._check_appointment_exists(
            await self._appointment_repository.get_by_id(appointment_id),
            appointment_id,
        )

        schedule_day_id = schema.schedule_day_id or appointment.schedule_day_id
        schedule_day = self._check_schedule_day_exists(
            await self._schedule_day_repository.get_by_id(schedule_day_id),
            schedule_day_id,
        )

        schedule = self._check_schedule_exists(
            await self._schedule_repository.get_schedule_by_day_id(schedule_day_id),
            schedule_day_id,
        )

        doctor = await self._user_service.get_by_id(schedule.doctor_id)

        # Check that provided patient exists and doctor supports his type ('adult' or 'child' etc.)
        await self._validate_patient_and_support(
            patient_id=schema.patient_id, doctor=doctor
        )

        if schema.referral_type:
            self._check_doctor_support(
                schema.referral_type,
                doctor,
                "served_referral_types",
                "The specialist does not support the referral type.",
            )
        if schema.referral_origin:
            self._check_doctor_support(
                schema.referral_origin,
                doctor,
                "served_referral_origins",
                "The specialist does not support the referral origin type.",
            )

        # Check that all provided financing sources IDs exist
        if schema.financing_sources_ids is not None:
            await self._validate_financing_sources(schema.financing_sources_ids)

        # Check that all provided financing sources IDs INSIDE additional_services exist
        if schema.additional_services is not None:
            await self._validate_additional_services(schema.additional_services)

        day_changed = bool(
            schema.schedule_day_id
            and schema.schedule_day_id != appointment.schedule_day_id
        )
        time_changed = bool(schema.time and schema.time != appointment.time)

        if day_changed or time_changed:
            new_appointment_time = schema.time or appointment.time
            await self._validate_time_change(
                schedule_day_id=schedule_day_id,
                schedule_day=schedule_day,
                schedule=schedule,
                new_time=new_appointment_time,
                current_appointment_id=appointment.id,
            )

            appointment.schedule_day_id = schedule_day_id
            appointment.time = new_appointment_time

        old_status = appointment.status

        appointment = map_appointment_update_schema_to_domain(appointment, schema)

        # Extract new status from schema (if present)
        update_data = schema.model_dump(exclude_unset=True)
        new_status = update_data.get("status")

        # Validate appointment status consistency
        self.__validate_appointment_status(appointment)

        # Update status and apply related business logic
        if "status" in update_data:
            self.__update_status_logic(
                appointment, new_status, old_status, schedule, schedule_day
            )

        async with self._uow:
            updated_appointment = await self._uow.appointment_repository.update(
                appointment
            )

        patient = (
            await self._patients_service.get_by_id(updated_appointment.patient_id)
            if updated_appointment.patient_id
            else None
        )

        end_datetime = self.__add_interval(
            schedule_day.date, updated_appointment.time, schedule.appointment_interval
        )
        end_time = end_datetime.time()
        appointment_date = schedule_day.date

        return updated_appointment, patient, doctor, end_time, appointment_date

    async def delete_by_id(self, appointment_id: int) -> None:
        async with self._uow:
            appointment = await self._uow.appointment_repository.get_by_id(
                appointment_id
            )
            appointment = self._check_appointment_exists(appointment, appointment_id)

            await self._uow.appointment_repository.delete_by_id(appointment.id)
