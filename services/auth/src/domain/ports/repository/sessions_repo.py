from datetime import datetime
from typing import Protocol
from uuid import UUID

from auth.src.domain.entities.session import UserSession, UserSessions


class IUserSessionsRepository(Protocol):
    async def create(
        self,
        *,
        session_id: UUID,
        user_id: UUID,
        refresh_token_hash: str,
        expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> None:
        pass

    async def fetch_by_refresh_token_hash(
        self,
        *,
        refresh_token_hash: str,
    ) -> UserSession | None:
        pass

    async def fetch_by_user_id(
        self,
        *,
        user_id: UUID,
    ) -> UserSessions:
        pass

    async def update_refresh_token(
        self,
        *,
        session_id: UUID,
        current_refresh_token_hash: str,
        next_refresh_token_hash: str,
        now: datetime,
    ) -> bool:
        pass

    async def revoke_by_id(
        self,
        *,
        session_id: UUID,
        user_id: UUID,
        revoked_at: datetime,
    ) -> None:
        pass
