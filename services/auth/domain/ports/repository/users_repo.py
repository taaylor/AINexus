from typing import Protocol
from uuid import UUID

from auth.domain.entities.user import (
    CreateUser,
    RegisteredUser,
    RegistrationConflicts,
    User,
)


class IUsersRepository(Protocol):
    async def fetch_by_id(self, *, user_id: UUID) -> User | None:
        pass

    async def exist_by_username_email(
        self,
        *,
        username: str,
        email: str,
    ) -> RegistrationConflicts:
        pass

    async def create(self, *, user: CreateUser) -> RegisteredUser:
        pass
