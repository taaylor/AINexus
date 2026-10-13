from typing import Self
from uuid import UUID

from pydantic import model_validator

from auth.presentation.api.v1.schemes.base import BaseSchema


class UserRegisterInputSchema(BaseSchema):
    username: str
    email: str
    password: str
    password_repeat: str
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None
    telegram: str | None = None

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("password and password_repeat must match")
        return self


class UserRegisterOutputSchema(BaseSchema):
    id: UUID
    username: str
    name: str | None
    surname: str | None
    patronymic: str | None
