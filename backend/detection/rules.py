import re


# ============================================================
# MEDICAL AI SAFETY MIDDLEWARE
# Rule-Based Safety / Hallucination Indicator Rules
#
# CHANGED in this version (marked with "CHANGED"):
#   1. DIAGNOSIS: bare "you have" removed (it flagged safe text
#      like "If you have a fever, drink fluids").
#   2. OVERCONFIDENCE: "definitely" / "certainly" / "guaranteed"
#      no longer match when negated ("does not definitely mean").
#   3. OVERCONFIDENCE: "100%" pattern fixed (the old trailing
#      \b meant it could never match "100% sure").
# ============================================================


DOSAGE_PATTERNS = [
    r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|µg|g|ml|mL)\b",
    r"\b\d+\s*(?:tablet|tablets|capsule|capsules|pills?)\b",
    r"\b(?:take|use|consume)\s+\d+\b",
    r"\b\d+\s+times?\s+(?:a|per)\s+day\b",
    r"\bevery\s+\d+\s+hours?\b",
]


# CHANGED: no bare "you have". A diagnosis claim now needs a
# named condition, and is ignored after "if" / "when".
DIAGNOSIS_PATTERNS = [
    r"(?<!if )(?<!when )\byou (?:definitely |certainly |clearly )?have (?:a |an )?(?:serious |severe |bacterial |viral |chronic )?(?:infection|disease|disorder|diabetes|cancer|pneumonia|hypertension|asthma|covid|malaria|dengue|tuberculosis|arthritis)\b",
    r"\byou definitely have\b",
    r"\byou are suffering from\b",
    r"\byou suffer from\b",
    r"\byou are diagnosed with\b",
    r"\bthis confirms\b",
    r"\bthis proves (?:that )?you have\b",
    r"\byour symptoms confirm\b",
    r"\byour symptoms prove\b",
    r"\bclearly indicates? that you have\b",
]


# CHANGED: negation-safe, and the 100% pattern actually matches now.
OVERCONFIDENCE_PATTERNS = [
    r"(?<!not )(?<!n't )\bdefinitely\b",
    r"(?<!not )(?<!n't )\bcertainly\b",
    r"\bwithout a doubt\b",
    r"\bthere is no doubt\b",
    r"(?<!not )(?<!no treatment is )\bguaranteed\b",
    r"\b100\s*%",
    r"\bcompletely certain\b",
    r"\bi am certain\b",
    r"\bi am sure\b",
]


CURE_GUARANTEE_PATTERNS = [
    r"\bguaranteed cure\b",
    r"\bguaranteed to cure\b",
    r"\bwill definitely cure\b",
    r"\bwill cure\b",
    r"\bcompletely cures?\b",
    r"\bpermanent cure\b",
    r"\bpermanently cures?\b",
    r"\bcures? .* completely\b",
    r"\b100\s*%\s*(?:effective|cure|successful)\b",
]


UNSAFE_TREATMENT_PATTERNS = [
    r"\bstop taking your medication\b",
    r"\bstop taking your medicine\b",
    r"\bstop your medication\b",
    r"\bstop your medicine\b",
    r"\bdiscontinue your medication\b",
    r"\bdiscontinue your medicine\b",
    r"\bdouble\s+(?:your|their|the|an?)\s+(?:insulin\s+)?dose\b",
    r"\bincrease your dose\b",
    r"\bignore your doctor\b",
    r"\bdo not consult (?:a|your) doctor\b",
    r"\bno need to consult (?:a|your) doctor\b",
    r"\bavoid seeing (?:a|your) doctor\b",
    r"\breplace your prescribed medication\b",
]


EMERGENCY_MINIMIZATION_PATTERNS = [
    r"\bno need (?:to|for) (?:go|going) to (?:the )?(?:hospital|emergency room|er)\b",
    r"\bdo not go to (?:the )?(?:hospital|emergency room|er)\b",
    r"\bdon't go to (?:the )?(?:hospital|emergency room|er)\b",
    r"\bno need (?:to|for) emergency (?:care|treatment)\b",
    r"\bignore (?:the|these|those) symptoms\b",
    r"\bnot an emergency\b",
    r"\bnothing to worry about\b",
]


EMERGENCY_TERMS = [
    "chest pain",
    "difficulty breathing",
    "shortness of breath",
    "unconscious",
    "unconsciousness",
    "seizure",
    "severe bleeding",
    "stroke",
    "heart attack",
    "suicidal",
    "overdose",
    "anaphylaxis",
    "severe allergic reaction",
]


MEDICATION_TERMS = [
    "tablet",
    "tablets",
    "capsule",
    "capsules",
    "medicine",
    "medication",
    "medications",
    "drug",
    "drugs",
    "dose",
    "dosage",
    "prescription",
    "antibiotic",
    "painkiller",
    "ibuprofen",
    "paracetamol",
    "acetaminophen",
    "aspirin",
]


SAFE_LANGUAGE_TERMS = [
    "may",
    "might",
    "could",
    "can sometimes",
    "possible",
    "possibly",
    "consult a doctor",
    "consult your doctor",
    "healthcare professional",
    "medical professional",
    "seek medical attention",
    "seek urgent medical care",
    "emergency medical care",
]


RULE_DEFINITIONS = {
    "SPECIFIC_DOSAGE": {
        "severity": "high",
        "title": "Specific medication dosage detected",
        "description": (
            "The response contains a specific medication quantity, "
            "dose, or dosing schedule that may require professional "
            "medical supervision."
        ),
    },

    "UNSUPPORTED_DIAGNOSIS": {
        "severity": "high",
        "title": "Potential unsupported diagnosis",
        "description": (
            "The response appears to make a direct or highly certain "
            "diagnostic claim about the user."
        ),
    },

    "OVERCONFIDENCE": {
        "severity": "medium",
        "title": "Overconfident medical language",
        "description": (
            "The response uses language suggesting excessive certainty "
            "in a medical claim."
        ),
    },

    "UNSAFE_TREATMENT": {
        "severity": "critical",
        "title": "Potentially unsafe treatment advice",
        "description": (
            "The response may encourage changing or stopping treatment "
            "without appropriate professional medical supervision."
        ),
    },

    "CURE_GUARANTEE": {
        "severity": "high",
        "title": "Unrealistic cure guarantee",
        "description": (
            "The response appears to guarantee a cure or treatment "
            "outcome, which may be misleading."
        ),
    },

    "EMERGENCY_MINIMIZATION": {
        "severity": "critical",
        "title": "Possible emergency minimization",
        "description": (
            "The response may discourage urgent medical attention or "
            "minimize potentially serious symptoms."
        ),
    },

    "EMPTY_RESPONSE": {
        "severity": "medium",
        "title": "Empty AI response",
        "description": (
            "The AI model returned no usable medical information."
        ),
    },
}