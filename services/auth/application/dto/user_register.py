from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserRegisterInput:
    username: str
    email: str
    password: str
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None
    telegram: str | None = None


@dataclass(frozen=True, slots=True)
class UserRegisterOutput:
    id: UUID
    username: str
    name: str | None
    surname: str | None
    patronymic: str | None
