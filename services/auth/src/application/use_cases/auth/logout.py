from typing import Final

from auth.src.application.dto.user_logout import UserLogoutInput
from auth.src.common.utils import datetime_with_tz
from auth.src.domain.ports import INoSQL, IUnitOfWork, IUseCase
from auth.src.domain.ports.repository.sessions_repo import IUserSessionsRepository


class UserLogoutUseCase(IUseCase[UserLogoutInput, None]):
    __slots__: Final[tuple[str, ...]] = (
        "_unit_of_work",
        "_sessions_repository",
        "_nosql_client",
        "_access_token_ttl_seconds",
        "_session_revoked_key_format",
        "_session_revoked_value",
    )

    def __init__(
        self,
        *,
        unit_of_work: IUnitOfWork,
        sessions_repository: IUserSessionsRepository,
        nosql_client: INoSQL,
        access_token_ttl_seconds: int,
        session_revoked_key_format: str,
        session_revoked_value: str,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._sessions_repository = sessions_repository
        self._nosql_client = nosql_client
        self._access_token_ttl_seconds = access_token_ttl_seconds
        self._session_revoked_key_format = session_revoked_key_format
        self._session_revoked_value = session_revoked_value

    async def execute(self, *, input_data: UserLogoutInput) -> None:
        async with self._unit_of_work:
            await self._sessions_repository.revoke_by_id(
                session_id=input_data.session_id,
                user_id=input_data.user_id,
                revoked_at=datetime_with_tz(),
            )

            await self._nosql_client.set(
                key=self._session_revoked_key_format.format(
                    session_id=input_data.session_id,
                ),
                value=self._session_revoked_value,
                ttl=self._access_token_ttl_seconds,
            )
