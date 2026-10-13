import logging
from functools import cached_property
from typing import Final, Self

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="POSTGRES_",
        env_ignore_empty=True,
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 5432
    username: str = "username"
    password: SecretStr = SecretStr("password")
    database: str = "database"
    dbschema: str = "auth"
    echo: bool = False
    pool_recycle: int = 20
    pool_size: int = 10
    max_pool_size: int = 10
    pool_pre_ping: bool = True

    @cached_property
    def dsn(self) -> str:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=self.database,
        ).unicode_string()

    @cached_property
    def idx_naming_convention(self) -> dict[str, str]:
        return {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }


class HasherSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="HASHER_",
        env_ignore_empty=True,
        extra="ignore",
    )

    time_cost: int = 2
    memory_cost: int = 51200
    parallelism: int = 1
    hash_len: int = 32
    salt_len: int = 16


class JwtSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="JWT_",
        env_ignore_empty=True,
        extra="ignore",
    )

    private_key: SecretStr
    public_key: SecretStr
    access_token_ttl_seconds: int = Field(default=900, gt=0)
    refresh_token_ttl_seconds: int = Field(default=2_592_000, gt=0)
    algo_access: str = "RS256"
    algo_refresh: str = "SHA-256"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        nested_model_default_partial_update=True,
        extra="ignore",
        frozen=True,
    )

    debug: bool = False
    postgres: DatabaseSettings = DatabaseSettings()
    hasher: HasherSettings = HasherSettings()
    jwt: JwtSettings = JwtSettings()

    @classmethod
    def create_settings(cls) -> Self:
        settings = cls()

        if settings.debug:
            logger = logging.getLogger(__name__)
            logger.info(settings.model_dump_json(indent=4))

        return settings


settings: Final[Settings] = Settings.create_settings()
