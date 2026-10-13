from typing import NoReturn
from uuid import UUID

from sqlalchemy import case, exists, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.entities.user import (
    CreateUser,
    RegisteredUser,
    RegistrationConflicts,
    User,
    UserCred,
)
from auth.domain.ports.repository.users_repo import IUsersRepository
from auth.infrastructure.database.models import UserCredentialModel, UserModel
from auth.infrastructure.database.utils import fetch_constraint_name
from auth.infrastructure.exceptions import UniqueConstraintError


class UsersRepository(IUsersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch_by_id(self, *, user_id: UUID) -> User | None:
        """
        SQL:

        SELECT
            u.*,
            c.*
        FROM auth.users AS u
            JOIN auth.users_cred AS c
            ON c.id = u.id WHERE u.id = :user_id
        """
        stmt = (
            select(UserModel, UserCredentialModel)
            .join(UserCredentialModel, UserModel.id == UserCredentialModel.id)
            .where(UserModel.id == user_id)
        )

        result = (await self._session.execute(stmt)).one_or_none()

        if result is None:
            return None

        user_model, credentials_model = result
        return User(
            id=user_model.id,
            username=user_model.username,
            name=user_model.name,
            surname=user_model.surname,
            patronymic=user_model.patronymic,
            is_platform_admin=user_model.is_platform_admin,
            avatar_key=user_model.avatar_key,
            organization_id=user_model.organization_id,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            cred=UserCred(
                email=credentials_model.email,
                password_hash=credentials_model.password_hash,
                telegram=credentials_model.telegram,
                is_verified_email=credentials_model.is_verified_email,
                created_at=credentials_model.created_at,
                updated_at=credentials_model.updated_at,
            ),
        )

    async def exist_by_username_email(
        self,
        *,
        username: str,
        email: str,
    ) -> RegistrationConflicts:
        """Check username and email in one SQL query.

        SQL:

        SELECT
          CASE WHEN EXISTS (
            SELECT 1
            FROM auth.users
            WHERE username = :username
          )
          THEN TRUE ELSE FALSE END AS username_exists,
          CASE WHEN EXISTS (
            SELECT 1
            FROM auth.users_cred
            WHERE email = :email
          ) THEN TRUE ELSE FALSE END AS email_exists
        """

        username_exists = exists(
            select(1).select_from(UserModel).where(UserModel.username == username)
        )
        email_exists = exists(
            select(1)
            .select_from(UserCredentialModel)
            .where(UserCredentialModel.email == email)
        )
        stmt = select(
            case((username_exists, True), else_=False).label("username_exists"),
            case((email_exists, True), else_=False).label("email_exists"),
        )
        result = (await self._session.execute(stmt)).one()

        return RegistrationConflicts(
            username_exists=result.username_exists,
            email_exists=result.email_exists,
        )

    async def create(self, *, user: CreateUser) -> RegisteredUser:
        """Insert an auth user and return the response fields.

        SQL:

        INSERT INTO auth.users
        (
            username,
            name,
            surname,
            patronymic,
            is_platform_admin,
            organization_id
        )
        VALUES (:username, :name, :surname, :patronymic, FALSE, NULL)
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
                organization_id=None,
            )
            .returning(
                UserModel.id,
                UserModel.username,
                UserModel.name,
                UserModel.surname,
                UserModel.patronymic,
            )
        )

        try:
            result = (await self._session.execute(stmt)).one()

            return RegisteredUser(
                id=result.id,
                username=result.username,
                name=result.name,
                surname=result.surname,
                patronymic=result.patronymic,
            )

        except IntegrityError as exc:
            self._raise_exception(exc)

    def _raise_exception(self, exc: IntegrityError) -> NoReturn:
        constraint_name = fetch_constraint_name(exc)

        match constraint_name:
            case "uq_users_username":
                raise UniqueConstraintError("Username already exists") from exc
            case _:
                raise exc
