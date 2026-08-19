import io

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.journalist_repository import JournalistRepository
from app.schemas.journalist import JournalistCreate
from app.services.journalist_service import JournalistService

CAMPAIGN_PAYLOAD = {
    "name": "AI Developer Security Launch",
    "company_name": "Acme Security",
    "product_description": "AI security analyzer for Python apps",
    "campaign_description": "Launching automated vulnerability scanner",
    "target_audience": "DevOps leads and Python engineers",
    "key_topics": "AI, Cybersecurity, Python, Developer Tools",
    "desired_outcome": "Earn press coverage in major tech journals",
}

VALID_CSV = (
    "name,email,publication,role,topics,bio,recent_articles\n"
    "Emma Smith,emma@example.com,Tech Weekly,Technology Writer,"
    '"AI;Developer Tools",Covers developer tools,AI coding tools\n'
    "James Chen,james@example.com,Security Today,Cybersecurity Reporter,"
    '"Cybersecurity;Cloud",Covers enterprise security,Zero trust adoption\n'
)


def create_campaign(client: TestClient) -> str:
    response = client.post("/api/campaigns", json=CAMPAIGN_PAYLOAD)
    assert response.status_code == 201
    return response.json()["id"]


def test_create_journalist_api_success(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    payload = {
        "name": "Emma Smith",
        "email": "emma@example.com",
        "publication": "Tech Weekly",
        "role": "Technology Writer",
        "topics": "AI;Developer Tools",
        "bio": "Covers developer tools and AI",
        "recent_articles": "AI coding tools;Python security",
    }
    response = client.post(f"/api/campaigns/{campaign_id}/journalists", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["campaign_id"] == campaign_id
    assert "id" in data


def test_create_journalist_for_missing_campaign_returns_404(client: TestClient) -> None:
    payload = {
        "name": "Emma Smith",
        "email": "emma@example.com",
        "publication": "Tech Weekly",
        "role": "Technology Writer",
    }
    response = client.post("/api/campaigns/non-existent-campaign/journalists", json=payload)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_list_journalists_for_campaign(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    for i in range(3):
        client.post(
            f"/api/campaigns/{campaign_id}/journalists",
            json={
                "name": f"Journalist {i}",
                "email": f"journalist{i}@example.com",
                "publication": "Tech Weekly",
                "role": "Writer",
            },
        )

    response = client.get(f"/api/campaigns/{campaign_id}/journalists")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_journalist_by_id_success(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    create_res = client.post(
        f"/api/campaigns/{campaign_id}/journalists",
        json={
            "name": "Emma Smith",
            "email": "emma@example.com",
            "publication": "Tech Weekly",
            "role": "Technology Writer",
        },
    )
    journalist_id = create_res.json()["id"]

    response = client.get(f"/api/campaigns/{campaign_id}/journalists/{journalist_id}")
    assert response.status_code == 200
    assert response.json()["id"] == journalist_id


def test_get_journalist_not_found(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    response = client.get(f"/api/campaigns/{campaign_id}/journalists/non-existent-id")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_import_valid_csv_persists_journalists(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    files = {"file": ("journalists.csv", io.BytesIO(VALID_CSV.encode("utf-8")), "text/csv")}
    response = client.post(f"/api/campaigns/{campaign_id}/journalists/import", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 2
    assert data["total_rows"] == 2
    assert data["errors"] == []

    list_response = client.get(f"/api/campaigns/{campaign_id}/journalists")
    assert len(list_response.json()) == 2


def test_import_csv_missing_required_columns_rejected(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    csv_content = "name,email\nEmma Smith,emma@example.com\n"
    files = {"file": ("journalists.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post(f"/api/campaigns/{campaign_id}/journalists/import", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "BAD_REQUEST"
    assert "missing_columns" in data["error"]["details"]


def test_import_csv_reports_invalid_rows_and_keeps_valid_ones(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    csv_content = (
        "name,email,publication,role,topics,bio,recent_articles\n"
        "Emma Smith,emma@example.com,Tech Weekly,Technology Writer,AI,Bio,Articles\n"
        ",bad-email,,Reporter,AI,Bio,Articles\n"
    )
    files = {"file": ("journalists.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post(f"/api/campaigns/{campaign_id}/journalists/import", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 1
    assert data["total_rows"] == 2
    assert len(data["errors"]) == 1
    assert data["errors"][0]["row"] == 3

    list_response = client.get(f"/api/campaigns/{campaign_id}/journalists")
    assert len(list_response.json()) == 1


def test_import_csv_rejects_non_csv_file(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    files = {"file": ("journalists.txt", io.BytesIO(b"not a csv"), "text/plain")}
    response = client.post(f"/api/campaigns/{campaign_id}/journalists/import", files=files)
    assert response.status_code == 400


def test_import_csv_for_missing_campaign_returns_404(client: TestClient) -> None:
    files = {"file": ("journalists.csv", io.BytesIO(VALID_CSV.encode("utf-8")), "text/csv")}
    response = client.post("/api/campaigns/non-existent-campaign/journalists/import", files=files)
    assert response.status_code == 404


def test_journalist_service_and_repository(db_session: Session) -> None:
    from app.repositories.campaign_repository import CampaignRepository
    from app.models.campaign import Campaign

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

    repo = JournalistRepository()
    service = JournalistService(repository=repo)

    created = service.create_journalist(
        db_session,
        campaign.id,
        JournalistCreate(
            name="Emma Smith",
            email="emma@example.com",
            publication="Tech Weekly",
            role="Technology Writer",
            topics="AI",
            bio="Bio",
            recent_articles="Articles",
        ),
    )
    assert created.id is not None
    assert created.campaign_id == campaign.id

    fetched = service.get_journalist(db_session, campaign.id, created.id)
    assert fetched.id == created.id

    all_journalists = service.list_journalists(db_session, campaign.id)
    assert len(all_journalists) == 1


def test_import_csv_with_empty_file_rejected(client: TestClient) -> None:
    campaign_id = create_campaign(client)
    files = {"file": ("journalists.csv", io.BytesIO(b""), "text/csv")}
    response = client.post(f"/api/campaigns/{campaign_id}/journalists/import", files=files)
    assert response.status_code == 400
