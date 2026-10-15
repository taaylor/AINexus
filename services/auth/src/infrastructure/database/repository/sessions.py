from datetime import datetime
from uuid import UUID

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth.src.domain.ports.repository.sessions_repo import IUserSessionsRepository
from auth.src.infrastructure.database.models import UserSessionModel


class UserSessionsRepository(IUserSessionsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID,
        refresh_token_hash: str,
        expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> None:
        stmt = insert(UserSessionModel).values(
            user_id=user_id,
            refresh_token=refresh_token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await self._session.execute(stmt)
