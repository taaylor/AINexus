from typing import Literal

import pytest
from faker import Faker
from sqlalchemy import select
from starlette import status
from starlette.testclient import TestClient

from auth.src.infrastructure.database.models import (
    UserCredentialModel,
    UserModel,
    UserSessionModel,
)
from auth.tests.types import ActiveSession
from auth.tests.utils import assert_response

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    "login_field",
    [
        pytest.param("username", id="username"),
        pytest.param("email", id="email"),
    ],
)
async def test_user_login(
    client: TestClient,
    active_session: ActiveSession,
    user: UserModel,
    user_cred: UserCredentialModel,
    user_password: str,
    login_field: Literal["username", "email"],
) -> None:
    assert_response(
        client.post(
            "/api/v1/auth/login",
            json={
                "login": (user.username if login_field == "username" else user_cred.email),
                "password": user_password,
            },
        ),
        expected_code=status.HTTP_200_OK,
        expected_json={
            "access_token": str,
            "refresh_token": str,
            "token_type": "Bearer",
            "expires_in": int,
            "refresh_token_expires_at": str,
        },
    )

    async with active_session() as session:
        assert (
            await session.scalar(
                select(UserSessionModel).where(UserSessionModel.user_id == user.id)
            )
            is not None
        )


async def test_user_login_invalid_password(
    faker: Faker,
    client: TestClient,
    user: UserModel,
    user_cred: UserCredentialModel,
) -> None:
    assert_response(
        client.post(
            "/api/v1/auth/login",
            json={
                "login": user.username,
                "password": faker.password(),
            },
        ),
        expected_code=status.HTTP_401_UNAUTHORIZED,
        expected_json={"detail": "Invalid login or password"},
    )


async def test_user_login_user_not_found(
    client: TestClient,
    faker: Faker,
) -> None:
    assert_response(
        client.post(
            "/api/v1/auth/login",
            json={
                "login": faker.unique.email(),
                "password": faker.password(),
            },
        ),
        expected_code=status.HTTP_401_UNAUTHORIZED,
        expected_json={"detail": "Invalid login or password"},
    )
