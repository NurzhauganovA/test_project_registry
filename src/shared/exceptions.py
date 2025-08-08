class ApplicationError(Exception):
    def __init__(
        self,
        detail: str,
        status_code: int,
    ):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)


class NoInstanceFoundError(ApplicationError):
    pass


class InstanceAlreadyExistsError(ApplicationError):
    pass


class DeleteRestrictedError(ApplicationError):
    pass


class InvalidActionTypeError(ApplicationError):
    pass


class InfrastructureError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


class UniqueViolationError(Exception):
    """Custom exception to signal duplicate key violation in the repository layer."""

    pass


class MapperError(InfrastructureError):
    """Basic mapper error"""

    pass


class AuthServiceError(InfrastructureError):
    def __init__(self, detail: str, status_code: int):
        self.status_code = status_code
        super().__init__(detail)


class AuthServiceConnectionError(AuthServiceError):
    pass


class RpnIntegrationServiceError(InfrastructureError):
    def __init__(self, detail: str, status_code: int):
        self.status_code = status_code
        super().__init__(detail)


class RpnIntegrationServiceConnectionError(RpnIntegrationServiceError):
    pass


class DependencyError(Exception):
    def __init__(
        self,
        detail: str,
        status_code: int,
    ):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)


class AccessDeniedError(DependencyError):
    pass


class InvalidPaginationParamsError(Exception):
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class DomainValidationError(Exception):
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class ValidationError(DomainValidationError):
    """Custom exception to signal validation errors in domain models."""

    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail, status_code)