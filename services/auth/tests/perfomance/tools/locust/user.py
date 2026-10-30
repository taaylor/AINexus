from locust import HttpUser, between

from auth.tests.perfomance.settings import settings


class BaseLocustUser(HttpUser):
    """
    Abstract base User virtual
    """

    abstract = True
    host = settings.auth_api_http_client.client_url
    wait_time = between(3.0, 5.0)
