from detection.risk_classifier import classify_risk


def test_no_flags_produces_low_risk():
    result = classify_risk({"flags": []})

    assert result["risk_score"] == 0
    assert result["risk_level"] == "LOW"


def test_critical_emergency_flag_produces_high_risk():
    analysis = {
        "flags": [
            {
                "code": "EMERGENCY_MINIMIZATION",
                "severity": "critical",
            }
        ]
    }

    result = classify_risk(analysis)

    assert result["risk_score"] == 65
    assert result["risk_level"] == "HIGH"


def test_unsupported_claim_produces_medium_risk():
    analysis = {"flags": []}
    verification = {
        "verification_status": "COMPLETED",
        "claims": [
            {
                "claim": "Example medical claim",
                "status": "UNSUPPORTED",
                "confidence": 0.9,
            }
        ],
    }

    result = classify_risk(analysis, verification)

    assert result["risk_score"] == 30
    assert result["risk_level"] == "MEDIUM"
    assert result["low_semantic_support_claim_count"] == 1


def test_unavailable_verification_requires_review():
    result = classify_risk(
        {"flags": []},
        {"verification_status": "UNAVAILABLE"},
    )

    assert result["risk_score"] == 30
    assert result["risk_level"] == "MEDIUM"
    assert result["verification_unavailable"] is True


def test_synthetic_test_claim_does_not_increase_score():
    analysis = {"flags": []}
    verification = {
        "verification_status": "COMPLETED",
        "claims": [
            {
                "claim": "Synthetic test claim",
                "status": "UNSUPPORTED",
                "confidence": 0.9,
                "is_synthetic_test_claim": True,
            }
        ],
    }

    result = classify_risk(analysis, verification)

    assert result["risk_score"] == 0
    assert result["risk_level"] == "LOW"
    assert result["low_semantic_support_claim_count"] == 0
    assert any(
        item["flag"] == "SYNTHETIC_CLAIM_EXCLUDED"
        for item in result["score_breakdown"]
    )


def test_safe_language_reduces_but_does_not_erase_risk():
    analysis = {
        "flags": [
            {
                "code": "OVERCONFIDENCE",
                "severity": "warning",
            }
        ],
        "safe_language_detected": True,
    }

    result = classify_risk(analysis)

    assert result["rule_based_score"] == 10
    assert result["risk_score"] == 10
    assert result["risk_level"] == "LOW"
