from typing import Any, Self, TypedDict

import httpx2


class ClientExtensions(TypedDict, total=False):
    route: str


class BaseClient:
    """Thin HTTPX2 wrapper that carries route metadata to request hooks."""

    def __init__(self, client: httpx2.AsyncClient) -> None:
        self.client = client

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.client.aclose()

    async def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        extensions: ClientExtensions | None = None,
    ) -> httpx2.Response:
        return await self.client.get(url, params=params, extensions=extensions)

    async def post(
        self,
        url: str,
        *,
        json: Any | None = None,
        extensions: ClientExtensions | None = None,
    ) -> httpx2.Response:
        return await self.client.post(url, json=json, extensions=extensions)
