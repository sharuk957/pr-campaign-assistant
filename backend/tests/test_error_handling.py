from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import AppException, BadRequestError, NotFoundError
from app.main import app


# Dedicated router to trigger various error scenarios
error_testing_router = APIRouter(prefix="/test-errors")


class SamplePayload(BaseModel):
    required_field: str
    numeric_field: int


@error_testing_router.get("/app-exception")
def raise_app_exception() -> None:
    raise AppException(code="CUSTOM_ERROR", message="Custom error occurred", status_code=400)


@error_testing_router.get("/not-found")
def raise_not_found() -> None:
    raise NotFoundError(message="Item could not be found")


@error_testing_router.get("/bad-request")
def raise_bad_request() -> None:
    raise BadRequestError(message="Invalid parameters provided")


@error_testing_router.post("/validation")
def validate_payload(payload: SamplePayload) -> dict[str, str]:
    return {"status": "ok"}


@error_testing_router.get("/unhandled-server-error")
def raise_unhandled() -> None:
    raise RuntimeError("Unexpected server crash")


app.include_router(error_testing_router)


def test_404_not_found(client: TestClient) -> None:
    response = client.get("/nonexistent-endpoint-12345")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "message" in data["error"]


def test_custom_app_exception(client: TestClient) -> None:
    response = client.get("/test-errors/app-exception")
    assert response.status_code == 400
    data = response.json()
    assert data == {
        "error": {
            "code": "CUSTOM_ERROR",
            "message": "Custom error occurred",
        }
    }


def test_not_found_error_subclass(client: TestClient) -> None:
    response = client.get("/test-errors/not-found")
    assert response.status_code == 404
    data = response.json()
    assert data == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Item could not be found",
        }
    }


def test_bad_request_error_subclass(client: TestClient) -> None:
    response = client.get("/test-errors/bad-request")
    assert response.status_code == 400
    data = response.json()
    assert data == {
        "error": {
            "code": "BAD_REQUEST",
            "message": "Invalid parameters provided",
        }
    }


def test_validation_error_format(client: TestClient) -> None:
    response = client.post("/test-errors/validation", json={"required_field": "test", "numeric_field": "not-a-number"})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Invalid request payload or parameters"
    assert "details" in data["error"]


def test_unhandled_server_error_format(client: TestClient) -> None:
    response = client.get("/test-errors/unhandled-server-error")
    assert response.status_code == 500
    data = response.json()
    assert data == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
        }
    }
