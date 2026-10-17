from auth.src.common.exceptions.base import ConflictException, InfrastructureException


class UniqueConstraintError(ConflictException, InfrastructureException):
    pass


class InfrastructureUnavailableException(InfrastructureException):
    pass
