import time
from collections.abc import Awaitable, Callable

import httpx2
from locust.env import Environment


async def locust_request_event_hook(request: httpx2.Request) -> None:
    """Store request start time for the response hook."""

    request.extensions["start_time"] = time.perf_counter()


def locust_response_event_hook(
    environment: Environment,
) -> Callable[[httpx2.Response], Awaitable[None]]:
    """Build an HTTPX2 response hook that reports request metrics to Locust."""

    async def handle_response(response: httpx2.Response) -> None:
        exception: Exception | None = None

        try:
            response.raise_for_status()
        except httpx2.HTTPError as error:
            exception = error

        request = response.request
        route = request.extensions.get("route", request.url.path)
        start_time = request.extensions.get("start_time", time.perf_counter())

        environment.events.request.fire(
            request_type="HTTP",
            name=f"{request.method} {route}",
            response_time=(time.perf_counter() - start_time) * 1000,
            response_length=len(await response.aread()),
            response=response,
            exception=exception,
            context=None,
        )

    return handle_response
