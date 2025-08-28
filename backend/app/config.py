from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    api_token: str | None = None
    llm_provider: str = "mock"  # openai|openrouter|together|mock
    openai_api_key: str | None = None
    openrouter_api_key: str | None = None
    together_api_key: str | None = None
    rate_limit_per_min: int = 20
    cors_origins: List[str] = ["*"]


def get_settings() -> Settings:
    return Settings()
