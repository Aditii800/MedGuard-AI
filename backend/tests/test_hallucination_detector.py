from detection.hallucination_detector import detect_hallucination_indicators


def get_flag_codes(result):
    return {flag["code"] for flag in result["flags"]}


def test_empty_response_is_flagged():
    result = detect_hallucination_indicators("")

    assert "EMPTY_RESPONSE" in get_flag_codes(result)
    assert result["has_safety_concern"] is True


def test_specific_medication_dosage_is_detected():
    result = detect_hallucination_indicators(
        "Take 500 mg of the medication every day."
    )

    assert "SPECIFIC_DOSAGE" in get_flag_codes(result)


def test_blood_glucose_measurement_is_not_mistaken_for_dosage():
    result = detect_hallucination_indicators(
        "Your blood glucose reading is 250 mg/dL."
    )

    assert "SPECIFIC_DOSAGE" not in get_flag_codes(result)


def test_direct_diagnosis_is_flagged():
    result = detect_hallucination_indicators(
        "You have diabetes."
    )

    assert "UNSUPPORTED_DIAGNOSIS" in get_flag_codes(result)


def test_conditional_health_statement_is_not_flagged_as_diagnosis():
    result = detect_hallucination_indicators(
        "If you have a fever, consider consulting a doctor."
    )

    assert "UNSUPPORTED_DIAGNOSIS" not in get_flag_codes(result)


def test_overconfident_language_is_detected():
    result = detect_hallucination_indicators(
        "This treatment will definitely work."
    )

    assert "OVERCONFIDENCE" in get_flag_codes(result)


def test_unsafe_treatment_advice_is_detected():
    result = detect_hallucination_indicators(
        "Stop taking your medication."
    )

    assert "UNSAFE_TREATMENT" in get_flag_codes(result)


def test_emergency_minimization_is_detected():
    result = detect_hallucination_indicators(
        "Chest pain is nothing to worry about."
    )

    assert "EMERGENCY_MINIMIZATION" in get_flag_codes(result)


def test_emergency_and_medication_context_are_reported():
    result = detect_hallucination_indicators(
        "If you have chest pain, seek emergency medical care."
    )

    assert result["emergency_context"] is True
    assert result["medication_context"] is False
