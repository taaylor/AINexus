from datetime import timedelta

import pytest
from starlette import status
from starlette.testclient import TestClient

from auth.src.common.utils import datetime_with_tz
from auth.src.infrastructure.database.models import UserSessionModel
from auth.src.presentation.api.v1.dependencies import AuthProxyData
from auth.tests.plugins.asession import ActiveSession
from auth.tests.plugins.sessions import UserSessionFactory
from auth.tests.utils import assert_nodata_response, assert_response

pytestmark = pytest.mark.anyio


async def test_user_logout_revokes_current_session(
    auth_client: TestClient,
    proxy_auth_data: AuthProxyData,
    user_session_factory: UserSessionFactory,
    active_session: ActiveSession,
) -> None:
    await user_session_factory(
        id=proxy_auth_data.session_id,
        user_id=proxy_auth_data.user_id,
        expires_at=datetime_with_tz() + timedelta(days=1),
    )

    assert_nodata_response(auth_client.post("/api/auth-service/protected/v1/auth/logout"))

    async with active_session() as asession:
        session = await asession.get(UserSessionModel, proxy_auth_data.session_id)

        assert session is not None
        assert session.revoked_at is not None


async def test_user_logout_without_proxy_headers_returns_unauthorized(
    client: TestClient,
) -> None:
    assert_response(
        client.post("/api/auth-service/protected/v1/auth/logout"),
        expected_code=status.HTTP_401_UNAUTHORIZED,
        expected_json={"detail": "Invalid or missing proxy authorization headers"},
    )
