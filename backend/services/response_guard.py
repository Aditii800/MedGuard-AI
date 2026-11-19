# ============================================================
# MEDICAL AI SAFETY MIDDLEWARE
# Response Guard / Safe Delivery Layer
# ============================================================


FLAG_EXPLANATIONS = {
    "SPECIFIC_DOSAGE": (
        "The response contains a specific medication dosage "
        "or dosing schedule."
    ),

    "UNSUPPORTED_DIAGNOSIS": (
        "The response appears to make a direct diagnostic "
        "claim without confirmed clinical evaluation."
    ),

    "OVERCONFIDENCE": (
        "The response uses language that may imply too much "
        "certainty for a medical situation."
    ),

    "UNSAFE_TREATMENT": (
        "The response may encourage unsafe treatment changes "
        "without medical supervision."
    ),

    "CURE_GUARANTEE": (
        "The response appears to guarantee a cure or treatment "
        "outcome."
    ),

    "EMERGENCY_MINIMIZATION": (
        "The response may minimize symptoms that could require "
        "urgent medical attention."
    ),

    "EMPTY_RESPONSE": (
        "The AI model did not return a usable medical response."
    ),
}


def build_explanations(flags):
    """
    Convert safety flags into clear,
    human-readable explanations.
    """

    explanations = []

    for flag in flags:

        flag_code = flag.get(
            "code",
            ""
        )

        explanation = FLAG_EXPLANATIONS.get(
            flag_code
        )

        if explanation:

            explanations.append({
                "code": flag_code,
                "message": explanation
            })

    return explanations


def guard_response(
    ai_response,
    safety_analysis
):
    """
    Decide what response can safely be delivered
    to the user based on the calculated risk level.

    LOW:
        Allow original AI response.

    MEDIUM:
        Do not rely on raw AI response directly.
        Return a cautionary review message.

    HIGH:
        Block the raw AI response and return a
        deterministic safety message.
    """

    risk_level = safety_analysis.get(
        "risk_level",
        "LOW"
    )

    flags = safety_analysis.get(
        "flags",
        []
    )

    explanations = build_explanations(
        flags
    )

    # ========================================================
    # LOW RISK
    # ========================================================

    if risk_level == "LOW":

        return {
            "delivery_action": "ALLOW",

            "response_blocked": False,

            "safe_response": ai_response,

            "safety_explanations": explanations,

            "guard_message": (
                "The response passed the current "
                "rule-based safety checks."
            )
        }

    # ========================================================
    # MEDIUM RISK
    # ========================================================

    if risk_level == "MEDIUM":

        safe_response = (
            "This AI-generated medical response contains "
            "one or more safety indicators and should not "
            "be relied upon without professional review.\n\n"
            "Please consult a qualified healthcare "
            "professional for diagnosis, medication, or "
            "treatment decisions."
        )

        return {
            "delivery_action": "REVIEW",

            "response_blocked": True,

            "safe_response": safe_response,

            "safety_explanations": explanations,

            "guard_message": (
                "The original AI response was withheld "
                "because medium-risk safety indicators "
                "were detected."
            )
        }

    # ========================================================
    # HIGH RISK
    # ========================================================

    safe_response = (
        "The AI-generated medical response was blocked by "
        "the Medical AI Safety Middleware because high-risk "
        "safety indicators were detected.\n\n"
        "Do not use the blocked response for diagnosis, "
        "medication dosage, treatment changes, or emergency "
        "decisions.\n\n"
        "Please seek guidance from a qualified healthcare "
        "professional. If there may be a medical emergency, "
        "seek urgent medical care immediately."
    )

    return {
        "delivery_action": "BLOCK",

        "response_blocked": True,

        "safe_response": safe_response,

        "safety_explanations": explanations,

        "guard_message": (
            "The original AI response was blocked because "
            "high-risk medical safety indicators were detected."
        )
    }