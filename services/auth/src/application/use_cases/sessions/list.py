from typing import Final

from auth.src.application.dto.user_sessions import (
    UserListSessionsInput,
    UserListSessionsOutput,
    UserSessionOutput,
)
from auth.src.domain.entities.session import UserSessionSummary
from auth.src.domain.ports import IUseCase
from auth.src.domain.ports.repository.sessions_repo import IUserSessionsRepository


class UserListSessionsUseCase(IUseCase[UserListSessionsInput, UserListSessionsOutput]):
    __slots__: Final[tuple[str, ...]] = ("_sessions_repository",)

    def __init__(self, *, sessions_repository: IUserSessionsRepository) -> None:
        self._sessions_repository = sessions_repository

    async def execute(self, *, input_data: UserListSessionsInput) -> UserListSessionsOutput:
        sessions = await self._sessions_repository.fetch_by_user_id(
            user_id=input_data.user_id,
        )

        return UserListSessionsOutput(
            active=[self._to_output(session) for session in sessions.active],
            inactive=[self._to_output(session) for session in sessions.inactive],
        )

    @staticmethod
    def _to_output(session: UserSessionSummary) -> UserSessionOutput:
        return UserSessionOutput(
            id=session.id,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
        )
