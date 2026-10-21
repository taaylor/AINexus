from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserProfileInput:
    user_id: UUID


@dataclass(frozen=True, slots=True)
class UserProfileOutput:
    id: UUID
    username: str
    name: str | None
    surname: str | None
    patronymic: str | None
    avatar_key: str | None
    email: str
    telegram: str | None
    is_verified_email: bool
