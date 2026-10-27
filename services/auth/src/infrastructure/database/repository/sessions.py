from datetime import datetime
from uuid import UUID

from sqlalchemy import func, insert, literal, or_, select, union_all, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.src.domain.entities.session import UserSession, UserSessions, UserSessionSummary
from auth.src.domain.ports.repository.sessions_repo import IUserSessionsRepository
from auth.src.infrastructure.database.models import UserSessionModel


class UserSessionsRepository(IUserSessionsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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
        """Create a user session.

        SQL:

        INSERT INTO auth.user_sessions
        (
            id,
            user_id,
            refresh_token,
            expires_at,
            user_agent,
            ip_address
        )
        VALUES
        (
            :session_id,
            :user_id,
            :refresh_token_hash,
            :expires_at,
            :user_agent,
            :ip_address
        );
        """
        stmt = insert(UserSessionModel).values(
            id=session_id,
            user_id=user_id,
            refresh_token=refresh_token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await self._session.execute(stmt)

    async def fetch_by_refresh_token_hash(
        self,
        *,
        refresh_token_hash: str,
    ) -> UserSession | None:
        """Fetch a session by its current refresh token hash.

        SQL:

        SELECT
            us.id,
            us.user_id,
            us.expires_at,
            us.revoked_at,
            us.user_agent,
            us.ip_address
        FROM auth.user_sessions AS us
        WHERE us.refresh_token = :refresh_token_hash;
        """
        stmt = select(
            UserSessionModel.id,
            UserSessionModel.user_id,
            UserSessionModel.expires_at,
            UserSessionModel.revoked_at,
            UserSessionModel.user_agent,
            UserSessionModel.ip_address,
        ).where(UserSessionModel.refresh_token == refresh_token_hash)

        result = (await self._session.execute(stmt)).one_or_none()

        if result is None:
            return None

        return UserSession(
            id=result.id,
            user_id=result.user_id,
            expires_at=result.expires_at,
            revoked_at=result.revoked_at,
            user_agent=result.user_agent,
            ip_address=result.ip_address,
        )

    async def fetch_by_user_id(
        self,
        *,
        user_id: UUID,
    ) -> UserSessions:
        """Fetch all active sessions and the most recently created inactive sessions.

        SQL:

        WITH inactive_sessions AS (
            SELECT
                id,
                user_agent,
                ip_address,
                created_at,
                FALSE AS is_active
            FROM auth.user_sessions
            WHERE user_id = :user_id
              AND (revoked_at IS NOT NULL OR expires_at <= NOW())
            ORDER BY created_at DESC, id DESC
            LIMIT 5
        ), sessions AS (
            SELECT
                id,
                user_agent,
                ip_address,
                created_at,
                TRUE AS is_active
            FROM auth.user_sessions
            WHERE user_id = :user_id
              AND revoked_at IS NULL
              AND expires_at > NOW()
            UNION ALL
            SELECT * FROM inactive_sessions
        )
        SELECT id, user_agent, ip_address, is_active
        FROM sessions
        ORDER BY is_active DESC, created_at DESC, id DESC;
        """
        inactive = (
            select(
                UserSessionModel.id,
                UserSessionModel.user_agent,
                UserSessionModel.ip_address,
                UserSessionModel.created_at,
                literal(False).label("is_active"),
            )
            .where(
                UserSessionModel.user_id == user_id,
                or_(
                    UserSessionModel.revoked_at.is_not(None),
                    UserSessionModel.expires_at <= func.now(),
                ),
            )
            .order_by(UserSessionModel.created_at.desc())
            .limit(5)
            .cte("inactive_sessions")
        )

        active = select(
            UserSessionModel.id,
            UserSessionModel.user_agent,
            UserSessionModel.ip_address,
            UserSessionModel.created_at,
            literal(True).label("is_active"),
        ).where(
            UserSessionModel.user_id == user_id,
            UserSessionModel.revoked_at.is_(None),
            UserSessionModel.expires_at > func.now(),
        )

        sbq = union_all(active, select(*inactive.c)).subquery("sessions")

        stmt = select(
            sbq.c.id,
            sbq.c.user_agent,
            sbq.c.ip_address,
            sbq.c.is_active,
        ).order_by(
            sbq.c.is_active.desc(),
            sbq.c.created_at.desc(),
            sbq.c.id.desc(),
        )

        active = []
        inactive = []

        for result in (await self._session.execute(stmt)).all():
            session = UserSessionSummary(
                id=result.id,
                user_agent=result.user_agent,
                ip_address=result.ip_address,
            )

            if result.is_active:
                active.append(session)
            else:
                inactive.append(session)

        return UserSessions(active=active, inactive=inactive)

    async def update_refresh_token(
        self,
        *,
        session_id: UUID,
        current_refresh_token_hash: str,
        next_refresh_token_hash: str,
        now: datetime,
    ) -> bool:
        """Update the refresh token for an active session.

        SQL:

        UPDATE auth.user_sessions
        SET refresh_token = :next_refresh_token_hash
        WHERE id = :session_id
          AND refresh_token = :current_refresh_token_hash
          AND expires_at > :now
          AND revoked_at IS NULL
        RETURNING id;
        """

        stmt = (
            update(UserSessionModel)
            .where(
                UserSessionModel.id == session_id,
                UserSessionModel.refresh_token == current_refresh_token_hash,
                UserSessionModel.expires_at > now,
                UserSessionModel.revoked_at.is_(None),
            )
            .values(refresh_token=next_refresh_token_hash)
            .returning(UserSessionModel.id)
        )
        updated_session_id = (await self._session.execute(stmt)).scalar_one_or_none()
        return updated_session_id is not None

    async def revoke_by_id(
        self,
        *,
        session_id: UUID,
        user_id: UUID,
        revoked_at: datetime,
    ) -> None:
        """Revoke a session owned by the authenticated user.

        SQL:

        UPDATE auth.user_sessions
        SET revoked_at = :revoked_at
        WHERE id = :session_id
          AND user_id = :user_id
          AND revoked_at IS NULL;
        """
        stmt = (
            update(UserSessionModel)
            .where(
                UserSessionModel.id == session_id,
                UserSessionModel.user_id == user_id,
                UserSessionModel.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
        )
        await self._session.execute(stmt)
