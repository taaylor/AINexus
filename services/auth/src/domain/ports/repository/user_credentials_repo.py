from typing import Protocol
from uuid import UUID

from auth.src.domain.entities.user import CreateUserCredentials


class IUserCredentialsRepository(Protocol):
    async def create(
        self,
        *,
        user_id: UUID,
        credentials: CreateUserCredentials,
    ) -> UUID | None:
        pass
