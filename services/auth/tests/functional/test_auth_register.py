from typing import Any
from uuid import UUID

import pytest
from faker import Faker
from starlette import status
from starlette.testclient import TestClient

from auth.src.infrastructure.database.models import (
    UserCredentialModel,
    UserModel,
)
from auth.tests import factories
from auth.tests.types import ActiveSession
from auth.tests.utils import assert_response

pytestmark = pytest.mark.anyio


async def test_user_register(
    client: TestClient,
    active_session: ActiveSession,
) -> None:
    payload = factories.UserRegisterInputSchemaFactory.build_json()

    user_id = UUID(
        assert_response(
            client.post(
                "/api/v1/auth/register",
                json=payload,
            ),
            expected_code=status.HTTP_201_CREATED,
            expected_json={
                "id": str,
                "username": payload.get("username"),
                "name": payload.get("name"),
                "surname": payload.get("surname"),
                "patronymic": payload.get("patronymic"),
            },
        ).json()["id"]
    )

    async with active_session() as session:
        assert await session.get(UserModel, user_id) is not None
        assert await session.get(UserCredentialModel, user_id) is not None


async def test_user_register_invalid_password(
    faker: Faker,
    client: TestClient,
) -> None:
    payload = factories.UserRegisterInputSchemaFactory.build_json()
    payload["password"] = faker.password(length=16)

    assert_response(
        client.post(
            "/api/v1/auth/register",
            json=payload,
        ),
        expected_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        expected_json={"detail": Any},
    )


async def test_user_register_email_exists(
    client: TestClient,
    user_cred: UserCredentialModel,
) -> None:
    assert_response(
        client.post(
            "/api/v1/auth/register",
            json=factories.UserRegisterInputSchemaFactory.build_json(email=user_cred.email),
        ),
        expected_code=status.HTTP_409_CONFLICT,
        expected_json={"detail": "Email already exists"},
    )


async def test_user_register_username_exists(
    client: TestClient,
    user: UserModel,
) -> None:
    assert_response(
        client.post(
            "/api/v1/auth/register",
            json=factories.UserRegisterInputSchemaFactory.build_json(
                username=user.username
            ),
        ),
        expected_code=status.HTTP_409_CONFLICT,
        expected_json={"detail": "Username already exists"},
    )
