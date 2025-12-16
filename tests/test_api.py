import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predict_telemetry_v2_normal():
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


def test_predict_telemetry_v2_out_of_range():
    response = client.post(
        "/predict/telemetry/v2", json={"temp_c": -50.0, "humidity": 110.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["temp_c"] == -40.0  # Clamped to min
    assert data["data"]["humidity"] == 100.0  # Clamped to max


def test_predict_telemetry_v2_missing_field():
    response = client.post("/predict/telemetry/v2", json={"temp_c": 25.0})
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["humidity"] == 50.0  # Default value


def test_predict_invalid_domain():
    response = client.post("/predict/invalid/v1", json={"field": "value"})
    assert response.status_code == 400


def test_predict_invalid_version():
    response = client.post("/predict/telemetry/v999", json={"temp_c": 25.0})
    assert response.status_code == 400
