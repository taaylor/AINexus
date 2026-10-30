import asyncio
import hashlib
import hmac

from auth.src.domain.ports import IHasher
from services.trace.tracer import TSpanKind, traced


class SHA256Hasher(IHasher):
    @traced("sha256.to_hash", kind=TSpanKind.INTERNAL)
    async def to_hash(self, *, string: str) -> str:
        return await asyncio.to_thread(self._sync_sha256, string.encode())

    @traced("sha256.verify", kind=TSpanKind.INTERNAL)
    async def verify(self, *, string: str, hashed_string: str) -> bool:
        return await asyncio.to_thread(self._sync_verify, string.encode(), hashed_string)

    @staticmethod
    def _sync_sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _sync_verify(data: bytes, hashed_string: str) -> bool:
        computed = hashlib.sha256(data).hexdigest()
        return hmac.compare_digest(computed, hashed_string)
