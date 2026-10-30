import asyncio

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from auth.src.common.settings import Settings
from auth.src.domain.ports import IHasher
from services.trace.tracer import TSpanKind, traced


class Argon2Hasher(IHasher):
    __slots__: tuple[str, ...] = ("hasher", "_semaphore")

    def __init__(self, *, settings: Settings) -> None:
        self.hasher: PasswordHasher = PasswordHasher(
            time_cost=settings.hasher.time_cost,
            memory_cost=settings.hasher.memory_cost,
            parallelism=settings.hasher.parallelism,
            hash_len=settings.hasher.hash_len,
            salt_len=settings.hasher.salt_len,
        )
        self._semaphore = asyncio.BoundedSemaphore(12)

    @traced("argon2.to_hash", kind=TSpanKind.INTERNAL)
    async def to_hash(self, *, string: str) -> str:
        async with self._semaphore:
            return await asyncio.to_thread(self.hasher.hash, string)

    @traced("argon2.verify", kind=TSpanKind.INTERNAL)
    async def verify(self, *, string: str, hashed_string: str) -> bool:
        async with self._semaphore:
            try:
                return await asyncio.to_thread(self.hasher.verify, hashed_string, string)
            except (InvalidHashError, VerifyMismatchError):
                return False
