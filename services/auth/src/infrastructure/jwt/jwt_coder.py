import secrets
from datetime import datetime, timedelta
from typing import Final

import jwt

from auth.src.common.settings import Settings
from auth.src.common.utils import datetime_with_tz
from auth.src.domain.entities.tokens import TokenPair, TokenPayload
from services.trace.tracer import traced


class JWTCoder:
    __slots__: Final[tuple[str, ...]] = (
        "private_key",
        "access_token_ttl_seconds",
        "refresh_token_ttl_seconds",
        "algo_access",
    )

    def __init__(
        self,
        *,
        settings: Settings,
    ) -> None:
        self.private_key = settings.jwt.private_key.get_secret_value()
        self.access_token_ttl_seconds = settings.jwt.access_token_ttl_seconds
        self.refresh_token_ttl_seconds = settings.jwt.refresh_token_ttl_seconds
        self.algo_access = settings.jwt.algo_access

    @traced("auth.token.create_pair")
    def create_token_pair(
        self,
        *,
        payload: TokenPayload,
        refresh_token_expires_at: datetime | None = None,
    ) -> TokenPair:
        datetimenow = datetime_with_tz()

        claims = {
            "id": str(payload.id),
            "session_id": str(payload.session_id),
            "username": payload.username,
            "is_platform_admin": payload.is_platform_admin,
            "is_verified_email": payload.is_verified_email,
            "iat": int(datetimenow.timestamp()),
            "exp": int(datetimenow.timestamp()) + self.access_token_ttl_seconds,
            "token_type": "access",
        }

        access_token = jwt.encode(claims, self.private_key, algorithm=self.algo_access)
        refresh_token = secrets.token_urlsafe(64)
        token_pair_refresh_token_expires_at = (
            refresh_token_expires_at
            if refresh_token_expires_at is not None
            else datetimenow + timedelta(seconds=self.refresh_token_ttl_seconds)
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self.access_token_ttl_seconds,
            refresh_token_expires_at=token_pair_refresh_token_expires_at,
        )
