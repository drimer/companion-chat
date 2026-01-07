import logging
import os
from functools import lru_cache

from fastapi import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AWS_ENDPOINT_URL: str = ""
    AWS_REGION: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None

    DB_CONVERSATIONS_TABLE_NAME: str = ""

    USE_MOCK_OPENAI: bool = False

    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    MAX_TOKENS: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def is_aws_lambda_environment(self) -> bool:
        return "AWS_LAMBDA_FUNCTION_NAME" in os.environ


@lru_cache
def get_settings() -> Settings:
    return Settings()


def configure_logging():
    stream_handler = logging.StreamHandler()
    log_formatter = logging.Formatter(
        "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
    )
    stream_handler.setFormatter(log_formatter)
    logger.logger.addHandler(stream_handler)
    logger.logger.setLevel("INFO")
