from contextlib import AbstractAsyncContextManager
from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class ActiveSession(Protocol):
    def __call__(self) -> AbstractAsyncContextManager[AsyncSession]:
        pass


type AnyJSON = dict[str, Any]
type AnyKwargs = AnyJSON
type JWT = str
type BearerHeader = dict[str, str]
