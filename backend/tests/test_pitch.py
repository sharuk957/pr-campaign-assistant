from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.ai.errors import AIProviderError
from app.ai.schemas import AnalysisResult, PitchResult
from app.api.routes.analysis import get_analysis_service
from app.api.routes.pitches import get_pitch_service
from app.main import app
from app.models.analysis import Analysis
from app.models.campaign import Campaign
from app.models.journalist import Journalist
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.journalist_repository import JournalistRepository
from app.services.analysis_service import AnalysisService
from app.services.pitch_service import PitchService

CAMPAIGN_PAYLOAD = {
    "name": "AI Developer Security Launch",
    "company_name": "Acme Security",
    "product_description": "AI security analyzer for Python apps",
    "campaign_description": "Launching automated vulnerability scanner",
    "target_audience": "DevOps leads and Python engineers",
    "key_topics": "AI, Cybersecurity, Python, Developer Tools",
    "desired_outcome": "Earn press coverage in major tech journals",
}


class FakeAnalysisAIService:
    def analyze_journalist(self, campaign, journalist):
        return AnalysisResult(
            score=85,
            priority="high",
            reasons=["Strong topical overlap"],
            supporting_evidence=["Topic: AI"],
            concerns=[],
        )


class FakePitchAIService:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def generate_pitch(self, campaign, journalist, analysis):
        self.calls.append((campaign, journalist, analysis))
        if self.error:
            raise self.error
        return self.result or PitchResult(
            subject="A story idea for you",
            body="Hi there, given your coverage of AI and developer tools, we have a story for you.",
        )


def override_analysis_service():
    def _override() -> AnalysisService:
        return AnalysisService(ai_service=FakeAnalysisAIService())

    return _override


def override_pitch_service(fake_ai_service):
    def _override() -> PitchService:
        return PitchService(ai_service=fake_ai_service)

    return _override


def create_campaign(client: TestClient) -> str:
    response = client.post("/api/campaigns", json=CAMPAIGN_PAYLOAD)
    assert response.status_code == 201
    return response.json()["id"]


def create_journalist(client: TestClient, campaign_id: str, name: str = "Emma Smith") -> str:
    response = client.post(
        f"/api/campaigns/{campaign_id}/journalists",
        json={
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}@example.com",
            "publication": "Tech Weekly",
            "role": "Writer",
            "topics": "AI;Developer Tools",
            "bio": "Covers developer tools and AI",
            "recent_articles": "AI coding tools",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def run_analysis(client: TestClient, campaign_id: str) -> None:
    app.dependency_overrides[get_analysis_service] = override_analysis_service()
    try:
        response = client.post(f"/api/campaigns/{campaign_id}/analysis")
        assert response.status_code == 200
    finally:
        del app.dependency_overrides[get_analysis_service]


def test_generate_pitch_requires_prior_analysis(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    journalist_id = create_journalist(client, campaign_id)

    fake_ai_service = FakePitchAIService()
    app.dependency_overrides[get_pitch_service] = override_pitch_service(fake_ai_service)
    try:
        response = client.post(f"/api/campaigns/{campaign_id}/journalists/{journalist_id}/pitch")
    finally:
        del app.dependency_overrides[get_pitch_service]

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"
    assert len(fake_ai_service.calls) == 0


def test_generate_pitch_success_includes_campaign_journalist_and_analysis(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    journalist_id = create_journalist(client, campaign_id)
    run_analysis(client, campaign_id)

    fake_ai_service = FakePitchAIService(
        result=PitchResult(subject="Exclusive AI security story", body="Hi Emma, ...")
    )
    app.dependency_overrides[get_pitch_service] = override_pitch_service(fake_ai_service)
    try:
        response = client.post(f"/api/campaigns/{campaign_id}/journalists/{journalist_id}/pitch")
    finally:
        del app.dependency_overrides[get_pitch_service]

    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Exclusive AI security story"
    assert data["campaign_id"] == campaign_id
    assert data["journalist_id"] == journalist_id

    assert len(fake_ai_service.calls) == 1
    campaign_context, journalist_context, analysis_result = fake_ai_service.calls[0]
    assert campaign_context.name == CAMPAIGN_PAYLOAD["name"]
    assert journalist_context.name == "Emma Smith"
    assert analysis_result.score == 85


def test_generate_pitch_is_stored_and_retrievable(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    journalist_id = create_journalist(client, campaign_id)
    run_analysis(client, campaign_id)

    fake_ai_service = FakePitchAIService()
    app.dependency_overrides[get_pitch_service] = override_pitch_service(fake_ai_service)
    try:
        client.post(f"/api/campaigns/{campaign_id}/journalists/{journalist_id}/pitch")
        get_response = client.get(f"/api/campaigns/{campaign_id}/journalists/{journalist_id}/pitch")
    finally:
        del app.dependency_overrides[get_pitch_service]

    assert get_response.status_code == 200
    assert get_response.json()["journalist_id"] == journalist_id


def test_get_pitch_before_generation_returns_404(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    journalist_id = create_journalist(client, campaign_id)
    run_analysis(client, campaign_id)

    response = client.get(f"/api/campaigns/{campaign_id}/journalists/{journalist_id}/pitch")
    assert response.status_code == 404


def test_regenerating_pitch_replaces_previous_pitch(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    journalist_id = create_journalist(client, campaign_id)
    run_analysis(client, campaign_id)

    first_service = FakePitchAIService(result=PitchResult(subject="First draft", body="Body one"))
    app.dependency_overrides[get_pitch_service] = override_pitch_service(first_service)
    try:
        first_response = client.post(f"/api/campaigns/{campaign_id}/journalists/{journalist_id}/pitch")
    finally:
        del app.dependency_overrides[get_pitch_service]
    first_id = first_response.json()["id"]

    second_service = FakePitchAIService(result=PitchResult(subject="Regenerated draft", body="Body two"))
    app.dependency_overrides[get_pitch_service] = override_pitch_service(second_service)
    try:
        second_response = client.post(f"/api/campaigns/{campaign_id}/journalists/{journalist_id}/pitch")
    finally:
        del app.dependency_overrides[get_pitch_service]

    assert second_response.status_code == 200
    data = second_response.json()
    assert data["subject"] == "Regenerated draft"
    assert data["id"] == first_id  # same stored row, updated in place


def test_generate_pitch_provider_failure_returns_502(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    journalist_id = create_journalist(client, campaign_id)
    run_analysis(client, campaign_id)

    fake_ai_service = FakePitchAIService(error=AIProviderError("AI provider timed out"))
    app.dependency_overrides[get_pitch_service] = override_pitch_service(fake_ai_service)
    try:
        response = client.post(f"/api/campaigns/{campaign_id}/journalists/{journalist_id}/pitch")
    finally:
        del app.dependency_overrides[get_pitch_service]

    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "AI_GENERATION_FAILED"
    assert "timed out" in data["error"]["message"]


def test_generate_pitch_for_missing_journalist_returns_404(client: TestClient) -> None:
    campaign_id = create_campaign(client)

    response = client.post(f"/api/campaigns/{campaign_id}/journalists/non-existent-id/pitch")
    assert response.status_code == 404


def test_pitch_service_and_repository_directly(db_session: Session) -> None:
    campaign = CampaignRepository().create(
        db_session,
        Campaign(
            name="Direct Service Campaign",
            company_name="Acme",
            product_description="Product",
            campaign_description="Story",
            target_audience="Target",
            key_topics="AI;Dev",
            desired_outcome="Coverage",
        ),
    )
    journalist = JournalistRepository().create(
        db_session,
        Journalist(
            campaign_id=campaign.id,
            name="Emma Smith",
            email="emma@example.com",
            publication="Tech Weekly",
            role="Writer",
            topics="AI",
            bio="Bio",
            recent_articles="Articles",
        ),
    )
    AnalysisRepository().upsert(
        db_session,
        campaign.id,
        journalist.id,
        AnalysisResult(
            score=90, priority="high", reasons=["Great fit"], supporting_evidence=["Evidence"], concerns=[]
        ),
    )

    fake_ai_service = FakePitchAIService(
        result=PitchResult(subject="Direct subject", body="Direct body")
    )
    service = PitchService(ai_service=fake_ai_service)

    pitch = service.generate_pitch(db_session, campaign.id, journalist.id)
    assert pitch.subject == "Direct subject"

    fetched = service.get_pitch(db_session, campaign.id, journalist.id)
    assert fetched.id == pitch.id
