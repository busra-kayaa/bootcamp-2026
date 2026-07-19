"""Application settings loaded from environment variables."""

from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configuration values for the FastAPI application."""

    app_name: str = "SprintMate AI Backend"  
    app_version: str = "0.1.0"
    debug: bool = True
    frontend_url: str = "http://localhost:5173"

    database_url: str = "postgresql+asyncpg://postgres:admin123@localhost:5432/sprintmate"
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_mode(cls, value: object) -> object:
        """Support common named development and release modes."""
        if isinstance(value, str):
            named_modes = {
                "debug": True,
                "development": True,
                "release": False,
                "production": False,
            }
            return named_modes.get(value.lower(), value)
        return value

@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()