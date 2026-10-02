from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from auth.infrastructure.database.enums import IsolationLevel


class UnitOfWork:
    __slots__: tuple[str, ...] = ("isolation", "session")

    def __init__(
        self,
        session: AsyncSession,
        isolation: IsolationLevel | None = None,
    ) -> None:
        self.session = session
        self.isolation = isolation

    def isolation_level(self, isolation: IsolationLevel) -> UnitOfWork:
        return UnitOfWork(self.session, isolation)

    async def __aenter__(self) -> Self:
        transaction = self.session.begin()
        await transaction.start()

        if self.isolation is not None:
            await self.session.connection(
                execution_options={
                    "isolation_level": self.isolation.value,
                }
            )

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                await self.session.rollback()
                return
            await self.session.commit()
        except BaseException:
            await self.session.rollback()
            raise
