import secrets
from datetime import timedelta
from typing import Any, Final
from uuid import UUID

import jwt

from auth.src.common.settings import Settings
from auth.src.common.utils import datetime_with_tz
from auth.src.domain.entities.tokens import TokenPair, TokenPayload


class JWTCoder:
    __slots__: Final[tuple[str, ...]] = (
        "private_key",
        "public_key",
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
        self.public_key = settings.jwt.public_key.get_secret_value()
        self.access_token_ttl_seconds = settings.jwt.access_token_ttl_seconds
        self.refresh_token_ttl_seconds = settings.jwt.refresh_token_ttl_seconds
        self.algo_access = settings.jwt.algo_access

    def create_token_pair(self, *, payload: TokenPayload) -> TokenPair:
        datetimenow = datetime_with_tz()

        claims = {
            "id": str(payload.id),
            "username": payload.username,
            "role": payload.role,
            "is_platform_admin": payload.is_platform_admin,
            "is_verified_email": payload.is_verified_email,
            "iat": int(datetimenow.timestamp()),
            "exp": int(datetimenow.timestamp()) + self.access_token_ttl_seconds,
            "token_type": "access",
        }

        access_token = jwt.encode(claims, self.private_key, algorithm=self.algo_access)
        refresh_token = secrets.token_urlsafe(64)
        refresh_token_exp_at = datetimenow + timedelta(
            seconds=self.refresh_token_ttl_seconds
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self.access_token_ttl_seconds,
            refresh_token_expires_at=refresh_token_exp_at,
        )

    def decode_access_token(self, *, token: str) -> TokenPayload | None:
        try:
            claims: dict[str, Any] = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algo_access],
                options={
                    "require": [
                        "exp",
                        "iat",
                        "token_type",
                        "id",
                        "username",
                        "is_platform_admin",
                        "role",
                        "is_verified_email",
                    ],
                },
            )
            if claims["token_type"] != "access":
                return None

            return TokenPayload(
                id=UUID(claims["id"]),
                username=claims["username"],
                role=claims["role"],
                is_platform_admin=claims["is_platform_admin"],
                is_verified_email=claims["is_verified_email"],
            )
        except (jwt.PyJWTError, KeyError, TypeError, ValueError):
            return None
