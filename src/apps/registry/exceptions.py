from src.shared.exceptions import ApplicationError


class ApplicationRegistryAppError(ApplicationError):
    origin = "registry"


class ScheduleOverlappingError(ApplicationRegistryAppError):
    pass


class NoInstanceFoundError(ApplicationRegistryAppError):
    pass


class ScheduleNameIsAlreadyTakenError(ApplicationRegistryAppError):
    pass


class ScheduleExceedsMaxAllowedPeriod(ApplicationRegistryAppError):
    pass


class ScheduleInvalidUpdateDatesError(ApplicationRegistryAppError):
    pass


class ScheduleDayNotFoundError(ApplicationRegistryAppError):
    pass


class ScheduleDayIsNotActiveError(ApplicationRegistryAppError):
    pass


class ScheduleIsNotActiveError(ApplicationRegistryAppError):
    pass


class InvalidAppointmentTimeError(ApplicationRegistryAppError):
    pass


class AppointmentOverlappingError(ApplicationRegistryAppError):
    pass


class InvalidAppointmentInsuranceTypeError(ApplicationRegistryAppError):
    pass


class BreakTimeConflictError(ApplicationRegistryAppError):
    pass
