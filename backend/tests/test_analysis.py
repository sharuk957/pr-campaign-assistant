from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.ai.errors import AIProviderError, AIResponseError
from app.ai.schemas import AnalysisResult
from app.api.routes.analysis import get_analysis_service
from app.main import app
from app.models.campaign import Campaign
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.journalist_repository import JournalistRepository
from app.models.journalist import Journalist
from app.services.analysis_service import AnalysisService

CAMPAIGN_PAYLOAD = {
    "name": "AI Developer Security Launch",
    "company_name": "Acme Security",
    "product_description": "AI security analyzer for Python apps",
    "campaign_description": "Launching automated vulnerability scanner",
    "target_audience": "DevOps leads and Python engineers",
    "key_topics": "AI, Cybersecurity, Python, Developer Tools",
    "desired_outcome": "Earn press coverage in major tech journals",
}


class FakeAIService:
    def __init__(self, results=None, errors=None):
        self.results = results or {}
        self.errors = errors or {}
        self.calls = []

    def analyze_journalist(self, campaign, journalist):
        self.calls.append((campaign, journalist))
        if journalist.name in self.errors:
            raise self.errors[journalist.name]
        return self.results.get(
            journalist.name,
            AnalysisResult(
                score=75,
                priority="medium",
                reasons=["Covers relevant topics"],
                supporting_evidence=["Topic: AI"],
                concerns=[],
            ),
        )


def override_analysis_service(fake_ai_service: FakeAIService):
    def _override() -> AnalysisService:
        return AnalysisService(ai_service=fake_ai_service)

    return _override


def create_campaign(client: TestClient) -> str:
    response = client.post("/api/campaigns", json=CAMPAIGN_PAYLOAD)
    assert response.status_code == 201
    return response.json()["id"]


def create_journalist(client: TestClient, campaign_id: str, name: str) -> str:
    response = client.post(
        f"/api/campaigns/{campaign_id}/journalists",
        json={
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}@example.com",
            "publication": "Tech Weekly",
            "role": "Writer",
            "topics": "AI;Developer Tools",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_run_analysis_persists_successful_results(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    create_journalist(client, campaign_id, "Emma Smith")
    create_journalist(client, campaign_id, "James Chen")

    fake_ai_service = FakeAIService(
        results={
            "Emma Smith": AnalysisResult(
                score=92,
                priority="high",
                reasons=["Strong AI coverage"],
                supporting_evidence=["Recent article on AI tooling"],
                concerns=[],
            ),
            "James Chen": AnalysisResult(
                score=60,
                priority="medium",
                reasons=["Some overlap"],
                supporting_evidence=["Topic: Cloud"],
                concerns=["Primarily covers security, not AI"],
            ),
        }
    )
    app.dependency_overrides[get_analysis_service] = override_analysis_service(fake_ai_service)
    try:
        response = client.post(f"/api/campaigns/{campaign_id}/analysis")
    finally:
        del app.dependency_overrides[get_analysis_service]

    assert response.status_code == 200
    data = response.json()
    assert data["total_journalists"] == 2
    assert data["succeeded"] == 2
    assert data["failed"] == 0

    scores = {r["journalist_name"]: r["analysis"]["score"] for r in data["results"]}
    assert scores["Emma Smith"] == 92
    assert scores["James Chen"] == 60
    assert all(r["status"] == "success" for r in data["results"])


def test_run_analysis_continues_after_one_journalist_fails(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    create_journalist(client, campaign_id, "Emma Smith")
    create_journalist(client, campaign_id, "James Chen")

    fake_ai_service = FakeAIService(
        errors={"James Chen": AIProviderError("AI provider timed out")},
        results={
            "Emma Smith": AnalysisResult(
                score=85,
                priority="high",
                reasons=["Strong match"],
                supporting_evidence=["Evidence"],
                concerns=[],
            ),
        },
    )
    app.dependency_overrides[get_analysis_service] = override_analysis_service(fake_ai_service)
    try:
        response = client.post(f"/api/campaigns/{campaign_id}/analysis")
    finally:
        del app.dependency_overrides[get_analysis_service]

    assert response.status_code == 200
    data = response.json()
    assert data["total_journalists"] == 2
    assert data["succeeded"] == 1
    assert data["failed"] == 1

    by_name = {r["journalist_name"]: r for r in data["results"]}
    assert by_name["Emma Smith"]["status"] == "success"
    assert by_name["Emma Smith"]["analysis"]["score"] == 85
    assert by_name["James Chen"]["status"] == "failed"
    assert by_name["James Chen"]["analysis"] is None
    assert "timed out" in by_name["James Chen"]["error"]

    # The successful analysis is still persisted despite the other failure.
    list_response = client.get(f"/api/campaigns/{campaign_id}/analysis")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_run_analysis_handles_invalid_ai_response(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    create_journalist(client, campaign_id, "Emma Smith")

    fake_ai_service = FakeAIService(
        errors={"Emma Smith": AIResponseError("AI response did not match the expected schema")}
    )
    app.dependency_overrides[get_analysis_service] = override_analysis_service(fake_ai_service)
    try:
        response = client.post(f"/api/campaigns/{campaign_id}/analysis")
    finally:
        del app.dependency_overrides[get_analysis_service]

    assert response.status_code == 200
    data = response.json()
    assert data["failed"] == 1
    assert data["results"][0]["status"] == "failed"


def test_run_analysis_for_missing_campaign_returns_404(client: TestClient) -> None:
    fake_ai_service = FakeAIService()
    app.dependency_overrides[get_analysis_service] = override_analysis_service(fake_ai_service)
    try:
        response = client.post("/api/campaigns/non-existent-campaign/analysis")
    finally:
        del app.dependency_overrides[get_analysis_service]

    assert response.status_code == 404


def test_run_analysis_with_no_journalists_returns_empty_results(client: TestClient) -> None:
    campaign_id = create_campaign(client)

    fake_ai_service = FakeAIService()
    app.dependency_overrides[get_analysis_service] = override_analysis_service(fake_ai_service)
    try:
        response = client.post(f"/api/campaigns/{campaign_id}/analysis")
    finally:
        del app.dependency_overrides[get_analysis_service]

    assert response.status_code == 200
    data = response.json()
    assert data["total_journalists"] == 0
    assert data["results"] == []


def test_list_analyses_ranked_by_score_descending(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    create_journalist(client, campaign_id, "Low Scorer")
    create_journalist(client, campaign_id, "High Scorer")

    fake_ai_service = FakeAIService(
        results={
            "Low Scorer": AnalysisResult(
                score=30, priority="low", reasons=["Weak match"], supporting_evidence=["Evidence"], concerns=[]
            ),
            "High Scorer": AnalysisResult(
                score=95, priority="high", reasons=["Great match"], supporting_evidence=["Evidence"], concerns=[]
            ),
        }
    )
    app.dependency_overrides[get_analysis_service] = override_analysis_service(fake_ai_service)
    try:
        client.post(f"/api/campaigns/{campaign_id}/analysis")
        response = client.get(f"/api/campaigns/{campaign_id}/analysis")
    finally:
        del app.dependency_overrides[get_analysis_service]

    assert response.status_code == 200
    data = response.json()
    assert [a["score"] for a in data] == [95, 30]


def test_get_analysis_for_journalist_success(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    journalist_id = create_journalist(client, campaign_id, "Emma Smith")

    fake_ai_service = FakeAIService()
    app.dependency_overrides[get_analysis_service] = override_analysis_service(fake_ai_service)
    try:
        client.post(f"/api/campaigns/{campaign_id}/analysis")
        response = client.get(f"/api/campaigns/{campaign_id}/analysis/{journalist_id}")
    finally:
        del app.dependency_overrides[get_analysis_service]

    assert response.status_code == 200
    assert response.json()["journalist_id"] == journalist_id


def test_get_analysis_for_journalist_not_yet_analyzed_returns_404(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    journalist_id = create_journalist(client, campaign_id, "Emma Smith")

    response = client.get(f"/api/campaigns/{campaign_id}/analysis/{journalist_id}")
    assert response.status_code == 404


def test_rerunning_analysis_updates_existing_record(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    journalist_id = create_journalist(client, campaign_id, "Emma Smith")

    first_ai_service = FakeAIService(
        results={
            "Emma Smith": AnalysisResult(
                score=40, priority="low", reasons=["Initial"], supporting_evidence=["Evidence"], concerns=[]
            )
        }
    )
    app.dependency_overrides[get_analysis_service] = override_analysis_service(first_ai_service)
    try:
        client.post(f"/api/campaigns/{campaign_id}/analysis")
    finally:
        del app.dependency_overrides[get_analysis_service]

    second_ai_service = FakeAIService(
        results={
            "Emma Smith": AnalysisResult(
                score=90, priority="high", reasons=["Improved"], supporting_evidence=["Evidence"], concerns=[]
            )
        }
    )
    app.dependency_overrides[get_analysis_service] = override_analysis_service(second_ai_service)
    try:
        client.post(f"/api/campaigns/{campaign_id}/analysis")
        list_response = client.get(f"/api/campaigns/{campaign_id}/analysis")
    finally:
        del app.dependency_overrides[get_analysis_service]

    data = list_response.json()
    assert len(data) == 1
    assert data[0]["score"] == 90
    assert data[0]["journalist_id"] == journalist_id


def test_analysis_service_and_repository_directly(db_session: Session) -> None:
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

    fake_ai_service = FakeAIService(
        results={
            "Emma Smith": AnalysisResult(
                score=88,
                priority="high",
                reasons=["Great fit"],
                supporting_evidence=["Evidence"],
                concerns=[],
            )
        }
    )
    service = AnalysisService(ai_service=fake_ai_service)

    run_result = service.run_campaign_analysis(db_session, campaign.id)
    assert run_result.succeeded == 1
    assert run_result.failed == 0

    stored = service.get_analysis_for_journalist(db_session, campaign.id, journalist.id)
    assert stored.score == 88
    assert stored.priority == "high"

    all_analyses = service.list_analyses(db_session, campaign.id)
    assert len(all_analyses) == 1
