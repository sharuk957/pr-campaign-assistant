from typing import Any, Optional


class AIServiceError(Exception):
    """Base class for all errors raised by the AI integration layer."""

    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(message)


class AIProviderError(AIServiceError):
    """Raised when the LLM provider cannot be reached or returns an error."""


class AIResponseError(AIServiceError):
    """Raised when the provider responds but the content cannot be parsed into the expected structure."""
