import json
import pytest

from app.ai.errors import AIProviderError, AIResponseError
from app.ai.schemas import AnalysisResult, CampaignContext, JournalistContext, PitchResult
from app.ai.service import AIService

CAMPAIGN = CampaignContext(
    name="AI Developer Security Launch",
    company_name="Acme Security",
    product_description="AI security analyzer for Python apps",
    campaign_description="Launching automated vulnerability scanner",
    target_audience="DevOps leads and Python engineers",
    key_topics="AI, Cybersecurity, Python, Developer Tools",
    desired_outcome="Earn press coverage in major tech journals",
)

JOURNALIST = JournalistContext(
    name="Emma Smith",
    publication="Tech Weekly",
    role="Technology Writer",
    topics="AI;Developer Tools;Python",
    bio="Covers developer tools and AI",
    recent_articles="AI coding tools;Python security",
)

VALID_ANALYSIS_JSON = json.dumps(
    {
        "score": 88,
        "priority": "high",
        "reasons": ["Covers AI and developer tools"],
        "supporting_evidence": ["Topic: AI", "Topic: Developer Tools"],
        "concerns": [],
    }
)

VALID_PITCH_JSON = json.dumps(
    {
        "subject": "AI Security for Python Developers",
        "body": "Hi Emma, given your coverage of AI and developer tools...",
    }
)


class FakeClient:
    def __init__(self, response: str = "", error: Exception | None = None):
        self.response = response
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def complete(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.3) -> str:
        self.calls.append((system_prompt, user_prompt))
        if self.error:
            raise self.error
        return self.response


def test_analyze_journalist_returns_parsed_analysis_result() -> None:
    client = FakeClient(response=VALID_ANALYSIS_JSON)
    service = AIService(client=client)

    result = service.analyze_journalist(CAMPAIGN, JOURNALIST)

    assert isinstance(result, AnalysisResult)
    assert result.score == 88
    assert result.priority == "high"
    assert result.reasons == ["Covers AI and developer tools"]
    assert len(client.calls) == 1
    assert JOURNALIST.name in client.calls[0][1]
    assert CAMPAIGN.name in client.calls[0][1]


def test_generate_pitch_returns_parsed_pitch_result() -> None:
    client = FakeClient(response=VALID_PITCH_JSON)
    service = AIService(client=client)

    analysis = AnalysisResult.model_validate(json.loads(VALID_ANALYSIS_JSON))
    result = service.generate_pitch(CAMPAIGN, JOURNALIST, analysis)

    assert isinstance(result, PitchResult)
    assert result.subject == "AI Security for Python Developers"
    assert "Emma" in result.body


def test_analyze_journalist_propagates_provider_error() -> None:
    client = FakeClient(error=AIProviderError("provider is down"))
    service = AIService(client=client)

    with pytest.raises(AIProviderError, match="provider is down"):
        service.analyze_journalist(CAMPAIGN, JOURNALIST)


def test_analyze_journalist_wraps_unexpected_client_error() -> None:
    client = FakeClient(error=RuntimeError("boom"))
    service = AIService(client=client)

    with pytest.raises(AIProviderError, match="Unexpected error"):
        service.analyze_journalist(CAMPAIGN, JOURNALIST)


def test_analyze_journalist_rejects_invalid_json() -> None:
    client = FakeClient(response="not valid json")
    service = AIService(client=client)

    with pytest.raises(AIResponseError, match="not valid JSON"):
        service.analyze_journalist(CAMPAIGN, JOURNALIST)


def test_analyze_journalist_rejects_out_of_range_score() -> None:
    invalid_json = json.dumps(
        {
            "score": 150,
            "priority": "high",
            "reasons": ["reason"],
            "supporting_evidence": ["evidence"],
            "concerns": [],
        }
    )
    client = FakeClient(response=invalid_json)
    service = AIService(client=client)

    with pytest.raises(AIResponseError, match="expected schema"):
        service.analyze_journalist(CAMPAIGN, JOURNALIST)


def test_analyze_journalist_rejects_invalid_priority() -> None:
    invalid_json = json.dumps(
        {
            "score": 80,
            "priority": "urgent",
            "reasons": ["reason"],
            "supporting_evidence": ["evidence"],
            "concerns": [],
        }
    )
    client = FakeClient(response=invalid_json)
    service = AIService(client=client)

    with pytest.raises(AIResponseError):
        service.analyze_journalist(CAMPAIGN, JOURNALIST)


def test_analyze_journalist_rejects_missing_required_fields() -> None:
    incomplete_json = json.dumps({"score": 80, "priority": "high"})
    client = FakeClient(response=incomplete_json)
    service = AIService(client=client)

    with pytest.raises(AIResponseError):
        service.analyze_journalist(CAMPAIGN, JOURNALIST)


def test_generate_pitch_rejects_missing_required_fields() -> None:
    incomplete_json = json.dumps({"subject": "Hello"})
    client = FakeClient(response=incomplete_json)
    service = AIService(client=client)

    analysis = AnalysisResult.model_validate(json.loads(VALID_ANALYSIS_JSON))
    with pytest.raises(AIResponseError):
        service.generate_pitch(CAMPAIGN, JOURNALIST, analysis)


def test_default_client_is_groq_client() -> None:
    from app.ai.client import GroqClient

    service = AIService()
    assert isinstance(service.client, GroqClient)
