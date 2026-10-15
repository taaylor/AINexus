from typing import override

from loguru import logger
from starlette.datastructures import Headers, MutableHeaders
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class CorrectCORSMiddleware(CORSMiddleware):
    @override
    async def send(
        self,
        message: Message,
        send: Send,
        request_headers: Headers,
    ) -> None:
        if message["type"] != "http.response.start":
            await send(message)
            return

        message.setdefault("headers", [])
        headers = MutableHeaders(scope=message)

        origin = request_headers.get("Origin")

        if origin is not None:
            headers.update(self.simple_headers)

            if self.is_allowed_origin(origin=origin):
                self.allow_explicit_origin(headers, origin)

        await send(message)


class ExceptionLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception:
            logger.exception(
                "Unhandled request exception: method={} path={}",
                scope.get("method", "-"),
                scope.get("path", "-"),
            )
            raise
