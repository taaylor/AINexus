from typing import Any, ClassVar, Self

from locust.clients import HttpSession
from pydantic import BaseModel

from auth.src.presentation.api.v1.schemes.user_login import (
    UserLoginInputSchema,
    UserLoginOutputSchema,
)
from auth.src.presentation.api.v1.schemes.user_profile import UserProfileOutputSchema
from auth.src.presentation.api.v1.schemes.user_refresh import (
    UserRefreshInputSchema,
    UserRefreshOutputSchema,
)
from auth.src.presentation.api.v1.schemes.user_register import (
    UserRegisterInputSchema,
    UserRegisterOutputSchema,
)
from auth.src.presentation.api.v1.schemes.user_sessions import (
    UserListSessionsOutputSchema,
)
from auth.tests.perfomance.api.base_client import BaseClient
from auth.tests.perfomance.api.client_factory import get_http_client
from auth.tests.perfomance.settings import HttpClientSettings


class ApiRequestError(RuntimeError):
    def __init__(self, *, method: str, path: str, status_code: int) -> None:
        self.method = method
        self.path = path
        self.status_code = status_code
        super().__init__(f"{method} {path} returned HTTP {status_code}")


class ApiResponseValidationError(RuntimeError):
    def __init__(self, *, method: str, path: str) -> None:
        self.method = method
        self.path = path
        super().__init__(f"{method} {path} returned an invalid response")


class AuthApiClient:
    """Typed HTTP client for the public auth API.

    The client reuses request and response schemas from ``auth`` and can be
    used by seed builders or other async test tooling. It owns one
    ``httpx2.AsyncClient`` so repeated calls can reuse the connection pool.
    Always close it with an asynchronous context manager.

    Example::

        from auth.tests.perfomance.api.auth_client import get_auth_api_client
        from auth.tests.perfomance.settings import settings
        from auth.src.presentation.api.v1.schemes.user_login import (
            UserLoginInputSchema,
        )

        async with get_auth_api_client(settings.auth_api_http_client) as client:
            tokens = await client.login_user(
                UserLoginInputSchema(login="load_user", password="secret")
            )

    ``AUTH_API_HTTP_CLIENT.URL`` and ``AUTH_API_HTTP_CLIENT.TIMEOUT`` configure
    the base URL and timeout through ``PerformanceSettings``. Methods target
    ``/api/auth-service/public/v1/auth/register`` and ``/login``.
    """

    API_PREFIX: ClassVar[str] = "/api/auth-service/public/v1/auth"

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self._client.__aexit__(*args)

    async def register_user(
        self,
        input_data: UserRegisterInputSchema,
    ) -> UserRegisterOutputSchema:
        return await self._post(
            path=f"{self.API_PREFIX}/register",
            input_data=input_data,
            output_schema=UserRegisterOutputSchema,
        )

    async def login_user(
        self,
        input_data: UserLoginInputSchema,
    ) -> UserLoginOutputSchema:
        return await self._post(
            path=f"{self.API_PREFIX}/login",
            input_data=input_data,
            output_schema=UserLoginOutputSchema,
        )

    async def _post[TOutput: BaseModel](
        self,
        *,
        path: str,
        input_data: BaseModel,
        output_schema: type[TOutput],
    ) -> TOutput:
        response = await self._client.post(
            path.lstrip("/"),
            json=input_data.model_dump(mode="json", exclude_none=True),
            extensions={"route": path},
        )
        if not response.is_success:
            raise ApiRequestError(
                method="POST",
                path=path,
                status_code=response.status_code,
            )

        try:
            return output_schema.model_validate(response.json())
        except (ValueError, TypeError) as exc:
            raise ApiResponseValidationError(method="POST", path=path) from exc


def get_auth_api_client(config: HttpClientSettings) -> AuthApiClient:
    """Create a typed auth API client for seeding and non-Locust calls."""

    return AuthApiClient(get_http_client(config))


class LocustAuthApiClient:
    """Typed auth API client that sends requests through Locust's HTTP session."""

    API_PREFIX: ClassVar[str] = AuthApiClient.API_PREFIX
    PROTECTED_API_PREFIX: ClassVar[str] = "/api/auth-service/protected/v1"

    def __init__(self, client: HttpSession, *, timeout: float) -> None:
        self._client = client
        self._timeout = timeout

    def register_user(
        self,
        input_data: UserRegisterInputSchema,
    ) -> UserRegisterOutputSchema | None:
        return self._post(
            path=f"{self.API_PREFIX}/register",
            input_data=input_data,
            output_schema=UserRegisterOutputSchema,
        )

    def login_user(
        self,
        input_data: UserLoginInputSchema,
    ) -> UserLoginOutputSchema | None:
        return self._post(
            path=f"{self.API_PREFIX}/login",
            input_data=input_data,
            output_schema=UserLoginOutputSchema,
        )

    def refresh_user(
        self,
        input_data: UserRefreshInputSchema,
    ) -> UserRefreshOutputSchema | None:
        return self._post(
            path=f"{self.API_PREFIX}/refresh",
            input_data=input_data,
            output_schema=UserRefreshOutputSchema,
        )

    def logout_user(self, *, headers: dict[str, str]) -> None:
        self._post(
            path=f"{self.PROTECTED_API_PREFIX}/auth/logout",
            input_data=None,
            output_schema=None,
            headers=headers,
        )

    def fetch_user_profile(
        self,
        *,
        headers: dict[str, str],
    ) -> UserProfileOutputSchema | None:
        return self._get(
            path=f"{self.PROTECTED_API_PREFIX}/auth/profile",
            output_schema=UserProfileOutputSchema,
            headers=headers,
        )

    def list_user_sessions(
        self,
        *,
        headers: dict[str, str],
    ) -> UserListSessionsOutputSchema | None:
        return self._get(
            path=f"{self.PROTECTED_API_PREFIX}/sessions",
            output_schema=UserListSessionsOutputSchema,
            headers=headers,
        )

    def _post[TOutput: BaseModel](
        self,
        *,
        path: str,
        input_data: BaseModel | dict[str, Any] | None,
        output_schema: type[TOutput] | None,
        headers: dict[str, str] | None = None,
    ) -> TOutput | None:
        return self._request(
            method="POST",
            path=path,
            input_data=input_data,
            output_schema=output_schema,
            headers=headers,
        )

    def _get[
        TOutput: BaseModel,
    ](
        self,
        *,
        path: str,
        output_schema: type[TOutput],
        headers: dict[str, str],
    ) -> TOutput | None:
        return self._request(
            method="GET",
            path=path,
            input_data=None,
            output_schema=output_schema,
            headers=headers,
        )

    def _request[TOutput: BaseModel](
        self,
        *,
        method: str,
        path: str,
        input_data: BaseModel | dict[str, Any] | None,
        output_schema: type[TOutput] | None,
        headers: dict[str, str] | None = None,
    ) -> TOutput | None:
        with self._client.request(
            method,
            path,
            json=(
                input_data.model_dump(mode="json", exclude_none=True)
                if isinstance(input_data, BaseModel)
                else input_data
            ),
            headers=headers,
            name=path,
            timeout=self._timeout,
            catch_response=True,
        ) as response:
            if not 200 <= response.status_code < 300:
                error = ApiRequestError(
                    method=method,
                    path=path,
                    status_code=response.status_code,
                )
                response.failure(str(error))
                raise error

            if output_schema is None:
                response.success()
                return None

            try:
                return output_schema.model_validate(response.json())
            except (ValueError, TypeError) as exc:
                error = ApiResponseValidationError(method=method, path=path)
                response.failure(str(error))
                raise error from exc


def get_auth_locust_api_client(
    client: HttpSession,
    config: HttpClientSettings,
) -> LocustAuthApiClient:
    """Create a typed auth API client backed by Locust's instrumented session."""

    return LocustAuthApiClient(client, timeout=config.timeout)
