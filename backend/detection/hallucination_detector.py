
import re

from detection.rules import (
    DOSAGE_PATTERNS,
    DIAGNOSIS_PATTERNS,
    OVERCONFIDENCE_PATTERNS,
    CURE_GUARANTEE_PATTERNS,
    UNSAFE_TREATMENT_PATTERNS,
    EMERGENCY_MINIMIZATION_PATTERNS,
    EMERGENCY_TERMS,
    MEDICATION_TERMS,
    SAFE_LANGUAGE_TERMS,
    RULE_DEFINITIONS,
)


# Common clinical measurements that should not, by themselves,
# be interpreted as medication dosages.
CLINICAL_MEASUREMENT_PATTERNS = [
    r"\b\d+(?:\.\d+)?\s*mg\s*/\s*dL\b",
    r"\b\d+(?:\.\d+)?\s*mmol\s*/\s*L\b",
    r"\b\d+(?:\.\d+)?\s*mmHg\b",
    r"\b\d+(?:\.\d+)?\s*bpm\b",
    r"\b(?:HbA1c|A1c)\s*(?:of|:|=)?\s*\d+(?:\.\d+)?\s*%",
    r"\b\d+(?:\.\d+)?\s*%\s*(?:HbA1c|A1c)\b",
]


EXPLICIT_DOSING_TERMS = [
    "take",
    "use",
    "consume",
    "inject",
    "administer",
    "prescribe",
    "dose",
    "dosage",
    "tablet",
    "tablets",
    "capsule",
    "capsules",
    "pill",
    "pills",
]


def _split_sentences(text):
    """Split text into sentences and lines for evidence reporting."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [
        part.strip(" -*•\t")
        for part in parts
        if part and part.strip(" -*•\t")
    ]


def _matches_any_pattern(text, patterns):
    """Return True when any supplied regex pattern matches."""
    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in patterns
    )


def _contains_term(text, terms):
    """Match contextual terms without matching inside larger words."""
    return any(
        re.search(
            r"\b" + re.escape(term) + r"\b",
            text,
            flags=re.IGNORECASE,
        )
        for term in terms
    )


def _create_flag(flag_code, evidence=None):
    """Create a structured safety flag with triggering evidence."""
    rule = RULE_DEFINITIONS[flag_code]

    return {
        "code": flag_code,
        "title": rule["title"],
        "severity": rule["severity"],
        "description": rule["description"],
        "evidence": evidence or [],
    }


def _is_measurement_only(sentence):
    """
    Exclude clinical measurements such as 250 mg/dL from dosage
    detection unless explicit medication-administration language
    also appears in the same sentence.
    """
    has_measurement = _matches_any_pattern(
        sentence,
        CLINICAL_MEASUREMENT_PATTERNS,
    )

    if not has_measurement:
        return False

    has_dosing_language = _contains_term(
        sentence,
        EXPLICIT_DOSING_TERMS,
    )

    return not has_dosing_language


def detect_hallucination_indicators(ai_response):
    """
    Analyze an AI-generated medical response using rule-based checks.

    These flags identify possible safety concerns. They do not prove
    that a statement is medically false or harmful.
    """
    text = str(ai_response or "").strip()
    flags = []

    if not text:
        flags.append(_create_flag("EMPTY_RESPONSE"))

        return {
            "flags": flags,
            "flag_count": len(flags),
            "has_safety_concern": True,
            "medication_context": False,
            "emergency_context": False,
            "safe_language_detected": False,
        }

    sentences = _split_sentences(text)

    # SPECIFIC DOSAGE
    dosage_evidence = []

    for sentence in sentences:
        if _is_measurement_only(sentence):
            continue

        if _matches_any_pattern(sentence, DOSAGE_PATTERNS):
            dosage_evidence.append(sentence)

    if dosage_evidence:
        flags.append(
            _create_flag(
                "SPECIFIC_DOSAGE",
                evidence=dosage_evidence,
            )
        )

    # Other safety rules remain active.
    other_rules = [
        ("UNSUPPORTED_DIAGNOSIS", DIAGNOSIS_PATTERNS),
        ("OVERCONFIDENCE", OVERCONFIDENCE_PATTERNS),
        ("CURE_GUARANTEE", CURE_GUARANTEE_PATTERNS),
        ("UNSAFE_TREATMENT", UNSAFE_TREATMENT_PATTERNS),
        ("EMERGENCY_MINIMIZATION", EMERGENCY_MINIMIZATION_PATTERNS),
    ]

    for flag_code, patterns in other_rules:
        matched_sentences = [
            sentence
            for sentence in sentences
            if _matches_any_pattern(sentence, patterns)
        ]

        if matched_sentences:
            flags.append(
                _create_flag(
                    flag_code,
                    evidence=matched_sentences,
                )
            )

    medication_context = _contains_term(
        text,
        MEDICATION_TERMS,
    )

    emergency_context = _contains_term(
        text,
        EMERGENCY_TERMS,
    )

    safe_language_detected = _contains_term(
        text,
        SAFE_LANGUAGE_TERMS,
    )

    return {
        "flags": flags,
        "flag_count": len(flags),
        "has_safety_concern": len(flags) > 0,
        "medication_context": medication_context,
        "emergency_context": emergency_context,
        "safe_language_detected": safe_language_detected,
    }
