import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AWS_ENDPOINT_URL: str = ""
    AWS_REGION: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def is_aws_lambda_environment() -> bool:
        return "AWS_LAMBDA_FUNCTION_NAME" in os.environ


@lru_cache
def get_settings() -> Settings:
    return Settings()
