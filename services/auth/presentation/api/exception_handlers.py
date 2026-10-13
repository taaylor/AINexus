from __future__ import annotations

from collections.abc import Callable, Coroutine, Sequence
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Final

from fastapi.responses import JSONResponse
from loguru import logger as log
from starlette.requests import Request
from starlette.responses import Response

from auth.common.exceptions.application import ServiceUnavailableException
from auth.common.exceptions.base import (
    AppException,
    ApplicationException,
    ConflictException,
    DomainException,
    InfrastructureException,
    PresenterException,
)
from auth.common.exceptions.presenter import DTOValidationException

type ExceptionHandler = Callable[[Request, Any], Coroutine[Any, Any, Response]]
type ExceptionHandlersType = Sequence[ExceptionHandlerItem[ExceptionHandler]]


@dataclass(frozen=True, slots=True, kw_only=True)
class ExceptionHandlerItem[THandler]:
    exception: type[Exception]
    handler: ExceptionHandler


EXCEPTION_TO_STATUS_MAP: Final[dict[type[Exception], HTTPStatus]] = {
    AppException: HTTPStatus.INTERNAL_SERVER_ERROR,
    ApplicationException: HTTPStatus.INTERNAL_SERVER_ERROR,
    InfrastructureException: HTTPStatus.SERVICE_UNAVAILABLE,
    PresenterException: HTTPStatus.UNPROCESSABLE_ENTITY,
    ServiceUnavailableException: HTTPStatus.SERVICE_UNAVAILABLE,
    ConflictException: HTTPStatus.CONFLICT,
    DTOValidationException: HTTPStatus.UNPROCESSABLE_ENTITY,
    DomainException: HTTPStatus.BAD_REQUEST,
    Exception: HTTPStatus.INTERNAL_SERVER_ERROR,
}


def _extract_exception_message(exc: Exception, fallback: str) -> str:
    for attr_name in ("message", "detail"):
        value = getattr(exc, attr_name, None)
        if isinstance(value, str) and value.strip():
            return value

    text = str(exc).strip()
    return text or fallback


def _response_content(exc: Exception, status: HTTPStatus) -> dict[str, object]:
    errors = getattr(exc, "errors", None)
    if errors is not None:
        content: dict[str, object] = {"detail": errors}
    else:
        content = {"detail": _extract_exception_message(exc, status.phrase)}

    for attr_name in ("username_exists", "email_exists", "code"):
        value = getattr(exc, attr_name, None)
        if value is not None:
            content[attr_name] = value

    return content


def make_exception_handler(
    exception_type: type[Exception],
    status: HTTPStatus,
) -> ExceptionHandler:
    async def handler(request: Request, exc: Any) -> JSONResponse:
        if status >= HTTPStatus.INTERNAL_SERVER_ERROR:
            log.opt(exception=(type(exc), exc, exc.__traceback__)).error(
                "Unhandled exception: {} {}",
                request.method,
                request.url.path,
            )
        else:
            log.warning(
                "Handled exception: {} {} status={} message={}",
                request.method,
                request.url.path,
                status.value,
                _extract_exception_message(exc, status.phrase),
            )

        return JSONResponse(
            status_code=status.value,
            content=_response_content(exc, status),
        )

    handler.__name__ = f"{exception_type.__name__}_handler"
    return handler


def build_exception_handlers(
    exception_to_status_map: dict[type[Exception], HTTPStatus] = EXCEPTION_TO_STATUS_MAP,
) -> dict[int | type[Exception], ExceptionHandler]:
    handlers: dict[int | type[Exception], ExceptionHandler] = {}
    for exception_type, status in exception_to_status_map.items():
        handlers[exception_type] = make_exception_handler(exception_type, status)
    return handlers


exception_handlers = build_exception_handlers()
