from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserLogoutInput:
    session_id: UUID
    user_id: UUID
