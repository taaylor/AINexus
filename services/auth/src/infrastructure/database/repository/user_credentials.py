from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth.src.domain.entities.user import CreateUserCredentials
from auth.src.domain.ports.repository.user_credentials_repo import (
    IUserCredentialsRepository,
)
from auth.src.infrastructure.database.models import UserCredentialModel


class UserCredentialsRepository(IUserCredentialsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID,
        credentials: CreateUserCredentials,
    ) -> UUID | None:
        """Insert credentials for a user.

        SQL:
        INSERT INTO auth.users_cred
            (id, email, password_hash, telegram, is_verified_email)
        VALUES
            (:user_id, :email, :password_hash, :telegram, FALSE)
        ON CONFLICT DO NOTHING;
        """
        stmt = (
            insert(UserCredentialModel)
            .on_conflict_do_nothing()
            .values(
                id=user_id,
                email=credentials.email,
                password_hash=credentials.password_hash,
                telegram=credentials.telegram,
                is_verified_email=False,
            )
            .returning(UserCredentialModel.id)
        )

        result = (await self._session.execute(stmt)).one_or_none()

        if result is None:
            return None

        return result.id
