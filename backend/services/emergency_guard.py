import re


OVERDOSE_PATTERNS = [
    # Direct overdose wording
    r"\boverdose(?:d)?\b",

    # General overdose concerns
    r"\btoo many\s+(?:tablets?|pills?|capsules?|doses?)\b",
    r"\btoo much\s+(?:medicine|medication|drug|of my medicine|of my medication)\b",

    # "I may have taken too much of my medicine"
    r"\b(?:i|we|someone|they)\s+"
    r"(?:(?:may|might|could)\s+have\s+|have\s+possibly\s+|possibly\s+)?"
    r"(?:accidentally\s+)?"
    r"(?:taken|took|swallowed|ingested)\s+"
    r"(?:too much|more than (?:the )?(?:recommended|prescribed|usual) amount|"
    r"an extra dose|extra doses)\b",

    # Specific number of tablets or pills
    r"\b(?:i|we|someone|they)\s+"
    r"(?:(?:may|might|could)\s+have\s+)?"
    r"(?:taken|took|swallowed|ingested)\s+\d+\s+"
    r"(?:tablets?|pills?|capsules?)\b",

    # Asking whether a large number of tablets is safe
    r"\b(?:can i|should i|is it safe to)\s+"
    r"(?:eat|take|swallow)\s+\d+\s+"
    r"(?:(?:tablets?|pills?|capsules?)\s+of\s+)?"
    r"(?:paracetamol|acetaminophen|ibuprofen|aspirin)\b",

    # Number of tablets followed by a medicine name
    r"\b(?:took|taken|swallowed|ingested)\s+\d+\s+"
    r"(?:tablets?|pills?|capsules?).{0,60}"
    r"\b(?:paracetamol|acetaminophen|ibuprofen|aspirin)\b",

    # Accidental extra or double dose
    r"\b(?:accidentally\s+)?(?:took|taken)\s+"
    r"(?:an extra dose|extra doses|a double dose|twice my dose)\b",

    # Taking more than prescribed
    r"\b(?:took|taken|taking)\s+more than\s+"
    r"(?:prescribed|recommended|the prescribed dose)\b",
]


URGENT_SYMPTOM_PATTERNS = [
    r"\b(?:i am|i'm|someone is|they are)\s+"
    r"(?:unconscious|having a seizure)\b",

    r"\b(?:i have|i'm having|experiencing)\s+"
    r"(?:severe\s+)?chest pain\b",

    r"\b(?:i can't breathe|i cannot breathe|"
    r"i am struggling to breathe|severe difficulty breathing)\b",

    r"\b(?:severe bleeding|signs of a stroke|having a heart attack)\b",

    r"\b(?:throat or tongue swelling|severe allergic reaction|anaphylaxis)\b",
]


def detect_emergency_question(question):
    """
    Conservative keyword-based screening of the original question.
    This is a safety trigger, not a medical diagnosis.
    """
    text = str(question or "").lower().strip()

    if not text:
        return None

    if any(re.search(pattern, text) for pattern in OVERDOSE_PATTERNS):
        return "POSSIBLE_OVERDOSE"

    if any(re.search(pattern, text) for pattern in URGENT_SYMPTOM_PATTERNS):
        return "POSSIBLE_EMERGENCY"

    return None


def emergency_safe_response(emergency_type):
    if emergency_type == "POSSIBLE_OVERDOSE":
        return (
            "POSSIBLE MEDICATION OVERDOSE — seek urgent professional help now.\n\n"
            "If you or someone else may have taken too much medicine, contact "
            "local emergency services or go to the nearest emergency department "
            "immediately. In India, call 112 for emergency assistance. Do not "
            "wait for symptoms, induce vomiting, or take more medicine unless "
            "a qualified medical professional or poison specialist instructs you. "
            "Keep the medicine packaging and tell medical staff what was taken, "
            "how much, and when."
        )

    return (
        "POSSIBLE MEDICAL EMERGENCY — seek urgent professional help now.\n\n"
        "Contact local emergency services or go to the nearest emergency "
        "department immediately if you or someone else may be experiencing "
        "a serious emergency. In India, call 112 for emergency assistance. "
        "Do not rely on an AI response to assess or manage an emergency."
    )