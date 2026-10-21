from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TokenPayload:
    id: UUID
    session_id: UUID
    username: str
    is_platform_admin: bool
    is_verified_email: bool


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_token_expires_at: datetime
