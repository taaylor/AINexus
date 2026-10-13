from auth.common.exceptions.base import ApplicationException, ConflictException


class ServiceUnavailableException(ApplicationException):
    pass


class UserAlreadyExistsException(ConflictException, ApplicationException):
    pass
