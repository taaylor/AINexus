import logging

import httpx2

from auth.tests.perfomance.api.base_client import BaseClient
from auth.tests.perfomance.settings import HttpClientSettings


def get_http_client(config: HttpClientSettings) -> BaseClient:
    """Create a reusable HTTPX2 client without Locust instrumentation."""

    logging.getLogger("httpx2").setLevel(logging.WARNING)

    return BaseClient(
        httpx2.AsyncClient(
            timeout=config.timeout,
            base_url=config.client_url,
        ),
    )
