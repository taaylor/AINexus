import hashlib
import hmac

from auth.src.domain.ports import IHasher
from services.trace.tracer import TSpanKind, traced


class SHA256Hasher(IHasher):
    @traced("sha256.to_hash", kind=TSpanKind.INTERNAL)
    async def to_hash(self, *, string: str) -> str:
        return hashlib.sha256(string.encode()).hexdigest()

    @traced("sha256.verify", kind=TSpanKind.INTERNAL)
    async def verify(self, *, string: str, hashed_string: str) -> bool:
        computed = hashlib.sha256(string.encode()).hexdigest()
        return hmac.compare_digest(computed, hashed_string)
