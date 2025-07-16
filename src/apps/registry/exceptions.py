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


class UserRoleIsNotSchedulableError(ApplicationRegistryAppError):
    """
    Raised when a user does not have any roles that allow schedule creation.

    This exception is thrown during scheduling operations when none of the user's assigned roles
    are found in the list of roles allowed for schedule assignment, as specified by the
    `SCHEDULABLE_USER_ROLES` environment variable.

    Typical usage: Raise this error to explicitly block scheduling for users whose roles do not
    permit such operations, providing a clear and actionable reason for the failure.
    """

    pass


class InvalidAppointmentTimeError(ApplicationRegistryAppError):
    pass


class InvalidAppointmentStatusError(ApplicationRegistryAppError):
    pass


class AppointmentOverlappingError(ApplicationRegistryAppError):
    pass


class InvalidAppointmentInsuranceTypeError(ApplicationRegistryAppError):
    pass


class BreakTimeConflictError(ApplicationRegistryAppError):
    pass
