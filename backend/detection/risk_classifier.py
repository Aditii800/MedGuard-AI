
# ============================================================
# MEDICAL AI SAFETY MIDDLEWARE
# Hybrid Risk Scoring and Classification Engine
# ============================================================

FLAG_WEIGHTS = {
    "EMPTY_RESPONSE": 20,
    "SPECIFIC_DOSAGE": 35,
    "UNSUPPORTED_DIAGNOSIS": 35,
    "OVERCONFIDENCE": 20,
    "UNSAFE_TREATMENT": 40,
    "CURE_GUARANTEE": 30,
    "EMERGENCY_MINIMIZATION": 50,
}

SEVERITY_BONUS = {
    "warning": 0,
    "medium": 5,
    "high": 10,
    "critical": 15,
}

CLAIM_WEIGHTS = {
    "SUPPORTED": 0,
    "UNCERTAIN": 5,
    "UNSUPPORTED": 30,
}

SEMANTIC_CAP = 40
VERIFICATION_UNAVAILABLE_MINIMUM = 30


def classify_risk(safety_analysis, claim_verification=None):
    """
    Combine rule-based indicators with semantic evidence retrieval.

    This is a heuristic academic score, not a clinical probability.
    Semantic similarity does not establish that a claim is true or false.
    """

    flags = safety_analysis.get("flags", [])
    score_breakdown = []

    rule_based_score = 0
    semantic_risk_score = 0
    ordinary_unsupported_count = 0

    # 1. Rule-based safety indicators
    for flag in flags:
        flag_code = flag.get("code", "")
        severity = flag.get("severity", "warning")

        base_weight = FLAG_WEIGHTS.get(flag_code, 0)
        severity_bonus = SEVERITY_BONUS.get(severity, 0)
        contribution = base_weight + severity_bonus

        rule_based_score += contribution

        score_breakdown.append({
            "type": "RULE_BASED",
            "flag": flag_code,
            "base_weight": base_weight,
            "severity": severity,
            "severity_bonus": severity_bonus,
            "contribution": contribution,
        })

    # 2. Medication context
    if safety_analysis.get("medication_context", False) and flags:
        rule_based_score += 5

        score_breakdown.append({
            "type": "RULE_BASED",
            "flag": "MEDICATION_CONTEXT",
            "base_weight": 5,
            "severity": "context",
            "severity_bonus": 0,
            "contribution": 5,
        })

    # 3. Protective language reduction
    # Cautious language must not erase the presence of safety flags.
    if safety_analysis.get("safe_language_detected", False):
        if rule_based_score > 0:
            reduction = min(10, rule_based_score)
            rule_based_score -= reduction

            score_breakdown.append({
                "type": "PROTECTIVE",
                "flag": "SAFE_LANGUAGE",
                "base_weight": 0,
                "severity": "protective",
                "severity_bonus": 0,
                "contribution": -reduction,
            })

    # 4. Semantic verification
    verification_status = "NOT_RUN"

    if claim_verification is not None:
        verification_status = claim_verification.get(
            "verification_status",
            "UNAVAILABLE",
        )

        if verification_status == "COMPLETED":
            for claim in claim_verification.get("claims", []):
                # Synthetic test claims must never affect normal scoring.
                if claim.get("is_synthetic_test_claim", False):
                    score_breakdown.append({
                        "type": "SEMANTIC_VERIFICATION",
                        "flag": "SYNTHETIC_CLAIM_EXCLUDED",
                        "claim": claim.get("claim", ""),
                        "contribution": 0,
                    })
                    continue

                status = claim.get("status", "UNCERTAIN")
                confidence = claim.get("confidence", 0)

                # Only known statuses contribute to the score.
                contribution = CLAIM_WEIGHTS.get(status, 5)

                # This is a low-evidence label, not proof of falsity.
                if status == "UNSUPPORTED":
                    ordinary_unsupported_count += 1

                semantic_risk_score += contribution

                score_breakdown.append({
                    "type": "SEMANTIC_VERIFICATION",
                    "flag": f"CLAIM_{status}",
                    "claim": claim.get("claim", ""),
                    "status": status,
                    "confidence": confidence,
                    "contribution": contribution,
                })

            semantic_risk_score = min(
                semantic_risk_score,
                SEMANTIC_CAP,
            )

        else:
            # Fail closed to REVIEW if semantic verification is
            # unavailable. This does not mean the claim is false.
            score_breakdown.append({
                "type": "VERIFICATION_STATUS",
                "flag": "SEMANTIC_VERIFICATION_UNAVAILABLE",
                "contribution": 0,
            })

    # 5. Combine the scores
    risk_score = rule_based_score + semantic_risk_score

    verification_unavailable = (
        claim_verification is not None
        and verification_status != "COMPLETED"
    )

    if verification_unavailable:
        risk_score = max(
            risk_score,
            VERIFICATION_UNAVAILABLE_MINIMUM,
        )

    risk_score = max(0, min(risk_score, 100))

    # 6. Classify risk
    if risk_score >= 60:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # 7. Explain the result
    if verification_unavailable:
        risk_message = (
            "Semantic claim verification was unavailable. "
            "The response requires review; safety was not "
            "established by the semantic verification layer."
        )
    elif risk_level == "HIGH":
        risk_message = (
            "High-risk medical safety indicators were detected. "
            "The response should not be used without additional "
            "safety review."
        )
    elif risk_level == "MEDIUM":
        risk_message = (
            "Medical safety indicators or claims with limited "
            "local semantic support were detected. Review the "
            "response before relying on it."
        )
    else:
        risk_message = (
            "No major risk indicators were detected by the current "
            "heuristic checks. This does not guarantee medical safety."
        )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_message": risk_message,
        "rule_based_score": rule_based_score,
        "semantic_risk_score": semantic_risk_score,
        "score_breakdown": score_breakdown,
        "scoring_method": "HYBRID_RULE_AND_SEMANTIC",
        "verification_status": verification_status,
        "verification_unavailable": verification_unavailable,
        "low_semantic_support_claim_count": ordinary_unsupported_count,
        "score_interpretation": "HEURISTIC_NOT_CONFIRMED_HALLUCINATION_RATE",
        "clinical_validation": "NOT_CLINICALLY_VALIDATED",
    }
