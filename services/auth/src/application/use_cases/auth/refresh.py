from typing import Final

from auth.src.application.dto.user_refresh import UserRefreshInput
from auth.src.common.exceptions import AuthenticationException
from auth.src.common.utils import datetime_with_tz
from auth.src.domain.entities.tokens import TokenPair, TokenPayload
from auth.src.domain.ports import IHasher, ITokenProvider, IUnitOfWork, IUseCase
from auth.src.domain.ports.repository.sessions_repo import IUserSessionsRepository
from auth.src.domain.ports.repository.users_repo import IUsersRepository


class UserRefreshUseCase(IUseCase[UserRefreshInput, TokenPair]):
    __slots__: Final[tuple[str, ...]] = (
        "_unit_of_work",
        "_sha256_hasher",
        "_sessions_repository",
        "_users_repository",
        "_token_provider",
    )

    def __init__(
        self,
        *,
        unit_of_work: IUnitOfWork,
        sha256_hasher: IHasher,
        sessions_repository: IUserSessionsRepository,
        users_repository: IUsersRepository,
        token_provider: ITokenProvider,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._sha256_hasher = sha256_hasher
        self._sessions_repository = sessions_repository
        self._users_repository = users_repository
        self._token_provider = token_provider

    async def execute(self, *, input_data: UserRefreshInput) -> TokenPair:
        refresh_token_hash = await self._sha256_hasher.to_hash(
            string=input_data.refresh_token,
        )

        async with self._unit_of_work:
            session = await self._sessions_repository.fetch_by_refresh_token_hash(
                refresh_token_hash=refresh_token_hash,
            )
            if session is None or session.revoked_at is not None:
                raise AuthenticationException("Invalid or expired refresh token")

            user = await self._users_repository.fetch_by_id_token_data(
                user_id=session.user_id,
            )
            if user is None:
                raise AuthenticationException("Invalid or expired refresh token")

            token_pair = self._token_provider.create_token_pair(
                payload=TokenPayload(
                    id=user.id,
                    session_id=session.id,
                    username=user.username,
                    is_platform_admin=user.is_platform_admin,
                    is_verified_email=user.is_verified_email,
                ),
                refresh_token_expires_at=session.expires_at,
            )

            next_refresh_token_hash = await self._sha256_hasher.to_hash(
                string=token_pair.refresh_token,
            )

            rotated = await self._sessions_repository.update_refresh_token(
                session_id=session.id,
                current_refresh_token_hash=refresh_token_hash,
                next_refresh_token_hash=next_refresh_token_hash,
                now=datetime_with_tz(),
            )

            if not rotated:
                raise AuthenticationException("Invalid or expired refresh token")

            return token_pair
