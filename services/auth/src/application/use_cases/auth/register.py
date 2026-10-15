from typing import Final

from auth.src.application.dto.user_register import UserRegisterInput, UserRegisterOutput
from auth.src.common.exceptions import AlreadyExistsException
from auth.src.domain.entities.user import CreateUser, CreateUserCredentials
from auth.src.domain.ports import IHasher, IUnitOfWork, IUseCase
from auth.src.domain.ports.repository.user_credentials_repo import (
    IUserCredentialsRepository,
)
from auth.src.domain.ports.repository.users_repo import IUsersRepository


class UserRegisterUseCase(IUseCase[UserRegisterInput, UserRegisterOutput]):
    __slots__: Final[tuple[str, ...]] = (
        "_unit_of_work",
        "_argon2_hasher",
        "_users_repository",
        "_user_credentials_repository",
    )

    def __init__(
        self,
        *,
        unit_of_work: IUnitOfWork,
        argon2_hasher: IHasher,
        users_repository: IUsersRepository,
        user_credentials_repository: IUserCredentialsRepository,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._argon2_hasher = argon2_hasher
        self._users_repository = users_repository
        self._user_credentials_repository = user_credentials_repository

    async def execute(self, *, input_data: UserRegisterInput) -> UserRegisterOutput:
        password_hash = await self._argon2_hasher.to_hash(
            string=input_data.password,
        )

        async with self._unit_of_work:
            user_reg = await self._users_repository.create(
                user=CreateUser(
                    username=input_data.username,
                    name=input_data.name,
                    surname=input_data.surname,
                    patronymic=input_data.patronymic,
                )
            )

            if user_reg is None:
                raise AlreadyExistsException("Username already exists")

            user_cred = await self._user_credentials_repository.create(
                user_id=user_reg.id,
                credentials=CreateUserCredentials(
                    email=input_data.email,
                    password_hash=password_hash,
                    telegram=input_data.telegram,
                ),
            )

            if user_cred is None:
                raise AlreadyExistsException("Email already exists")

        return UserRegisterOutput(
            id=user_reg.id,
            username=user_reg.username,
            name=user_reg.name,
            surname=user_reg.surname,
            patronymic=user_reg.patronymic,
        )
