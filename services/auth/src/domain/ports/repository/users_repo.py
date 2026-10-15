from typing import Protocol
from uuid import UUID

from auth.src.domain.entities.user import (
    CreateUser,
    RegisteredUser,
    UserLogin,
    UserProfile,
)


class IUsersRepository(Protocol):
    async def fetch_by_login(self, *, login: str) -> UserLogin | None:
        pass

    async def fetch_by_id_profile(self, *, user_id: UUID) -> UserProfile | None:
        pass

    async def create(self, *, user: CreateUser) -> RegisteredUser | None:
        pass
