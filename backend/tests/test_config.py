import os
from unittest.mock import patch

from app.core.config import Settings


def test_default_settings() -> None:
    settings = Settings()
    assert settings.PROJECT_NAME == "PR Campaign Assistant API"
    assert settings.ENVIRONMENT == "development"
    assert "sqlite" in settings.DATABASE_URL
    assert "http://localhost:5173" in settings.cors_origins
    assert "http://127.0.0.1:5173" in settings.cors_origins


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
        assert "https://app.example.com" in settings.cors_origins
