from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserListSessionsInput:
    user_id: UUID


@dataclass(frozen=True, slots=True)
class UserSessionOutput:
    id: UUID
    user_agent: str | None
    ip_address: str | None


@dataclass(frozen=True, slots=True)
class UserListSessionsOutput:
    active: list[UserSessionOutput]
    inactive: list[UserSessionOutput]
