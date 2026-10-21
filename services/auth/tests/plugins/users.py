from collections.abc import Awaitable, Callable
from typing import Any

import pytest

from auth.src.infrastructure.database.models import UserModel
from auth.tests.factories import UserModelFactory
from auth.tests.types import ActiveSession

type UserFactory = Callable[..., Awaitable[UserModel]]


@pytest.fixture(scope="session")
def user_factory(active_session: ActiveSession) -> UserFactory:
    async def create_user(**kwargs: Any) -> UserModel:
        user = UserModelFactory.build(**kwargs)

        async with active_session() as session:
            session.add(user)
            await session.flush()

        return user

    return create_user


@pytest.fixture()
async def user(user_factory: UserFactory) -> UserModel:
    return await user_factory()
