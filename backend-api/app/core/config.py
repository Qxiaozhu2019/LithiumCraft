from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    API_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://lithiumcraft:lithiumcraft@postgres:5432/lithiumcraft"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET_KEY: str = "change-this-in-production"
    JWT_EXPIRE_MINUTES: int = 720
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "ChangeMe123!"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    CRAWLER_USER_AGENT: str = "LithiumCraftBot/0.1 (+https://example.com; compliance contact: ops@example.com)"
    DEFAULT_DOMAIN_DELAY_SECONDS: float = 3.0
    DEFAULT_DAILY_LIMIT: int = 100
    AI_PROVIDER: str = "stub"
    AI_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.CORS_ORIGINS.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
