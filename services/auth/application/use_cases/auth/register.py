from typing import Final

from auth.application.dto.user_register import UserRegisterInput, UserRegisterOutput
from auth.common.exceptions.application import UserAlreadyExistsException
from auth.domain.entities.user import CreateUser, CreateUserCredentials
from auth.domain.ports import IHasher, IUnitOfWork, IUseCase
from auth.domain.ports.repository.user_credentials_repo import (
    IUserCredentialsRepository,
)
from auth.domain.ports.repository.users_repo import IUsersRepository


class UserRegisterUseCase(IUseCase[UserRegisterInput, UserRegisterOutput]):
    __slots__: Final[tuple[str, ...]] = (
        "_unit_of_work",
        "_password_hasher",
        "_users_repository",
        "_user_credentials_repository",
    )

    def __init__(
        self,
        *,
        unit_of_work: IUnitOfWork,
        password_hasher: IHasher,
        users_repository: IUsersRepository,
        user_credentials_repository: IUserCredentialsRepository,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher
        self._users_repository = users_repository
        self._user_credentials_repository = user_credentials_repository

    async def execute(self, *, input_data: UserRegisterInput) -> UserRegisterOutput:
        async with self._unit_of_work:
            conflicts = await self._users_repository.exist_by_username_email(
                username=input_data.username,
                email=input_data.email,
            )

        if conflicts.username_exists or conflicts.email_exists:
            raise UserAlreadyExistsException("Registration data already exists")

        password_hash = await self._password_hasher.to_hash(
            string=input_data.password,
        )

        async with self._unit_of_work:
            registered_user = await self._users_repository.create(
                user=CreateUser(
                    username=input_data.username,
                    name=input_data.name,
                    surname=input_data.surname,
                    patronymic=input_data.patronymic,
                )
            )
            await self._user_credentials_repository.create(
                user_id=registered_user.id,
                credentials=CreateUserCredentials(
                    email=input_data.email,
                    password_hash=password_hash,
                    telegram=input_data.telegram,
                ),
            )

        return UserRegisterOutput(
            id=registered_user.id,
            username=registered_user.username,
            name=registered_user.name,
            surname=registered_user.surname,
            patronymic=registered_user.patronymic,
        )
