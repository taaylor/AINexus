import pytest

from auth.src.common.settings import settings
from auth.src.domain.entities.tokens import TokenPayload
from auth.src.infrastructure.database.models import UserModel
from auth.src.infrastructure.jwt.jwt_coder import JWTCoder
from auth.tests.types import JWT, BearerHeader


@pytest.fixture(scope="session")
def jwt_coder() -> JWTCoder:
    return JWTCoder(settings=settings)


@pytest.fixture()
def access_token(
    user: UserModel,
    jwt_coder: JWTCoder,
) -> JWT:
    return jwt_coder.create_token_pair(
        payload=TokenPayload(
            id=user.id,
            username=user.username,
            role="user",
            is_platform_admin=user.is_platform_admin,
            is_verified_email=False,
        )
    ).access_token


@pytest.fixture()
def header_bearer(access_token: JWT) -> BearerHeader:
    return {"Authorization": f"Bearer {access_token}"}
