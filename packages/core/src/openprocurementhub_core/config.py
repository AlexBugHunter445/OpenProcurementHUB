"""Validated settings loaded from environment and optional YAML profiles."""
from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPH_", env_file=".env", extra="ignore")
    env: Literal["development", "testing", "production"] = "development"
    database_url: str = "sqlite+pysqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/0"
    opensearch_url: str = "http://localhost:9200"
    anonymous_read: bool = True
    api_keys: list[str] = Field(default_factory=list)
    log_level: str = "INFO"

def load_settings(config_file: Path | None = None) -> Settings:
    data = yaml.safe_load(config_file.read_text()) if config_file and config_file.exists() else {}
    return Settings(**(data or {}))
