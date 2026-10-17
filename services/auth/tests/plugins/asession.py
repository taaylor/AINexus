from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker as create_async_sessionmaker,
)

from auth.src.common.settings import settings
from auth.tests.types import ActiveSession


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine]:
    db_engine = create_async_engine(
        url=settings.postgres.dsn,
        echo=settings.postgres.echo,
        pool_size=settings.postgres.pool_size,
        max_overflow=settings.postgres.max_pool_size,
        pool_recycle=settings.postgres.pool_recycle,
        pool_pre_ping=settings.postgres.pool_pre_ping,
    )
    try:
        yield db_engine
    finally:
        await db_engine.dispose()


@pytest.fixture(scope="session")
def async_sessionmaker(
    engine: AsyncEngine,
) -> create_async_sessionmaker[AsyncSession]:
    return create_async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest.fixture(scope="session")
def active_session(
    async_sessionmaker: create_async_sessionmaker[AsyncSession],
) -> ActiveSession:
    @asynccontextmanager
    async def active_session_inner() -> AsyncGenerator[AsyncSession]:
        async with async_sessionmaker.begin() as session:
            yield session

    return active_session_inner
