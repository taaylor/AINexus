from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.src.common.exceptions import AuthenticationException
from auth.src.domain.entities.tokens import TokenPayload
from auth.src.domain.ports import ITokenProvider

bearer_scheme = HTTPBearer(auto_error=False)


@inject
async def auth_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    token_provider: FromDishka[ITokenProvider],
) -> TokenPayload:
    if credentials is None:
        raise AuthenticationException("Invalid or missing access token")

    payload = token_provider.decode_access_token(token=credentials.credentials)

    if payload is None:
        raise AuthenticationException("Invalid or missing access token")

    return payload
