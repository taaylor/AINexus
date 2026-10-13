from typing import NoReturn
from uuid import UUID

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.entities.user import CreateUserCredentials
from auth.domain.ports.repository.user_credentials_repo import (
    IUserCredentialsRepository,
)
from auth.infrastructure.database.models import UserCredentialModel
from auth.infrastructure.database.utils import fetch_constraint_name
from auth.infrastructure.exceptions import UniqueConstraintError


class UserCredentialsRepository(IUserCredentialsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID,
        credentials: CreateUserCredentials,
    ) -> None:
        """Insert credentials for a user.

        SQL:
        INSERT INTO auth.users_cred
            (id, email, password_hash, telegram, is_verified_email)
        VALUES
            (:user_id, :email, :password_hash, :telegram, FALSE).
        """
        stmt = insert(UserCredentialModel).values(
            id=user_id,
            email=credentials.email,
            password_hash=credentials.password_hash,
            telegram=credentials.telegram,
            is_verified_email=False,
        )
        try:
            await self._session.execute(stmt)
        except IntegrityError as exc:
            self._raise_exception(exc)

    def _raise_exception(self, exc: IntegrityError) -> NoReturn:
        constraint_name = fetch_constraint_name(exc)

        match constraint_name:
            case "uq_users_cred_email":
                raise UniqueConstraintError("Email already exists") from exc
            case _:
                raise exc
