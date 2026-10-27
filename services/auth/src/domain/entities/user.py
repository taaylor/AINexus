from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserCred:
    email: str
    password_hash: str
    telegram: str | None
    is_verified_email: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class User:
    id: UUID
    username: str
    name: str | None
    surname: str | None
    patronymic: str | None
    is_platform_admin: bool
    avatar_key: str | None
    created_at: datetime
    updated_at: datetime
    cred: UserCred


@dataclass(frozen=True, slots=True)
class CreateUser:
    username: str
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None


@dataclass(frozen=True, slots=True)
class CreateUserCredentials:
    email: str
    password_hash: str
    telegram: str | None = None


@dataclass(frozen=True, slots=True)
class RegisteredUser:
    id: UUID
    username: str
    name: str | None
    surname: str | None
    patronymic: str | None


@dataclass(frozen=True, slots=True)
class UserProfile:
    id: UUID
    username: str
    name: str | None
    surname: str | None
    patronymic: str | None
    avatar_key: str | None
    email: str
    telegram: str | None
    is_verified_email: bool


@dataclass(frozen=True, slots=True)
class UserLogin:
    id: UUID
    username: str
    password_hash: str
    is_platform_admin: bool
    is_verified_email: bool


@dataclass(frozen=True, slots=True)
class UserTokenData:
    id: UUID
    username: str
    is_platform_admin: bool
    is_verified_email: bool
