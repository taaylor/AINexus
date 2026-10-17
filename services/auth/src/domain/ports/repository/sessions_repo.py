from datetime import datetime
from typing import Protocol
from uuid import UUID


class IUserSessionsRepository(Protocol):
    async def create(
        self,
        *,
        user_id: UUID,
        refresh_token_hash: str,
        expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> None:
        pass
