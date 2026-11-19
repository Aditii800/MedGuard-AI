import sys
import types

# Prevent the real claim verifier from loading PyTorch during isolated tests.
if "services.claim_verifier" not in sys.modules:
    claim_verifier_stub = types.ModuleType("services.claim_verifier")
    claim_verifier_stub.verify_medical_claims = lambda text: {
        "verification_status": "COMPLETED",
        "claims": [],
    }
    sys.modules["services.claim_verifier"] = claim_verifier_stub

from services import safety_service


def install_fake_pipeline(monkeypatch):
    calls = []

    detection = {
        "flags": [{"code": "OVERCONFIDENCE"}],
        "has_safety_concern": True,
    }

    verification = {
        "verification_status": "COMPLETED",
        "claims": [],
    }

    risk = {
        "risk_score": 20,
        "risk_level": "LOW",
    }

    guard = {
        "delivery_action": "ALLOW",
        "response_blocked": False,
        "safe_response": "Test response",
    }

    def fake_detect(text):
        calls.append(("detect", text))
        return detection

    def fake_verify(text):
        calls.append(("verify", text))
        return verification

    def fake_classify(analysis, claim_verification=None):
        calls.append(("classify", analysis, claim_verification))
        return risk

    def fake_guard(text, analysis):
        calls.append(("guard", text, analysis))
        return guard

    monkeypatch.setattr(
        safety_service, "detect_hallucination_indicators", fake_detect
    )
    monkeypatch.setattr(
        safety_service, "verify_medical_claims", fake_verify
    )
    monkeypatch.setattr(
        safety_service, "classify_risk", fake_classify
    )
    monkeypatch.setattr(
        safety_service, "guard_response", fake_guard
    )

    return calls, detection, verification, risk, guard


def test_pipeline_executes_all_four_stages(monkeypatch):
    calls, detection, verification, risk, guard = install_fake_pipeline(
        monkeypatch
    )

    result = safety_service.analyze_ai_response("Test response")

    assert [call[0] for call in calls] == [
        "detect", "verify", "classify", "guard"
    ]
    assert result["risk_level"] == "LOW"
    assert result["delivery_action"] == "ALLOW"
    assert result["claim_verification"] == verification


def test_pipeline_trims_response_before_processing(monkeypatch):
    calls, *_ = install_fake_pipeline(monkeypatch)

    safety_service.analyze_ai_response("  Test response  ")

    assert calls[0] == ("detect", "Test response")
    assert calls[1] == ("verify", "Test response")


def test_none_input_is_converted_to_empty_string(monkeypatch):
    calls, *_ = install_fake_pipeline(monkeypatch)

    safety_service.analyze_ai_response(None)

    assert calls[0] == ("detect", "")
    assert calls[1] == ("verify", "")


def test_guard_receives_combined_detection_and_risk_data(monkeypatch):
    calls, detection, verification, risk, guard = install_fake_pipeline(
        monkeypatch
    )

    safety_service.analyze_ai_response("Test response")

    guard_call = calls[3]

    assert guard_call[0] == "guard"
    assert guard_call[1] == "Test response"
    assert guard_call[2]["flags"] == detection["flags"]
    assert guard_call[2]["risk_score"] == risk["risk_score"]
    assert guard_call[2]["risk_level"] == risk["risk_level"]
