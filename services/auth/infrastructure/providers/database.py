from collections.abc import AsyncGenerator
from typing import Any

import anyio
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from auth.common.settings import Settings
from auth.domain.ports.repository.user_credentials_repo import (
    IUserCredentialsRepository,
)
from auth.domain.ports.repository.users_repo import IUsersRepository
from auth.domain.ports.unit_of_work import IUnitOfWork
from auth.infrastructure.database.repository.user_credentials import (
    UserCredentialsRepository,
)
from auth.infrastructure.database.repository.users import UsersRepository
from auth.infrastructure.database.unit_of_work import UnitOfWork


class DatabaseProvider(Provider):
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
    async def engine(self) -> AsyncGenerator[AsyncEngine, None]:
        engine = create_async_engine(
            url=self.settings.postgres.dsn,
            echo=self.settings.postgres.echo,
            pool_size=self.settings.postgres.pool_size,
            max_overflow=self.settings.postgres.max_pool_size,
            pool_recycle=self.settings.postgres.pool_recycle,
            pool_pre_ping=self.settings.postgres.pool_pre_ping,
        )
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    async def sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @provide(scope=Scope.REQUEST)
    async def session(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> AsyncGenerator[AsyncSession, None]:
        session = sessionmaker()
        try:
            yield session
        finally:
            with anyio.CancelScope(shield=True):
                if session.in_transaction():
                    await session.rollback()
                await session.close()

    @provide(scope=Scope.REQUEST)
    def unit_of_work(
        self,
        session: AsyncSession,
    ) -> IUnitOfWork:
        return UnitOfWork(session)

    @provide(scope=Scope.REQUEST)
    async def users_db_repo(
        self,
        session: AsyncSession,
    ) -> IUsersRepository:
        return UsersRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def user_credentials_db_repo(
        self,
        session: AsyncSession,
    ) -> IUserCredentialsRepository:
        return UserCredentialsRepository(session=session)
