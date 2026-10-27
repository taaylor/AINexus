from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserSession:
    id: UUID
    user_id: UUID
    expires_at: datetime
    revoked_at: datetime | None
    user_agent: str | None
    ip_address: str | None


@dataclass(frozen=True, slots=True)
class UserSessionSummary:
    id: UUID
    user_agent: str | None
    ip_address: str | None


@dataclass(frozen=True, slots=True)
class UserSessions:
    active: list[UserSessionSummary]
    inactive: list[UserSessionSummary]
