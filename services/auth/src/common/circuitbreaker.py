from __future__ import annotations

import functools
import inspect
from collections.abc import Callable, Coroutine
from datetime import datetime, timedelta
from enum import StrEnum, auto
from threading import Lock
from typing import Any, Final, Self, cast, overload

from loguru import logger
from redis.exceptions import (
    ConnectionError as RedisConnectionError,
)
from redis.exceptions import (
    TimeoutError as RedisTimeoutError,
)
from sqlalchemy.exc import (
    DisconnectionError as SqlAlchemyDisconnectionError,
)
from sqlalchemy.exc import (
    InterfaceError as SqlAlchemyInterfaceError,
)
from sqlalchemy.exc import (
    OperationalError as SqlAlchemyOperationalError,
)
from sqlalchemy.exc import (
    TimeoutError as SqlAlchemyTimeoutError,
)

from auth.src.common.utils import datetime_with_tz

__all__ = ("RedisErrors", "SqlAlchemyErrors", "CircuitBreaker", "circuit_breaker")


RedisErrors: Final[tuple[type[Exception], ...]] = (RedisTimeoutError, RedisConnectionError)
SqlAlchemyErrors: Final[tuple[type[Exception], ...]] = (
    SqlAlchemyDisconnectionError,
    SqlAlchemyInterfaceError,
    SqlAlchemyOperationalError,
    SqlAlchemyTimeoutError,
)


class StateEnum(StrEnum):
    OPEN = auto()
    CLOSED = auto()
    HALF_OPEN = auto()


class CircuitBreaker[**P, T]:
    def __init__(
        self,
        func: Callable[P, T] | Callable[P, Coroutine[Any, Any, T]] | None = None,
        *,
        threshold: int = 5,
        delay: int = 10,
        exceptions: tuple[type[Exception], ...] = (ConnectionError, TimeoutError),
    ) -> None:
        self.func = func
        self.exceptions_to_catch = exceptions
        self.threshold = threshold
        self.delay = delay

        # by default set the state to closed
        self.state = StateEnum.CLOSED
        self._last_attempt_timestamp: datetime | None = None
        # keep track of failed attemp count
        self._failed_attempt_count = 0
        self._sync_lock = Lock()

        if self.func is not None:
            functools.update_wrapper(self, self.func)

    def __get__(
        self,
        instance: Any,
        owner: type[Any] | None = None,
    ) -> Self | Callable[..., Any]:
        if instance is None:
            return self
        return functools.partial(self, instance)

    @overload
    def __call__[**P2, T2](
        self,
        func: Callable[P2, Coroutine[Any, Any, T2]],
        /,
    ) -> Callable[P2, Coroutine[Any, Any, tuple[T2 | None, bool]]]: ...

    @overload
    def __call__[**P2, T2](
        self,
        func: Callable[P2, T2],
        /,
    ) -> Callable[P2, tuple[T2 | None, bool]]: ...

    @overload
    def __call__(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[T | None, bool] | Coroutine[Any, Any, tuple[T | None, bool]]:
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.func is None:
            decorated_func = args[0]
            breaker = self.__class__(
                func=decorated_func,
                exceptions=self.exceptions_to_catch,
                threshold=self.threshold,
                delay=self.delay,
            )

            if inspect.iscoroutinefunction(decorated_func):

                @functools.wraps(decorated_func)
                async def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
                    return await breaker._async_routing(*func_args, **func_kwargs)
            else:

                @functools.wraps(decorated_func)
                def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
                    return breaker._sync_routing(*func_args, **func_kwargs)

            return wrapper

        if inspect.iscoroutinefunction(self.func):
            return self._async_routing(*args, **kwargs)
        else:
            return self._sync_routing(*args, **kwargs)

    @property
    def state(self) -> StateEnum:
        return self._state

    @state.setter
    def state(self, value: StateEnum) -> None:
        if not isinstance(value, StateEnum):
            raise ValueError("value must be type StateEnum")
        self._state = value

    @property
    def funcname(self) -> str:
        return getattr(self.func, "__name__", type(self.func).__name__)

    def _sync_routing(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[T | None, bool]:
        with self._sync_lock:
            match self.state:
                case StateEnum.CLOSED:
                    handler = self._handle_closed_state

                case StateEnum.OPEN:
                    handler = self._handle_open_state

                case _:
                    return None, False

        return handler(*args, **kwargs)

    async def _async_routing(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[T | None, bool]:
        match self.state:
            case StateEnum.CLOSED:
                handler = self._ahandle_closed_state

            case StateEnum.OPEN:
                handler = self._ahandle_open_state

            case _:
                return None, False

        return await handler(*args, **kwargs)

    def _handle_closed_state(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[T | None, bool]:
        try:
            sync_func = cast(Callable[P, T], self.func)
            result = sync_func(*args, **kwargs)

            with self._sync_lock:
                self._last_attempt_timestamp = datetime_with_tz()
                self._failed_attempt_count = 0
            return result, True

        except self.exceptions_to_catch as error:
            with self._sync_lock:
                self._failed_attempt_count += 1
                if self._failed_attempt_count >= self.threshold:
                    self.state = StateEnum.OPEN
                    self._last_attempt_timestamp = datetime_with_tz()

            logger.warning("[Remote Call] {}: {}", self.funcname, error)
            return None, False

    def _handle_open_state(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[T | None, bool]:
        try:
            sync_func = cast(Callable[P, T], self.func)
            result = sync_func(*args, **kwargs)

            with self._sync_lock:
                self.state = StateEnum.CLOSED
                self._failed_attempt_count = 0
                self._last_attempt_timestamp = datetime_with_tz()
            return result, True

        except self.exceptions_to_catch as error:
            with self._sync_lock:
                self._failed_attempt_count += 1
                self._last_attempt_timestamp = datetime_with_tz()
                self.state = StateEnum.OPEN

            logger.warning("[Remote Call] {}: {}", self.funcname, error)
            return None, False

    async def _ahandle_closed_state(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[T | None, bool]:
        try:
            async_func = cast(Callable[P, Coroutine[Any, Any, T]], self.func)
            result = await async_func(*args, **kwargs)
            self._last_attempt_timestamp = datetime_with_tz()
            return result, True
        except self.exceptions_to_catch as error:
            self._failed_attempt_count += 1
            self._last_attempt_timestamp = datetime_with_tz()

            if self._failed_attempt_count >= self.threshold:
                self.state = StateEnum.OPEN

            logger.warning("[Remote Call] {}: {}", self.funcname, error)
            return None, False

    async def _ahandle_open_state(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[T | None, bool]:
        currtimestamp = datetime_with_tz()
        last_attempt_timestamp = self._last_attempt_timestamp

        if last_attempt_timestamp is None:
            return None, False

        retry_timestamp = last_attempt_timestamp + timedelta(seconds=self.delay)

        if retry_timestamp >= currtimestamp:
            logger.warning(
                "[Remote Call] Retry {} after {} secs",
                self.funcname,
                retry_timestamp - currtimestamp,
            )
            return None, False

        self.state = StateEnum.HALF_OPEN

        try:
            async_func = cast(Callable[P, Coroutine[Any, Any, T]], self.func)
            result = await async_func(*args, **kwargs)
            self.state = StateEnum.CLOSED
            self._failed_attempt_count = 0
            self._last_attempt_timestamp = datetime_with_tz()
            return result, True

        except self.exceptions_to_catch as error:
            self._failed_attempt_count += 1
            self._last_attempt_timestamp = datetime_with_tz()
            self.state = StateEnum.OPEN
            logger.warning("[Remote Call] {}: {}", self.funcname, error)
            return None, False


circuit_breaker = CircuitBreaker
