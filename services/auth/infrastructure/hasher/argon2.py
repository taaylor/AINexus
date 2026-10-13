import asyncio

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from auth.common.settings import Settings
from auth.domain.ports import IHasher


class Argon2Hasher(IHasher):
    __slots__: tuple[str, ...] = ("hasher",)

    def __init__(self, *, settings: Settings) -> None:
        self.hasher: PasswordHasher = PasswordHasher(
            time_cost=settings.hasher.time_cost,
            memory_cost=settings.hasher.memory_cost,
            parallelism=settings.hasher.parallelism,
            hash_len=settings.hasher.hash_len,
            salt_len=settings.hasher.salt_len,
        )

    async def to_hash(self, *, string: str) -> str:
        return await asyncio.to_thread(self.hasher.hash, string)

    async def verify(self, *, string: str, hashed_string: str) -> bool:
        try:
            return await asyncio.to_thread(self.hasher.verify, hashed_string, string)
        except (InvalidHashError, VerifyMismatchError):
            return False
