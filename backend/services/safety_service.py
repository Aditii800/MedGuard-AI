
# ============================================================
# MEDICAL AI SAFETY MIDDLEWARE
# Integrated Safety Analysis Pipeline
# ============================================================

from detection.hallucination_detector import (
    detect_hallucination_indicators,
)

from detection.risk_classifier import (
    classify_risk,
)

from services.claim_verifier import (
    verify_medical_claims,
)

from services.response_guard import (
    guard_response,
)


def analyze_ai_response(ai_response):
    """
    Run the complete Medical AI Safety Middleware.

    Pipeline:
    1. Detect rule-based safety indicators.
    2. Verify extracted claims using local semantic evidence.
    3. Calculate the hybrid risk score.
    4. Decide whether to allow, review, or block the response.

    Semantic similarity is not proof of medical truth.
    This system is an academic prototype, not a clinically
    validated medical safety product.
    """

    text = str(ai_response or "").strip()

    # Part 1: Rule-based detection
    detection_result = detect_hallucination_indicators(text)

    # Part 2: Semantic claim verification
    claim_verification = verify_medical_claims(text)

    # Part 3: Hybrid risk classification
    risk_result = classify_risk(
        detection_result,
        claim_verification=claim_verification,
    )

    # Preserve detection and risk fields for existing consumers.
    combined_analysis = {
        **detection_result,
        **risk_result,
    }

    # Part 4: Guard the original response
    guard_result = guard_response(
        text,
        combined_analysis,
    )

    # Return both the overall safety decision and detailed
    # claim-level evidence for the application's results page.
    return {
        **combined_analysis,
        **guard_result,
        "claim_verification": claim_verification,
    }
