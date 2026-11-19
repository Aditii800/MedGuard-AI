from services.response_guard import guard_response, build_explanations


def test_low_risk_allows_original_response():
    original = "A fever is an elevated body temperature."

    result = guard_response(
        original,
        {"risk_level": "LOW", "flags": []},
    )

    assert result["delivery_action"] == "ALLOW"
    assert result["response_blocked"] is False
    assert result["safe_response"] == original


def test_medium_risk_withholds_original_response():
    original = "Take this medicine without consulting anyone."

    result = guard_response(
        original,
        {
            "risk_level": "MEDIUM",
            "flags": [{"code": "UNSAFE_TREATMENT"}],
        },
    )

    assert result["delivery_action"] == "REVIEW"
    assert result["response_blocked"] is True
    assert result["safe_response"] != original
    assert "qualified healthcare professional" in result["safe_response"]


def test_high_risk_blocks_original_response():
    original = "Ignore severe chest pain."

    result = guard_response(
        original,
        {
            "risk_level": "HIGH",
            "flags": [{"code": "EMERGENCY_MINIMIZATION"}],
        },
    )

    assert result["delivery_action"] == "BLOCK"
    assert result["response_blocked"] is True
    assert result["safe_response"] != original
    assert "urgent medical care" in result["safe_response"]


def test_known_safety_flag_has_readable_explanation():
    result = build_explanations(
        [{"code": "SPECIFIC_DOSAGE"}]
    )

    assert len(result) == 1
    assert result[0]["code"] == "SPECIFIC_DOSAGE"
    assert "dosage" in result[0]["message"]


def test_unknown_flag_is_ignored():
    result = build_explanations(
        [{"code": "UNKNOWN_FLAG"}]
    )

    assert result == []


def test_missing_risk_level_defaults_to_low():
    original = "Please stay hydrated."

    result = guard_response(original, {})

    assert result["delivery_action"] == "ALLOW"
    assert result["response_blocked"] is False
    assert result["safe_response"] == original
