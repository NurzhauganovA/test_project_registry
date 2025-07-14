from src.shared.exceptions import ApplicationError


class InsuranceInfoInvalidDateError(ApplicationError):
    pass


class InactiveDiagnosisError(ApplicationError):
    pass
