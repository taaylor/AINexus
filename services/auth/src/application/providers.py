from typing import Annotated, Any

from dishka import FromComponent, Provider, Scope, provide

from auth.src.application.dto.user import UserProfileInput, UserProfileOutput
from auth.src.application.dto.user_login import UserLoginInput
from auth.src.application.dto.user_register import UserRegisterInput, UserRegisterOutput
from auth.src.application.use_cases.auth.login import UserLoginUseCase
from auth.src.application.use_cases.auth.profile import UserProfileUseCase
from auth.src.application.use_cases.auth.register import UserRegisterUseCase
from auth.src.common.settings import Settings
from auth.src.domain.entities.tokens import TokenPair
from auth.src.domain.ports import (
    IHasher,
    ITokenProvider,
    IUnitOfWork,
    IUseCase,
)
from auth.src.domain.ports.repository.sessions_repo import IUserSessionsRepository
from auth.src.domain.ports.repository.user_credentials_repo import (
    IUserCredentialsRepository,
)
from auth.src.domain.ports.repository.users_repo import IUsersRepository


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

    @provide(
        scope=Scope.REQUEST,
        provides=Annotated[
            IUseCase[UserRegisterInput, UserRegisterOutput],
            FromComponent("user_register"),
        ],
    )
    def user_register_use_case(
        self,
        unit_of_work: IUnitOfWork,
        argon2_hasher: Annotated[IHasher, FromComponent("argon2")],
        users_repository: IUsersRepository,
        user_credentials_repository: IUserCredentialsRepository,
    ) -> UserRegisterUseCase:
        return UserRegisterUseCase(
            unit_of_work=unit_of_work,
            argon2_hasher=argon2_hasher,
            users_repository=users_repository,
            user_credentials_repository=user_credentials_repository,
        )

    @provide(
        scope=Scope.REQUEST,
        provides=Annotated[
            IUseCase[UserLoginInput, TokenPair],
            FromComponent("user_login"),
        ],
    )
    def user_login_use_case(
        self,
        unit_of_work: IUnitOfWork,
        users_repository: IUsersRepository,
        argon2_hasher: Annotated[IHasher, FromComponent("argon2")],
        sha256_hasher: Annotated[IHasher, FromComponent("sha256")],
        sessions_repository: IUserSessionsRepository,
        token_provider: ITokenProvider,
    ) -> UserLoginUseCase:
        return UserLoginUseCase(
            unit_of_work=unit_of_work,
            users_repository=users_repository,
            argon2_hasher=argon2_hasher,
            sha256_hasher=sha256_hasher,
            sessions_repository=sessions_repository,
            token_provider=token_provider,
        )

    @provide(
        scope=Scope.REQUEST,
        provides=Annotated[
            IUseCase[UserProfileInput, UserProfileOutput],
            FromComponent("user_profile"),
        ],
    )
    def user_profile_use_case(
        self,
        users_repository: IUsersRepository,
    ) -> UserProfileUseCase:
        return UserProfileUseCase(users_repository=users_repository)
