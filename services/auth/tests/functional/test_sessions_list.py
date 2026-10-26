from collections.abc import AsyncGenerator
from datetime import timedelta
from typing import Final

import pytest
from faker import Faker
from starlette.testclient import TestClient

from auth.src.common.utils import datetime_with_tz
from auth.src.infrastructure.database.models import UserModel, UserSessionModel
from auth.src.presentation.api.v1.dependencies import AuthProxyData
from auth.tests.factories import UserSessionModelFactory
from auth.tests.plugins.asession import ActiveSession
from auth.tests.plugins.sessions import UserSessionFactory
from auth.tests.utils import assert_response

pytestmark = pytest.mark.anyio

SESSION_FLAG_VALUES: Final[tuple[bool, bool]] = (False, True)
SESSION_FLAGS_COUNT: Final[int] = 2
SESSION_COMBINATIONS_COUNT: Final[int] = len(SESSION_FLAG_VALUES) ** SESSION_FLAGS_COUNT


@pytest.fixture()
async def sessions(
    faker: Faker,
    active_session: ActiveSession,
    user: UserModel,
) -> AsyncGenerator[list[UserSessionModel], None]:
    now = datetime_with_tz()
    sessions: list[UserSessionModel] = []

    async with active_session() as asession:
        for i in range(SESSION_COMBINATIONS_COUNT):
            session = UserSessionModelFactory.build(
                user_id=user.id,
                revoked_at=(
                    now - timedelta(minutes=1)
                    if SESSION_FLAG_VALUES[i // len(SESSION_FLAG_VALUES)]
                    else None
                ),
                expires_at=(
                    now - timedelta(days=1)
                    if SESSION_FLAG_VALUES[i % len(SESSION_FLAG_VALUES)]
                    else now + timedelta(days=1)
                ),
                created_at=now - timedelta(minutes=i),
                user_agent=faker.user_agent(),
                ip_address=faker.ipv4(),
            )

            asession.add(session)
            await asession.flush()

            sessions.append(session)

    yield sessions

    async with active_session() as asession:
        for session in sessions:
            await asession.delete(session)


async def test_list_sessions(
    auth_client: TestClient,
    sessions: list[UserSessionModel],
) -> None:
    expected_sessions = [
        {
            "id": str(session.id),
            "user_agent": session.user_agent,
            "ip_address": session.ip_address,
        }
        for session in sessions
    ]

    assert_response(
        auth_client.get("/api/auth-service/protected/v1/sessions"),
        expected_json={
            "active": expected_sessions[:1],
            "inactive": expected_sessions[1:],
        },
    )


async def test_list_sessions_inactive(
    auth_client: TestClient,
    proxy_auth_data: AuthProxyData,
    user_session_factory: UserSessionFactory,
) -> None:
    sessions = [
        await user_session_factory(
            user_id=proxy_auth_data.user_id,
            expires_at=datetime_with_tz() - timedelta(days=1),
            created_at=datetime_with_tz() - timedelta(days=7 - index),
            user_agent=f"inactive-agent-{index}",
            ip_address=f"192.0.2.{index + 1}",
        )
        for index in range(7)
    ]

    assert_response(
        auth_client.get("/api/auth-service/protected/v1/sessions"),
        expected_json={
            "active": [],
            "inactive": [
                {
                    "id": str(session.id),
                    "user_agent": f"inactive-agent-{index}",
                    "ip_address": f"192.0.2.{index + 1}",
                }
                for index, session in list(enumerate(sessions[-5:], start=2))[::-1]
            ],
        },
    )
