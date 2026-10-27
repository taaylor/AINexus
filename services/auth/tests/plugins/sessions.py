from collections.abc import Awaitable, Callable
from typing import Any

import pytest

from auth.src.infrastructure.database.models import UserSessionModel
from auth.tests.factories import UserSessionModelFactory
from auth.tests.types import ActiveSession

type UserSessionFactory = Callable[..., Awaitable[UserSessionModel]]


@pytest.fixture(scope="session")
def user_session_factory(active_session: ActiveSession) -> UserSessionFactory:
    async def create_user_session(**kwargs: Any) -> UserSessionModel:
        user_session = UserSessionModelFactory.build(**kwargs)

        async with active_session() as session:
            session.add(user_session)
            await session.flush()

        return user_session

    return create_user_session
