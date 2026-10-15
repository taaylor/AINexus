from auth.src.common.exceptions.base import ApplicationException, ConflictException


class ServiceUnavailableException(ApplicationException):
    pass


class AlreadyExistsException(ConflictException, ApplicationException):
    pass


class NotFoundException(ApplicationException):
    pass


class AuthenticationException(ApplicationException):
    pass
