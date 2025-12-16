"""Simple API tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["engine"] == "contract-execution"


def test_metrics(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "contracts_loaded" in data
    assert "load_time_ms" in data
    assert "domains" in data
    assert "versions" in data


def test_predict_telemetry_v2_normal(client):
    response = client.post(
        "/predict/telemetry/v2", json={"temp_c": 25.0, "humidity": 60.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["domain"] == "telemetry"
    assert data["version"] == "v2"
    assert "predictions" in data
    assert "metadata" in data
    assert data["data"]["temp_c"] == 25.0
    assert data["data"]["humidity"] == 60.0


def test_predict_invalid_domain(client):
    response = client.post("/predict/invalid/v1", json={"field": "value"})
    assert response.status_code == 404


def test_predict_invalid_version(client):
    response = client.post("/predict/telemetry/v999", json={"temp_c": 25.0})
    assert response.status_code == 404
