"""Application configuration loaded from environment variables.

This module uses pydantic-settings to load and validate configuration
from environment variables with type safety and sensible defaults.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings can be overridden via environment variables.
    Prefix GHL_ is used for all settings (e.g., GHL_DATABASE_HOST).
    """

    model_config = SettingsConfigDict(
        env_prefix="GHL_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(
        default="GoHighLevel Clone",
        description="Application name displayed in API docs",
    )
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment",
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 route prefix")

    # Database
    database_host: str = Field(default="localhost", description="PostgreSQL host")
    database_port: int = Field(default=5432, description="PostgreSQL port")
    database_user: str = Field(default="postgres", description="PostgreSQL user")
    database_password: str = Field(default="postgres", description="PostgreSQL password")
    database_name: str = Field(default="gohighlevel", description="PostgreSQL database name")
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Max overflow connections")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """Build async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url_sync(self) -> str:
        """Build sync PostgreSQL connection URL for Alembic."""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    # Redis
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: str | None = Field(default=None, description="Redis password")
    redis_db: int = Field(default=0, description="Redis database number")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def redis_url(self) -> str:
        """Build Redis connection URL."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Security
    secret_key: str = Field(
        default="change-me-in-production-use-openssl-rand-hex-32",
        description="Secret key for JWT signing",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes",
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration in days",
    )

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100,
        description="Maximum requests per rate limit window",
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Rate limit window in seconds",
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # Clerk Authentication
    clerk_secret_key: str | None = Field(
        default=None,
        description="Clerk secret key for authentication",
    )
    clerk_publishable_key: str | None = Field(
        default=None,
        description="Clerk publishable key",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Global settings instance for convenience
settings = get_settings()
