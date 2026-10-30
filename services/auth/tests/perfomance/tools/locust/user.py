from locust import HttpUser, constant_throughput

from auth.tests.perfomance.settings import settings


class BaseLocustUser(HttpUser):
    """
    Abstract base User virtual
    """

    abstract = True
    host = settings.auth_api_http_client.url
    wait_time = constant_throughput(2)
