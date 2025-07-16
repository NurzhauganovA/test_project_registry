class DomainError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


# AppointmentDomain errors
class AppointmentError(DomainError):
    pass


class AppointmentIsNotAvailableError(AppointmentError):
    pass


class InvalidAppointmentStatusDomainError(AppointmentError):
    pass


# ScheduleDomain errors
class ScheduleError(DomainError):
    pass


class InvalidAppointmentIntervalError(ScheduleError):
    pass


class ScheduleValidationError(ScheduleError):
    pass


class ScheduleDayIsNotActiveError(ScheduleError):
    pass


class ScheduleIsNotActiveError(DomainError):
    pass


class InvalidWorkTimeError(ScheduleError):
    pass


class InvalidBreakTimeError(ScheduleError):
    pass
