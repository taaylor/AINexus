from typing import Protocol


class IHasher(Protocol):
    async def to_hash(self, *, string: str) -> str:
        pass

    async def verify(self, *, string: str, hashed_string: str) -> bool:
        pass
