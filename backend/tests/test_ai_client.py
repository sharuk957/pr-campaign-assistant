import httpx
import pytest

from app.ai.client import GroqClient
from app.ai.errors import AIProviderError


class FakeResponse:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json_data = json_data

    def json(self) -> dict:
        return self._json_data


def make_success_payload(content: str) -> dict:
    return {"choices": [{"message": {"content": content}}]}


def test_complete_success_returns_message_content(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url, json, headers, timeout):
        assert url == GroqClient.BASE_URL
        assert headers["Authorization"] == "Bearer test-key"
        return FakeResponse(200, make_success_payload('{"score": 90}'))

    monkeypatch.setattr("app.ai.client.httpx.post", fake_post)

    client = GroqClient(api_key="test-key")
    result = client.complete("system prompt", "user prompt")

    assert result == '{"score": 90}'


def test_complete_without_api_key_raises_provider_error() -> None:
    client = GroqClient(api_key="")

    with pytest.raises(AIProviderError, match="not configured"):
        client.complete("system prompt", "user prompt")


def test_complete_network_error_raises_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url, json, headers, timeout):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr("app.ai.client.httpx.post", fake_post)

    client = GroqClient(api_key="test-key")
    with pytest.raises(AIProviderError, match="Failed to reach the AI provider"):
        client.complete("system prompt", "user prompt")


def test_complete_non_200_status_raises_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url, json, headers, timeout):
        return FakeResponse(401, {"error": "invalid api key"})

    monkeypatch.setattr("app.ai.client.httpx.post", fake_post)

    client = GroqClient(api_key="test-key")
    with pytest.raises(AIProviderError) as exc_info:
        client.complete("system prompt", "user prompt")

    assert "status 401" in str(exc_info.value)
    assert exc_info.value.details == {"error": "invalid api key"}


def test_complete_malformed_success_body_raises_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url, json, headers, timeout):
        return FakeResponse(200, {"unexpected": "shape"})

    monkeypatch.setattr("app.ai.client.httpx.post", fake_post)

    client = GroqClient(api_key="test-key")
    with pytest.raises(AIProviderError, match="malformed"):
        client.complete("system prompt", "user prompt")
