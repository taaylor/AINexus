from typing import Annotated, Final, Self
from uuid import UUID

from fastapi import Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from auth.src.common.exceptions import AuthenticationException

AUTH_SESSION_ID_HEADER_NAME: Final[str] = "X-Session-ID"
AUTH_USER_ID_HEADER_NAME: Final[str] = "X-User-ID"
AUTH_USERNAME_HEADER_NAME: Final[str] = "X-Username"
AUTH_IS_PLATFORM_ADMIN_HEADER_NAME: Final[str] = "X-Is-Platform-Admin"
AUTH_IS_VERIFIED_EMAIL_HEADER_NAME: Final[str] = "X-Is-Verified-Email"


SessionIDHeader = Annotated[
    str | None,
    Depends(
        APIKeyHeader(
            name=AUTH_SESSION_ID_HEADER_NAME,
            auto_error=False,
            scheme_name="session id header",
        )
    ),
]
UserIDHeader = Annotated[
    str | None,
    Depends(
        APIKeyHeader(
            name=AUTH_USER_ID_HEADER_NAME,
            auto_error=False,
            scheme_name="user id header",
        )
    ),
]
UsernameHeader = Annotated[
    str | None,
    Depends(
        APIKeyHeader(
            name=AUTH_USERNAME_HEADER_NAME,
            auto_error=False,
            scheme_name="username header",
        )
    ),
]
IsPlatformAdminHeader = Annotated[
    str | None,
    Depends(
        APIKeyHeader(
            name=AUTH_IS_PLATFORM_ADMIN_HEADER_NAME,
            auto_error=False,
            scheme_name="platform admin header",
        )
    ),
]
IsVerifiedEmailHeader = Annotated[
    str | None,
    Depends(
        APIKeyHeader(
            name=AUTH_IS_VERIFIED_EMAIL_HEADER_NAME,
            auto_error=False,
            scheme_name="verified email header",
        )
    ),
]


class AuthProxyData(BaseModel):
    session_id: UUID
    user_id: UUID
    username: str
    is_platform_admin: bool
    is_verified_email: bool

    @classmethod
    def construct_auth_proxy_data(
        cls,
        *,
        session_id: SessionIDHeader,
        user_id: UserIDHeader,
        username: UsernameHeader,
        is_platform_admin: IsPlatformAdminHeader,
        is_verified_email: IsVerifiedEmailHeader,
    ) -> Self:
        if (
            session_id is None
            or user_id is None
            or username is None
            or is_platform_admin is None
            or is_verified_email is None
        ):
            raise AuthenticationException("Invalid or missing proxy authorization headers")

        return cls(
            session_id=session_id,
            user_id=user_id,
            username=username,
            is_platform_admin=is_platform_admin,
            is_verified_email=is_verified_email,
        )

    @property
    def as_headers(self) -> dict[str, str]:
        return {
            AUTH_SESSION_ID_HEADER_NAME: str(self.session_id),
            AUTH_USER_ID_HEADER_NAME: str(self.user_id),
            AUTH_USERNAME_HEADER_NAME: self.username,
            AUTH_IS_PLATFORM_ADMIN_HEADER_NAME: str(self.is_platform_admin),
            AUTH_IS_VERIFIED_EMAIL_HEADER_NAME: str(self.is_verified_email),
        }


async def auth_proxy_data(
    session_id: SessionIDHeader = None,
    user_id: UserIDHeader = None,
    username: UsernameHeader = None,
    is_platform_admin: IsPlatformAdminHeader = None,
    is_verified_email: IsVerifiedEmailHeader = None,
) -> AuthProxyData:
    return AuthProxyData.construct_auth_proxy_data(
        session_id=session_id,
        user_id=user_id,
        username=username,
        is_platform_admin=is_platform_admin,
        is_verified_email=is_verified_email,
    )


AuthUserProxy = Annotated[AuthProxyData, Depends(auth_proxy_data)]
