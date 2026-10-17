from collections.abc import Awaitable, Callable, Generator
from typing import Any

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from auth.src.domain.ports import IHasher
from auth.src.infrastructure.database.models import (
    UserCredentialModel,
    UserModel,
)
from auth.src.main import app
from auth.tests.factories import UserModelFactory
from auth.tests.types import ActiveSession, BearerHeader

pytest_plugins = (
    "anyio",
    "auth.tests.plugins.asession",
    "auth.tests.plugins.faker",
    "auth.tests.plugins.hasher",
    "auth.tests.plugins.jwt",
)


type UserFactory = Callable[..., Awaitable[UserModel]]
type UserCredFactory = Callable[..., Awaitable[UserCredentialModel]]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_client(client: TestClient, header_bearer: BearerHeader) -> TestClient:
    return TestClient(client.app, headers=header_bearer)


@pytest.fixture(scope="session")
def user_factory(active_session: ActiveSession) -> UserFactory:
    async def create_user(**kwargs: Any) -> UserModel:
        user = UserModelFactory.build(**kwargs)

        async with active_session() as session:
            session.add(user)
            await session.flush()

        return user

    return create_user


@pytest.fixture(scope="session")
def user_cred_factory(
    argon2: IHasher,
    active_session: ActiveSession,
) -> UserCredFactory:
    async def create_user_cred(**kwargs: Any) -> UserCredentialModel:
        user_cred = UserCredentialModel(
            id=kwargs.pop("user_id"),
            email=kwargs.pop("email"),
            password_hash=await argon2.to_hash(string=kwargs.pop("password")),
            telegram=kwargs.pop("telegram", None),
            is_verified_email=kwargs.pop("is_verified_email", False),
        )

        async with active_session() as session:
            session.add(user_cred)
            await session.flush()

        return user_cred

    return create_user_cred


@pytest.fixture()
async def user(user_factory: UserFactory) -> UserModel:
    return await user_factory()


@pytest.fixture()
def user_password(faker: Faker) -> str:
    return faker.password(length=16)


@pytest.fixture()
async def user_cred(
    user: UserModel,
    user_cred_factory: UserCredFactory,
    faker: Faker,
    user_password: str,
) -> UserCredentialModel:
    return await user_cred_factory(
        user_id=user.id,
        email=faker.unique.email(),
        password=user_password,
        telegram=faker.user_name(),
    )
