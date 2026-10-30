from typing import Final, cast
from uuid import UUID

from uuid_extensions import uuid7

from auth.src.application.dto.user_login import UserLoginInput
from auth.src.common.exceptions import AuthenticationException
from auth.src.domain.entities.tokens import TokenPair, TokenPayload
from auth.src.domain.ports import (
    IHasher,
    ITokenProvider,
    IUnitOfWork,
    IUseCase,
)
from auth.src.domain.ports.repository.sessions_repo import IUserSessionsRepository
from auth.src.domain.ports.repository.users_repo import IUsersRepository
from services.trace.tracer import traced


class UserLoginUseCase(IUseCase[UserLoginInput, TokenPair]):
    __slots__: Final[tuple[str, ...]] = (
        "_unit_of_work",
        "_users_repository",
        "_argon2_hasher",
        "_sha256_hasher",
        "_sessions_repository",
        "_token_provider",
    )

    def __init__(
        self,
        *,
        unit_of_work: IUnitOfWork,
        users_repository: IUsersRepository,
        argon2_hasher: IHasher,
        sha256_hasher: IHasher,
        sessions_repository: IUserSessionsRepository,
        token_provider: ITokenProvider,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._users_repository = users_repository
        self._argon2_hasher = argon2_hasher
        self._sha256_hasher = sha256_hasher
        self._sessions_repository = sessions_repository
        self._token_provider = token_provider

    @traced("auth.user.login")
    async def execute(self, *, input_data: UserLoginInput) -> TokenPair:
        async with self._unit_of_work:
            user = await self._users_repository.fetch_by_login(
                login=input_data.login,
            )

        if user is None or not await self._argon2_hasher.verify(
            string=input_data.password,
            hashed_string=user.password_hash,
        ):
            raise AuthenticationException("Invalid login or password")

        session_id = uuid7()
        token_pair = self._token_provider.create_token_pair(
            payload=TokenPayload(
                id=user.id,
                session_id=cast(UUID, session_id),
                username=user.username,
                is_platform_admin=user.is_platform_admin,
                is_verified_email=user.is_verified_email,
            ),
        )

        refresh_token_hash = await self._sha256_hasher.to_hash(
            string=token_pair.refresh_token,
        )

        async with self._unit_of_work:
            await self._sessions_repository.create(
                session_id=cast(UUID, session_id),
                user_id=user.id,
                refresh_token_hash=refresh_token_hash,
                expires_at=token_pair.refresh_token_expires_at,
                user_agent=input_data.user_agent,
                ip_address=input_data.ip_address,
            )

        return token_pair
