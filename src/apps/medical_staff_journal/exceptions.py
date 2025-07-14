from src.shared.exceptions import ApplicationError


class ApplicationMedicalStaffJournalAppError(ApplicationError):
    origin = "registry"


class NoInstanceFoundError(ApplicationMedicalStaffJournalAppError):
    pass
