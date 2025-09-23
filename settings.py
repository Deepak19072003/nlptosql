from typing import Optional, Set
import os
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API / LLM
    gemini_api_key: str
    gemini_model: Optional[str] = "gemini-1.5-flash"

    # Database
    database_url: str

    # App constraints
    allowed_tables: Set[str] = {"customers", "products", "orders"}
    max_limit: int = 200
    statement_timeout_ms: int = 5000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("gemini_api_key", "database_url")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Environment variable is required and cannot be empty")
        return v


settings = Settings()


