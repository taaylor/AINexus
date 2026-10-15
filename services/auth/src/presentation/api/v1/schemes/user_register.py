from typing import Self
from uuid import UUID

from pydantic import Field, model_validator

from auth.src.presentation.api.v1.schemes.base import BaseSchema


class UserRegisterInputSchema(BaseSchema):
    username: str = Field(min_length=4, max_length=30)
    email: str = Field(
        min_length=5,
        max_length=100,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        examples=["mymail@gmail.com"],
    )
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
