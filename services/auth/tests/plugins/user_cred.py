from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from faker import Faker

from auth.src.domain.ports import IHasher
from auth.src.infrastructure.database.models import UserCredentialModel, UserModel
from auth.tests.types import ActiveSession

type UserCredFactory = Callable[..., Awaitable[UserCredentialModel]]


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
