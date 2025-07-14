from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from src.apps.patients.domain.patient import PatientDomain
from src.apps.patients.services.patients_service import PatientService
from src.apps.registry.domain.enums import AppointmentStatusEnum
from src.apps.registry.domain.exceptions import (
    ScheduleDayIsNotActiveError as ScheduleDayIsNotActiveErrorDomain,
)
from src.apps.registry.domain.models.appointment import AppointmentDomain
from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.exceptions import (
    AppointmentOverlappingError,
    InvalidAppointmentInsuranceTypeError,
    InvalidAppointmentTimeError,
    NoInstanceFoundError,
    ScheduleDayIsNotActiveError,
    ScheduleDayNotFoundError,
    ScheduleIsNotActiveError,
)
from src.apps.registry.infrastructure.api.schemas.requests.appointment_schemas import (
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
        user_repository: UserRepositoryInterface,
    ):
        self._uow = uow
        self._logger = logger
        self._appointment_repository = appointment_repository
        self._schedule_repository = schedule_repository
        self._schedule_day_repository = schedule_day_repository
        self._user_service = user_service
        self._patients_service = patients_service
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
    def _check_support(
        obj: Any, doctor: UserDomain, attribute_name: str, error_message: str
    ):
        key = AppointmentService._extract_key(obj)
        served = getattr(doctor, attribute_name, [])
        if key not in served:
            raise InvalidAppointmentInsuranceTypeError(
                status_code=409,
                detail=_(error_message),
            )

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

    async def update_appointment(
        self, appointment_id: int, schema: UpdateAppointmentSchema
    ) -> Tuple[AppointmentDomain, Optional[PatientDomain], UserDomain, time, date]:
        appointment = self._check_appointment_exists(
            await self._appointment_repository.get_by_id(appointment_id),
            appointment_id,
        )

        if schema.patient_id:
            await self._patients_service.get_by_id(schema.patient_id)

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
        if not doctor:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("The specialist with ID: %(ID) not found.")
                % {"ID": schedule.doctor_id},
            )

        if schema.patient_type:
            AppointmentService._check_support(
                schema.patient_type,
                doctor,
                "served_patient_types",
                "The specialist does not support the provided patient type.",
            )
        if schema.referral_type:
            AppointmentService._check_support(
                schema.referral_type,
                doctor,
                "served_referral_types",
                "The specialist does not support the referral type.",
            )
        if schema.referral_origin:
            AppointmentService._check_support(
                schema.referral_origin,
                doctor,
                "served_referral_origins",
                "The specialist does not support the referral origin type.",
            )
        if schema.insurance_type:
            AppointmentService._check_support(
                schema.insurance_type,
                doctor,
                "served_payment_types",
                "The specialist does not support the provided insurance type.",
            )

        day_changed = bool(
            schema.schedule_day_id
            and schema.schedule_day_id != appointment.schedule_day_id
        )
        time_changed = bool(schema.time and schema.time != appointment.time)

        if day_changed or time_changed:
            if not schedule.is_active:
                raise ScheduleIsNotActiveError(
                    status_code=409,
                    detail=_("Associated schedule is inactive or not found."),
                )

            new_appointment_time = schema.time or appointment.time
            appointment_interval_minutes = schedule.appointment_interval
            appointment_start_datetime = datetime.combine(
                schedule_day.date, new_appointment_time
            )
            appointment_end_datetime = appointment_start_datetime + timedelta(
                minutes=appointment_interval_minutes
            )

            self._validate_appointment_within_working_hours(
                appointment_start_datetime,
                appointment_end_datetime,
                schedule_day,
                appointment_interval_minutes,
                schema.time,
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
                current_appointment_id=appointment.id,
            )

            appointment.schedule_day_id = schedule_day_id
            appointment.time = new_appointment_time

        update_data = schema.model_dump(exclude_unset=True)
        old_status = appointment.status

        for attr, val in update_data.items():
            # These attributes should not be updated directly only through specific methods
            if attr in ("status", "cancelled_at"):
                continue

            setattr(appointment, attr, val)

        if "status" in update_data:
            if (
                update_data["status"] == AppointmentStatusEnum.CANCELLED
                and old_status != AppointmentStatusEnum.CANCELLED
            ):
                appointment.cancel()

            elif (
                update_data["status"] == AppointmentStatusEnum.BOOKED
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
        if not doctor:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Doctor with ID: %(ID)s not found.")
                % {"ID": schedule.doctor_id},
            )

        if schema.patient_type:
            AppointmentService._check_support(
                schema.patient_type,
                doctor,
                "served_patient_types",
                "The specialist does not support the provided patient type.",
            )
        if schema.referral_type:
            AppointmentService._check_support(
                schema.referral_type,
                doctor,
                "served_referral_types",
                "The specialist does not support the referral type.",
            )
        if schema.referral_origin:
            AppointmentService._check_support(
                schema.referral_origin,
                doctor,
                "served_referral_origins",
                "The specialist does not support the referral origin type.",
            )
        if schema.insurance_type:
            AppointmentService._check_support(
                schema.insurance_type,
                doctor,
                "served_payment_types",
                "The specialist does not support the provided insurance type.",
            )

        if schema.patient_id:
            await self._patients_service.get_by_id(schema.patient_id)

        if not schedule_day.is_active:
            raise ScheduleIsNotActiveError(
                status_code=409,
                detail=_("Schedule day %(id)s is inactive.") % {"id": schedule_day_id},
            )

        appointment_interval = timedelta(minutes=schedule.appointment_interval)
        appointment_start_datetime = datetime.combine(schedule_day.date, schema.time)
        appointment_end_datetime = appointment_start_datetime + appointment_interval

        self._validate_appointment_within_working_hours(
            appointment_start_datetime,
            appointment_end_datetime,
            schedule_day,
            schedule.appointment_interval,
            schema.time,
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
            schedule.appointment_interval,
        )

        appointment = AppointmentDomain(
            schedule_day_id=schedule_day_id,
            time=schema.time,
            patient_id=schema.patient_id,
            type=schema.type,
            insurance_type=schema.insurance_type,
            reason=schema.reason,
            additional_services=schema.additional_services or {},
        )
        async with self._uow:
            created_appointment = await self._uow.appointment_repository.add(
                appointment
            )

        patient = (
            await self._patients_service.get_by_id(schema.patient_id)
            if schema.patient_id
            else None
        )

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

    async def delete_by_id(self, appointment_id: int) -> None:
        async with self._uow:
            appointment = await self._uow.appointment_repository.get_by_id(
                appointment_id
            )
            if not appointment:
                raise NoInstanceFoundError(
                    status_code=404,
                    detail=_("Appointment with ID: %(ID)s not found.")
                    % {"ID": appointment_id},
                )

            await self._uow.appointment_repository.delete_by_id(appointment_id)
