from typing import override

from starlette.datastructures import Headers, MutableHeaders
from starlette.middleware.cors import CORSMiddleware
from starlette.types import Message, Send


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
