"""Configuration management for ContractML."""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    api_title: str = "ContractML"
    api_description: str = "Runtime-executable Pydantic contracts for ML inference"
    api_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Performance
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    request_timeout: int = 30

    # Security
    enable_cors: bool = True
    cors_origins: List[str] = ["*"]

    # Model settings
    model_cache_size: int = 100
    model_timeout: int = 10

    # Paths
    schemas_path: str = "schemas"
    models_path: str = "models"

    model_config = {"env_prefix": "CONTRACTML_", "env_file": ".env"}


# Global settings instance
settings = Settings()
