from typing import Any

from dishka import Provider, Scope, provide

from auth.application.use_cases.auth.register import UserRegisterUseCase
from auth.common.settings import Settings
from auth.domain.ports import IHasher, IUnitOfWork
from auth.domain.ports.repository.user_credentials_repo import (
    IUserCredentialsRepository,
)
from auth.domain.ports.repository.users_repo import IUsersRepository


class ApplicationProvider(Provider):
    def __init__(
        self,
        settings: Settings,
        *,
        scope: Any | None = None,
        component: Any | None = None,
        when: Any | None = None,
    ):
        super().__init__(scope, component, when)
        self.settings = settings

    @provide(scope=Scope.REQUEST)
    def user_register_use_case(
        self,
        unit_of_work: IUnitOfWork,
        password_hasher: IHasher,
        users_repository: IUsersRepository,
        user_credentials_repository: IUserCredentialsRepository,
    ) -> UserRegisterUseCase:
        return UserRegisterUseCase(
            unit_of_work=unit_of_work,
            password_hasher=password_hasher,
            users_repository=users_repository,
            user_credentials_repository=user_credentials_repository,
        )
