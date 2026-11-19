import tempfile
from pathlib import Path

import pytest
import database

# Use a temporary SQLite database so tests never modify project data.
_test_directory = tempfile.TemporaryDirectory(prefix="medical_ai_tests_")
database.DATABASE_PATH = (
    Path(_test_directory.name) / "test_medical_ai_safety.db"
)

import sys
import types

# Replace the heavyweight claim-verifier module for API tests.
claim_verifier_stub = types.ModuleType("services.claim_verifier")

def fake_verify_medical_claims(text):
    return {
        "verification_status": "COMPLETED",
        "claims": [],
    }

claim_verifier_stub.verify_medical_claims = fake_verify_medical_claims

sys.modules["services.claim_verifier"] = claim_verifier_stub

# Import the Flask application after redirecting its database.
import app as app_module


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)

    with app_module.app.test_client() as test_client:
        yield test_client


def test_home_endpoint_returns_success(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_test_safety_rejects_empty_response(client):
    response = client.post(
        "/api/test-safety",
        json={"response": ""},
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_test_safety_returns_analysis(client, monkeypatch):
    fake_verification = {
        "verification_status": "COMPLETED",
        "claims": [],
    }

    fake_analysis = {
        "risk_score": 10,
        "risk_level": "LOW",
        "delivery_action": "ALLOW",
    }

    monkeypatch.setattr(
        app_module,
        "verify_medical_claims",
        lambda text: fake_verification,
    )

    monkeypatch.setattr(
        app_module,
        "analyze_ai_response",
        lambda text: {"flags": []},
    )

    monkeypatch.setattr(
        app_module,
        "apply_hybrid_risk",
        lambda *args: fake_analysis,
    )

    response = client.post(
        "/api/test-safety",
        json={
            "question": "What is a fever?",
            "response": "A fever is an elevated body temperature.",
        },
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["analysis"]["risk_level"] == "LOW"


def test_test_safety_handles_analysis_failure(client, monkeypatch):
    def raise_error(text):
        raise RuntimeError("Simulated verification failure")

    monkeypatch.setattr(
        app_module,
        "verify_medical_claims",
        raise_error,
    )

    response = client.post(
        "/api/test-safety",
        json={"response": "Example medical response."},
    )

    assert response.status_code == 500
    assert response.get_json()["success"] is False


def test_history_endpoint_returns_success(client):
    response = client.get("/api/history")

    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["count"] == 0


def test_dashboard_endpoint_returns_success(client):
    response = client.get("/api/dashboard")

    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["dashboard"]["total_analyses"] == 0
