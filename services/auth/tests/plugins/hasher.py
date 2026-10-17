import pytest

from auth.src.common.settings import settings
from auth.src.domain.ports import IHasher
from auth.src.infrastructure.hasher.argon2 import Argon2Hasher
from auth.src.infrastructure.hasher.sha256 import SHA256Hasher


@pytest.fixture(scope="session")
def argon2() -> IHasher:
    return Argon2Hasher(settings=settings)


@pytest.fixture(scope="session")
def sha256() -> IHasher:
    return SHA256Hasher()
