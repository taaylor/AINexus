from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from auth.application.providers import ApplicationProvider
from auth.common.settings import settings
from auth.infrastructure.providers.database import DatabaseProvider
from auth.infrastructure.providers.hasher import HasherProvider
from auth.infrastructure.providers.jwt import JwtProvider


def initialization_async_container() -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(settings=settings),
        HasherProvider(settings=settings),
        JwtProvider(settings=settings),
        ApplicationProvider(settings=settings),
        FastapiProvider(),
    )
