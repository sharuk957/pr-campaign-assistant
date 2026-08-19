import json
import pytest

from app.ai.errors import AIResponseError
from app.ai.grounding import (
    build_vocabulary,
    extract_journalist_coverage_claims,
    find_ungrounded_items,
    tokenize,
)
from app.ai.schemas import CampaignContext, JournalistContext
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

# This journalist has no cybersecurity information anywhere in their profile.
JOURNALIST_WITHOUT_CYBERSECURITY = JournalistContext(
    name="Priya Patel",
    publication="Health Innovations",
    role="Health Tech Editor",
    topics="Healthcare;Digital Health;AI",
    bio="Reports on healthcare technology and policy",
    recent_articles="AI diagnostics;Telehealth regulation",
)


class FakeClient:
    def __init__(self, response: str):
        self.response = response

    def complete(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.3) -> str:
        return self.response


def test_tokenize_strips_stopwords_and_short_words() -> None:
    tokens = tokenize("You regularly cover the AI and Cybersecurity beat")
    assert "ai" in tokens
    assert "cybersecurity" in tokens
    assert "the" not in tokens
    assert "you" not in tokens


def test_build_vocabulary_combines_all_source_texts() -> None:
    vocabulary = build_vocabulary("AI;Developer Tools", "Covers Python", "Recent Python security piece")
    assert "developer" in vocabulary
    assert "python" in vocabulary
    assert "security" in vocabulary


def test_find_ungrounded_items_flags_only_unsupported_items() -> None:
    vocabulary = build_vocabulary("Healthcare;Digital Health;AI", "Reports on healthcare technology")
    items = ["Topic: AI", "Cybersecurity leadership award"]
    ungrounded = find_ungrounded_items(items, vocabulary)
    assert ungrounded == ["Cybersecurity leadership award"]


def test_extract_journalist_coverage_claims_matches_common_phrasings() -> None:
    text = "Given your regular coverage of cybersecurity threats, we think you'd love this story."
    claims = extract_journalist_coverage_claims(text)
    assert any("cybersecurity" in claim.lower() for claim in claims)


def test_extract_journalist_coverage_claims_ignores_campaign_only_language() -> None:
    text = "Our platform covers a wide range of vulnerabilities across Python codebases."
    claims = extract_journalist_coverage_claims(text)
    assert claims == []


def test_analyze_journalist_rejects_ungrounded_supporting_evidence() -> None:
    raw_response = json.dumps(
        {
            "score": 75,
            "priority": "medium",
            "reasons": ["Covers AI in healthcare"],
            "supporting_evidence": ["Cybersecurity beat reporter"],
            "concerns": [],
        }
    )
    service = AIService(client=FakeClient(raw_response))

    with pytest.raises(AIResponseError, match="not grounded"):
        service.analyze_journalist(CAMPAIGN, JOURNALIST_WITHOUT_CYBERSECURITY)


def test_analyze_journalist_accepts_grounded_supporting_evidence() -> None:
    raw_response = json.dumps(
        {
            "score": 40,
            "priority": "low",
            "reasons": ["Covers AI only within healthcare contexts"],
            "supporting_evidence": ["Topics Covered: Healthcare;Digital Health;AI"],
            "concerns": ["No cybersecurity coverage"],
        }
    )
    service = AIService(client=FakeClient(raw_response))

    result = service.analyze_journalist(CAMPAIGN, JOURNALIST_WITHOUT_CYBERSECURITY)
    assert result.score == 40


def test_generate_pitch_rejects_unsupported_coverage_claim() -> None:
    raw_response = json.dumps(
        {
            "subject": "Loved your cybersecurity reporting",
            "body": "Hi Priya, given your regular coverage of cybersecurity, we thought you'd want an exclusive.",
        }
    )
    service = AIService(client=FakeClient(raw_response))
    analysis = _make_analysis_result()

    with pytest.raises(AIResponseError, match="unsupported claims"):
        service.generate_pitch(CAMPAIGN, JOURNALIST_WITHOUT_CYBERSECURITY, analysis)


def test_generate_pitch_accepts_grounded_claims() -> None:
    raw_response = json.dumps(
        {
            "subject": "A healthcare AI story for you",
            "body": "Hi Priya, given your coverage of AI diagnostics in healthcare, we have a story for you.",
        }
    )
    service = AIService(client=FakeClient(raw_response))
    analysis = _make_analysis_result()

    result = service.generate_pitch(CAMPAIGN, JOURNALIST_WITHOUT_CYBERSECURITY, analysis)
    assert result.subject == "A healthcare AI story for you"


def _make_analysis_result():
    from app.ai.schemas import AnalysisResult

    return AnalysisResult(
        score=40,
        priority="low",
        reasons=["Covers AI only within healthcare contexts"],
        supporting_evidence=["Topics Covered: Healthcare;Digital Health;AI"],
        concerns=["No cybersecurity coverage"],
    )
