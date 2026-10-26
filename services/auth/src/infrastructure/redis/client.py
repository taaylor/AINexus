from typing import Final

from redis.asyncio import Redis

from auth.src.common.circuitbreaker import RedisErrors, circuit_breaker
from auth.src.domain.ports import INoSQL


class RedisClient(INoSQL):
    __slots__: Final[tuple[str, ...]] = ("_redis",)

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    @circuit_breaker(threshold=5, delay=15, exceptions=RedisErrors)
    async def set(self, *, key: str, value: str, ttl: int) -> None:
        await self._redis.set(name=key, value=value, ex=ttl)
        return

    @circuit_breaker(threshold=5, delay=15, exceptions=RedisErrors)
    async def delete(self, *, key: str) -> None:
        await self._redis.delete(key)
        return
