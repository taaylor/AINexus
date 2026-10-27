from datetime import datetime
from typing import Protocol

from auth.src.domain.entities.tokens import TokenPair, TokenPayload


class ITokenProvider(Protocol):
    def create_token_pair(
        self,
        *,
        payload: TokenPayload,
        refresh_token_expires_at: datetime | None = None,
    ) -> TokenPair:
        pass
