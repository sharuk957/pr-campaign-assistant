from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "PR Campaign Assistant API"
    ENVIRONMENT: str = "development"
    FRONTEND_ORIGIN: str = "http://localhost:5173,http://127.0.0.1:5173"
    DATABASE_URL: str = "sqlite:///./pr_campaign_assistant.db"
    GROQ_API_KEY: Optional[str] = None

    @property
    def cors_origins(self) -> list[str]:
        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        if self.FRONTEND_ORIGIN:
            for item in self.FRONTEND_ORIGIN.split(","):
                item_clean = item.strip().rstrip("/")
                if item_clean and item_clean not in origins:
                    origins.append(item_clean)
        return origins


@lru_cache()
def get_settings() -> Settings:
    return Settings()
