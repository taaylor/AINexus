from pydantic_core import ErrorDetails

from auth.common.exceptions.base import PresenterException


class DTOValidationException(PresenterException):
    def __init__(self, errors: list[ErrorDetails]) -> None:
        self.errors = errors
        super().__init__("Input data is invalid")
