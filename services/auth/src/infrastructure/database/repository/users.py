from uuid import UUID

from sqlalchemy import case, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth.src.domain.entities.user import (
    CreateUser,
    RegisteredUser,
    UserLogin,
    UserProfile,
)
from auth.src.domain.ports.repository.users_repo import IUsersRepository
from auth.src.infrastructure.database.models import UserCredentialModel, UserModel


class UsersRepository(IUsersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch_by_login(self, *, login: str) -> UserLogin | None:
        """Fetch login credentials by username or email.

        SQL:

        SELECT
            u.id,
            u.username,
            u.is_platform_admin,
            c.password_hash,
            c.is_verified_email
        FROM auth.users AS u
            JOIN auth.users_cred AS c ON c.id = u.id
        WHERE u.username = :login OR c.email = :login
        ORDER BY CASE WHEN u.username = :login THEN 0 ELSE 1 END
        LIMIT 1
        """
        stmt = (
            select(
                UserModel.id,
                UserModel.username,
                UserModel.is_platform_admin,
                UserCredentialModel.password_hash,
                UserCredentialModel.is_verified_email,
            )
            .join(UserCredentialModel, UserModel.id == UserCredentialModel.id)
            .where((UserModel.username == login) | (UserCredentialModel.email == login))
            .order_by(case((UserModel.username == login, 0), else_=1))
            .limit(1)
        )

        result = (await self._session.execute(stmt)).one_or_none()
        if result is None:
            return None

        return UserLogin(
            id=result.id,
            username=result.username,
            password_hash=result.password_hash,
            is_platform_admin=result.is_platform_admin,
            is_verified_email=result.is_verified_email,
        )

    async def fetch_by_id_profile(self, *, user_id: UUID) -> UserProfile | None:
        """
        SQL:

        SELECT
            u.id,
            u.username,
            u.name,
            u.surname,
            u.patronymic,
            u.avatar_key,
            c.email,
            c.telegram,
            c.is_verified_email
        FROM auth.users AS u
            JOIN auth.users_cred AS c
            ON c.id = u.id WHERE u.id = :user_id
        """
        stmt = (
            select(
                UserModel.id,
                UserModel.username,
                UserModel.name,
                UserModel.surname,
                UserModel.patronymic,
                UserModel.avatar_key,
                UserCredentialModel.email,
                UserCredentialModel.telegram,
                UserCredentialModel.is_verified_email,
            )
            .join(UserCredentialModel, UserModel.id == UserCredentialModel.id)
            .where(UserModel.id == user_id)
        )

        result = (await self._session.execute(stmt)).one_or_none()

        if result is None:
            return None

        return UserProfile(
            id=result.id,
            username=result.username,
            name=result.name,
            surname=result.surname,
            patronymic=result.patronymic,
            avatar_key=result.avatar_key,
            email=result.email,
            telegram=result.telegram,
            is_verified_email=result.is_verified_email,
        )

    async def create(self, *, user: CreateUser) -> RegisteredUser | None:
        """Insert an auth user and return the response fields.

        SQL:

        INSERT INTO auth.users
        (
            username,
            name,
            surname,
            patronymic,
            is_platform_admin
        )
        VALUES (:username, :name, :surname, :patronymic, FALSE)
        ON CONFLICT DO NOTHING
        RETURNING id, username, name, surname, patronymic
        """
        stmt = (
            insert(UserModel)
            .values(
                username=user.username,
                name=user.name,
                surname=user.surname,
                patronymic=user.patronymic,
                is_platform_admin=False,
            )
            .on_conflict_do_nothing(index_elements=["username"])
            .returning(
                UserModel.id,
                UserModel.username,
                UserModel.name,
                UserModel.surname,
                UserModel.patronymic,
            )
        )

        result = (await self._session.execute(stmt)).one_or_none()

        if result is None:
            return None

        return RegisteredUser(
            id=result.id,
            username=result.username,
            name=result.name,
            surname=result.surname,
            patronymic=result.patronymic,
        )
