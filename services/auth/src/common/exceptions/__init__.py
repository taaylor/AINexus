from auth.src.common.exceptions.application import (
    AlreadyExistsException,
    AuthenticationException,
    NotFoundException,
    ServiceUnavailableException,
)
from auth.src.common.exceptions.base import (
    AppException,
    ApplicationException,
    ConflictException,
    DomainException,
    InfrastructureException,
    PresenterException,
)
from auth.src.common.exceptions.infrastructure import (
    InfrastructureUnavailableException,
    UniqueConstraintError,
)
from auth.src.common.exceptions.presenter import DTOValidationException

__all__ = [
    "AppException",
    "ApplicationException",
    "ConflictException",
    "DTOValidationException",
    "DomainException",
    "InfrastructureException",
    "InfrastructureUnavailableException",
    "NotFoundException",
    "PresenterException",
    "AlreadyExistsException",
    "AuthenticationException",
    "ServiceUnavailableException",
    "UniqueConstraintError",
]
