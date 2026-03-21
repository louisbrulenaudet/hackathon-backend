import time
from functools import lru_cache
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as importlib_version

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict

__all__ = [
    "Settings",
    "get_settings",
]


def _get_package_version() -> str:
    """
    Return the installed distribution version from package metadata (see `pyproject.toml`).
    """
    try:
        return importlib_version("backend")
    except PackageNotFoundError:
        return "0.0.0"


class Settings(BaseSettings):
    """
    Configuration settings for the application, using Pydantic for validation.
    """

    name: str = Field(default="Backend", alias="APP_NAME")
    version: str = Field(default_factory=_get_package_version)
    service_start_time: float = Field(default_factory=time.time, exclude=True)
    api_key: str = Field(default="", alias="API_KEY")
    api_client: str = Field(default="", alias="API_CLIENT")
    force_https: bool = Field(default=False, alias="FORCE_HTTPS")

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached application settings. Use with FastAPI Depends() for testability.
    """
    settings = Settings()

    return settings
