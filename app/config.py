"""
Configuration settings for the FastAPI application.
This module defines the configuration variables and their default values.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

IS_PRODUCTION = os.getenv("ENV") == "production"

class Settings(BaseSettings):
    """Configuration settings for the FastAPI application."""
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None
    DATABASE_URL_SYNC: str | None = None

    APP_NAME: str = "기억공간 - Gieok Gonggan"
    DEBUG: bool = False
    ENV: str = "development"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43_200
    API_CLIENT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 43_200
    ALGORITHM: str = "HS256"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    SHOW_DOCS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env" if not IS_PRODUCTION else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def database_url(self) -> str:
        """
        Construct the database URL for SQLAlchemy.
        :return: The database URL.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def database_url_sync(self) -> str:
        """
        Construct the synchronous database URL for SQLAlchemy.
        :return: The synchronous database URL.
        """
        if self.DATABASE_URL_SYNC:
            return self.DATABASE_URL_SYNC
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()
