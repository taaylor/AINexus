from typing import cast, override

from faker import Faker
from locust import HttpUser, SequentialTaskSet, TaskSet

from auth.tests.perfomance.api.auth_client import (
    LocustAuthApiClient,
    get_auth_locust_api_client,
)
from auth.tests.perfomance.settings import settings
from auth.tests.perfomance.tools.faker import fake


class BaseLocustTaskSet(TaskSet):
    fake: Faker
    auth_client: LocustAuthApiClient

    @override
    def on_start(self) -> None:
        self.fake = fake.faker
        self.auth_client = get_auth_locust_api_client(
            cast(HttpUser, self.user).client,
            settings.auth_api_http_client,
        )


class BaseLocustSequentialTaskSet(SequentialTaskSet):
    fake: Faker
    auth_client: LocustAuthApiClient

    @override
    def on_start(self) -> None:
        self.fake = fake.faker
        self.auth_client = get_auth_locust_api_client(
            cast(HttpUser, self.user).client,
            settings.auth_api_http_client,
        )
