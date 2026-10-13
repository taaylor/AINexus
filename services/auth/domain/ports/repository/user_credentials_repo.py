from typing import Protocol
from uuid import UUID

from auth.domain.entities.user import CreateUserCredentials


class IUserCredentialsRepository(Protocol):
    async def create(
        self,
        *,
        user_id: UUID,
        credentials: CreateUserCredentials,
    ) -> None:
        pass
