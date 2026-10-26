from typing import Protocol


class INoSQL(Protocol):
    async def set(self, *, key: str, value: str, ttl: int) -> tuple[None, bool]:
        pass

    async def delete(self, *, key: str) -> tuple[None, bool]:
        pass
