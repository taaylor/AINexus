from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TraceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="TRACE_",
        env_ignore_empty=True,
        extra="ignore",
        frozen=True,
    )

    otlp_endpoint: str = "http://localhost:4317"
    insecure: bool = True
    sample_ratio: float = Field(default=0.8, ge=0.0, le=1.0)


settings: Final[TraceSettings] = TraceSettings()
