from services.emergency_guard import (
    detect_emergency_question,
    emergency_safe_response,
)


def test_detects_possible_overdose():
    result = detect_emergency_question(
        "I accidentally took an extra dose of my medicine."
    )

    assert result == "POSSIBLE_OVERDOSE"


def test_detects_multiple_tablets_concern():
    result = detect_emergency_question(
        "I may have swallowed 10 tablets."
    )

    assert result == "POSSIBLE_OVERDOSE"


def test_detects_severe_chest_pain():
    result = detect_emergency_question(
        "I'm having severe chest pain."
    )

    assert result == "POSSIBLE_EMERGENCY"


def test_detects_breathing_difficulty():
    result = detect_emergency_question(
        "I can't breathe."
    )

    assert result == "POSSIBLE_EMERGENCY"


def test_ordinary_health_question_is_not_flagged():
    result = detect_emergency_question(
        "What are common causes of a mild headache?"
    )

    assert result is None


def test_empty_question_returns_none():
    assert detect_emergency_question("") is None
    assert detect_emergency_question(None) is None


def test_overdose_response_contains_urgent_guidance():
    result = emergency_safe_response("POSSIBLE_OVERDOSE")

    assert "urgent professional help" in result
    assert "112" in result
    assert "Do not wait for symptoms" in result


def test_general_emergency_response_contains_urgent_guidance():
    result = emergency_safe_response("POSSIBLE_EMERGENCY")

    assert "urgent professional help" in result
    assert "112" in result
    assert "Do not rely on an AI response" in result
