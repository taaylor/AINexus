import hashlib
import hmac

from auth.src.domain.ports import IHasher
from services.trace.tracer import traced


class SHA256Hasher(IHasher):
    @traced("auth.token.hash")
    async def to_hash(self, *, string: str) -> str:
        return hashlib.sha256(string.encode()).hexdigest()

    async def verify(self, *, string: str, hashed_string: str) -> bool:
        computed_hash = await self.to_hash(string=string)
        return hmac.compare_digest(computed_hash, hashed_string)
