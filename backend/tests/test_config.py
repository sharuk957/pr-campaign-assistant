import os
from unittest.mock import patch

from app.core.config import Settings


def test_default_settings() -> None:
    settings = Settings()
    assert settings.PROJECT_NAME == "PR Campaign Assistant API"
    assert settings.ENVIRONMENT == "development"
    assert "sqlite" in settings.DATABASE_URL
    assert settings.FRONTEND_ORIGIN == "http://localhost:5173"


def test_custom_environment_settings() -> None:
    custom_env = {
        "PROJECT_NAME": "Custom PR API",
        "ENVIRONMENT": "production",
        "DATABASE_URL": "sqlite:///./custom.db",
        "FRONTEND_ORIGIN": "https://app.example.com",
    }
    with patch.dict(os.environ, custom_env, clear=False):
        settings = Settings()
        assert settings.PROJECT_NAME == "Custom PR API"
        assert settings.ENVIRONMENT == "production"
        assert settings.DATABASE_URL == "sqlite:///./custom.db"
        assert settings.FRONTEND_ORIGIN == "https://app.example.com"
