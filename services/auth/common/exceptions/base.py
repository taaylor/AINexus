class AppException(Exception):
    def __init__(self, message: str | None = None) -> None:
        self.message = message
        super().__init__(message)


class DomainException(AppException):
    pass


class ApplicationException(AppException):
    pass


class InfrastructureException(AppException):
    pass


class ConflictException(AppException):
    pass


class PresenterException(AppException):
    pass
