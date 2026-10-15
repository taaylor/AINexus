from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from auth.src.application.providers import ApplicationProvider
from auth.src.common.settings import settings
from auth.src.infrastructure.providers.database import DatabaseProvider
from auth.src.infrastructure.providers.hasher import HasherProvider
from auth.src.infrastructure.providers.jwt import JwtProvider


def initialization_async_container() -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(settings=settings),
        HasherProvider(settings=settings),
        JwtProvider(settings=settings),
        ApplicationProvider(settings=settings),
        FastapiProvider(),
    )
