from typing import Protocol

from auth.src.domain.entities.tokens import TokenPair, TokenPayload


class ITokenProvider(Protocol):
    def create_token_pair(self, *, payload: TokenPayload) -> TokenPair:
        pass

    def decode_access_token(self, *, token: str) -> TokenPayload | None:
        pass
