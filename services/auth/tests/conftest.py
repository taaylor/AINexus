from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.src.infrastructure.database.models import (
    UserCredentialModel,
    UserModel,
)
from auth.src.main import app
from auth.src.presentation.api.v1.dependencies import AuthProxyData

pytest_plugins = (
    "anyio",
    "auth.tests.plugins.asession",
    "auth.tests.plugins.faker",
    "auth.tests.plugins.hasher",
    "auth.tests.plugins.sessions",
    "auth.tests.plugins.users",
    "auth.tests.plugins.user_cred",
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
def proxy_auth_data(
    user: UserModel,
    user_cred: UserCredentialModel,
) -> AuthProxyData:
    return AuthProxyData(
        session_id=uuid4(),
        user_id=user.id,
        username=user.username,
        is_platform_admin=user.is_platform_admin,
        is_verified_email=user_cred.is_verified_email,
    )


@pytest.fixture(scope="session", autouse=True)
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_client(
    client: TestClient,
    proxy_auth_data: AuthProxyData,
) -> TestClient:
    return TestClient(client.app, headers=proxy_auth_data.as_headers)
