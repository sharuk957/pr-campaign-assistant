from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.repositories.campaign_repository import CampaignRepository
from app.schemas.campaign import CampaignCreate
from app.services.campaign_service import CampaignService


def test_create_campaign_api_success(client: TestClient) -> None:
    payload = {
        "name": "AI Developer Security Launch",
        "company_name": "Acme Security",
        "product_description": "AI security analyzer for Python apps",
        "campaign_description": "Launching automated vulnerability scanner",
        "target_audience": "DevOps leads and Python engineers",
        "key_topics": "AI, Cybersecurity, Python, Developer Tools",
        "desired_outcome": "Earn press coverage in major tech journals",
    }
    response = client.post("/api/campaigns", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["company_name"] == payload["company_name"]
    assert "id" in data
    assert "created_at" in data


def test_create_campaign_validation_failure(client: TestClient) -> None:
    # Missing required fields
    payload = {
        "name": "Incomplete Campaign",
    }
    response = client.post("/api/campaigns", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_get_campaign_by_id_success(client: TestClient) -> None:
    payload = {
        "name": "Product Launch",
        "company_name": "Tech Corp",
        "product_description": "Cloud monitoring suite",
        "campaign_description": "Announcing general availability",
        "target_audience": "CTOs and DevOps Engineers",
        "key_topics": "Cloud, DevOps, Observability",
        "desired_outcome": "Brand awareness",
    }
    create_res = client.post("/api/campaigns", json=payload)
    assert create_res.status_code == 201
    campaign_id = create_res.json()["id"]

    get_res = client.get(f"/api/campaigns/{campaign_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == campaign_id
    assert data["name"] == "Product Launch"


def test_get_campaign_not_found(client: TestClient) -> None:
    response = client.get("/api/campaigns/non-existent-id-999")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "non-existent-id-999" in data["error"]["message"]


def test_list_campaigns(client: TestClient) -> None:
    for i in range(3):
        payload = {
            "name": f"Campaign {i}",
            "company_name": f"Company {i}",
            "product_description": "Description",
            "campaign_description": "Angle",
            "target_audience": "Audience",
            "key_topics": "Topics",
            "desired_outcome": "Outcome",
        }
        client.post("/api/campaigns", json=payload)

    response = client.get("/api/campaigns")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_campaign_service_and_repository(db_session: Session) -> None:
    repo = CampaignRepository()
    service = CampaignService(repository=repo)

    create_data = CampaignCreate(
        name="Direct Service Campaign",
        company_name="Acme",
        product_description="Product",
        campaign_description="Story",
        target_audience="Target",
        key_topics="AI;Dev",
        desired_outcome="Coverage",
    )

    created = service.create_campaign(db_session, create_data)
    assert created.id is not None
    assert created.name == "Direct Service Campaign"

    fetched = service.get_campaign(db_session, created.id)
    assert fetched.id == created.id

    all_campaigns = service.list_campaigns(db_session)
    assert len(all_campaigns) == 1
