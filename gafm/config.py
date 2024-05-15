from ipaddress import IPv4Address, IPv6Address
from pathlib import Path
from typing import Annotated, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

NetworkPort = Annotated[int, Field(ge=0, le=65535)]


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GAFM_REDIS_", extra="ignore")

    host: IPv4Address | IPv6Address | str = Field(
        default=IPv4Address("127.0.0.1"),
        description="The IP address or hostname for the Redis server",
    )
    port: NetworkPort = Field(default=6379, description="The port Redis is listening on")


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GAFM_", extra="ignore")

    bind_address: IPv4Address | IPv6Address = Field(
        default=IPv4Address("127.0.0.1"), description="The interface that GAFM will listen on"
    )
    hot_reload: bool = Field(
        default=False, description="Whether or not to reload GAFM automatically when code changes"
    )
    max_cache_size: Annotated[int, Field(ge=0)] = Field(
        default=65536, description="The maximum number of randomly generated responses to cache"
    )
    max_subdirs: int = Field(
        default=24,
        description="The maximum number of subdirectories to include in a response",
        gt=1,
        le=4096,
    )
    min_subdirs: int = Field(
        default=3,
        description="The maximum number of subdirectories to include in a response",
        gt=1,
        le=4096,
    )
    port: NetworkPort = Field(default=8080, description="The port that GAFM will listen on")
    redis: RedisConfig = Field(default_factory=RedisConfig)
    ssl_certfile: Path | None = Field(
        default=None,
        description="The path to an SSL certificate file; if this is not set, HTTP will be used.",
    )
    ssl_keyfile: Path | None = Field(
        default=None,
        description="The path to an SSL certificate file; if this is not set, HTTP will be used.",
    )

    @model_validator(mode="after")
    def validate_subdirs(self) -> Self:
        if self.min_subdirs > self.max_subdirs:
            raise ValueError("min_subdirs must be less than or equal to max_subdirs")

        return self

    @model_validator(mode="after")
    def validate_ssl(self) -> Self:
        if (self.ssl_certfile is not None and self.ssl_keyfile is None) or (
            self.ssl_certfile is None and self.ssl_keyfile is not None
        ):
            raise ValueError("ssl_cert and ssl_keyfile must be set together")

        return self


def load_config(env_file: Path = Path.cwd() / ".env") -> Config:
    _redis_config = RedisConfig(_env_file=env_file)
    return Config(_env_file=env_file, redis=_redis_config)
