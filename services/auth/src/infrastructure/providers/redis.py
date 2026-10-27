from collections.abc import AsyncGenerator
from typing import Any

from dishka import Provider, Scope, provide
from redis.asyncio import Redis as RedisAsync

from auth.src.common.settings import Settings
from auth.src.domain.ports import INoSQL
from auth.src.infrastructure.redis.client import RedisClient


class RedisProvider(Provider):
    def __init__(
        self,
        settings: Settings,
        *,
        scope: Any | None = None,
        component: Any | None = None,
        when: Any | None = None,
    ) -> None:
        super().__init__(scope, component, when)
        self.settings = settings

    @provide(scope=Scope.APP)
    async def redis_connection(self) -> AsyncGenerator[RedisAsync, None]:
        redis = RedisAsync.from_url(
            url=self.settings.redis.dsn,
            decode_responses=True,
        )

        try:
            await redis.ping()
            yield redis
        finally:
            await redis.aclose()

    @provide(scope=Scope.APP, provides=INoSQL)
    def redis_client(self, redis_connection: RedisAsync) -> INoSQL:
        return RedisClient(redis_connection)
