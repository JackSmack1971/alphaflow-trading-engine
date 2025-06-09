"""Configuration loading."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""

    redis_url: str
    db_url: str


def load_config() -> Config:
    """Load configuration from environment."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    db_url = os.getenv("DB_URL", "postgresql://localhost/db")
    return Config(redis_url=redis_url, db_url=db_url)
