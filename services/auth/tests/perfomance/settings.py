from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class HttpClientSettings(BaseModel):
    url: HttpUrl = HttpUrl("http://localhost:80")
    timeout: float = Field(default=10.0, gt=0)

    @property
    def client_url(self) -> str:
        return str(self.url)


class PerformanceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        env_nested_delimiter=".",
        nested_model_default_partial_update=True,
        extra="ignore",
        frozen=True,
    )

    auth_api_http_client: HttpClientSettings = HttpClientSettings()
    seed_users_count: PositiveInt = 10
    seeds_output_path: Path = Path(
        "services/auth/tests/perfomance/dumps/auth-users.json",
    )


settings = PerformanceSettings()
