from typing import Any, Optional, Protocol
import httpx

from app.ai.errors import AIProviderError
from app.core.config import get_settings


class LLMClient(Protocol):
    """Interface any AI provider client must satisfy to be used by AIService."""

    def complete(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.3) -> str: ...


class GroqClient:
    """Thin HTTP client for the Groq chat completions API.

    This is the only place in the application that talks to the LLM provider directly.
    """

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
    DEFAULT_MODEL = "openai/gpt-oss-120b"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.GROQ_API_KEY
        self.model = model or self.DEFAULT_MODEL
        self.timeout = timeout

    def complete(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.3) -> str:
        if not self.api_key:
            raise AIProviderError("GROQ_API_KEY is not configured")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(self.BASE_URL, json=payload, headers=headers, timeout=self.timeout)
        except httpx.RequestError as exc:
            raise AIProviderError(f"Failed to reach the AI provider: {exc}") from exc

        if response.status_code != 200:
            raise AIProviderError(
                f"AI provider returned an error (status {response.status_code})",
                details=self._safe_json(response),
            )

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("AI provider response was malformed", details=data) from exc

    @staticmethod
    def _safe_json(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text
