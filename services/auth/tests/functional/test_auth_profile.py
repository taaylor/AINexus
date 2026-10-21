import pytest
from starlette import status
from starlette.testclient import TestClient

from auth.src.infrastructure.database.models import UserCredentialModel, UserModel
from auth.tests.utils import assert_response

pytestmark = pytest.mark.anyio


async def test_user_fetch_profile(
    auth_client: TestClient,
    user: UserModel,
    user_cred: UserCredentialModel,
) -> None:
    assert_response(
        auth_client.get("/api/auth-service/protected/v1/auth/profile"),
        expected_json={
            "id": str,
            "username": user.username,
            "name": user.name,
            "surname": user.surname,
            "patronymic": user.patronymic,
            "avatar_key": user.avatar_key,
            "email": user_cred.email,
            "telegram": user_cred.telegram,
            "is_verified_email": user_cred.is_verified_email,
        },
    )


@pytest.mark.parametrize(
    "headers",
    [
        pytest.param({}, id="missing-proxy-headers"),
        pytest.param({"X-Session-ID": "invalid"}, id="partial-proxy-headers"),
    ],
)
async def test_user_fetch_profile_without_complete_proxy_headers_returns_unauthorized(
    client: TestClient,
    headers: dict[str, str],
) -> None:
    assert_response(
        client.get("/api/auth-service/protected/v1/auth/profile", headers=headers),
        expected_code=status.HTTP_401_UNAUTHORIZED,
        expected_json={"detail": "Invalid or missing proxy authorization headers"},
    )
