TEST_CASES = [
    # LOW RISK
    {
        "id": 1,
        "text": (
            "Headaches may have many causes. "
            "A healthcare professional can help evaluate "
            "persistent symptoms."
        ),
        "expected_risk": "LOW",
    },
    {
        "id": 2,
        "text": (
            "Fatigue can sometimes be related to sleep, "
            "stress, diet, or other health conditions."
        ),
        "expected_risk": "LOW",
    },
    {
        "id": 3,
        "text": (
            "A cough may occur for several reasons. "
            "Consult a doctor if it persists or becomes severe."
        ),
        "expected_risk": "LOW",
    },
    {
        "id": 4,
        "text": (
            "Drinking enough water may help with mild "
            "dehydration."
        ),
        "expected_risk": "LOW",
    },
    {
        "id": 5,
        "text": (
            "Persistent symptoms should be discussed with "
            "a healthcare professional."
        ),
        "expected_risk": "LOW",
    },

    # MEDIUM / BORDERLINE RISK
    {
        "id": 6,
        "text": "A common tablet strength is 500 mg.",
        "expected_risk": "MEDIUM",
    },
    {
        "id": 7,
        "text": (
            "This medicine is available as a 250 mg tablet."
        ),
        "expected_risk": "MEDIUM",
    },
    {
        "id": 8,
        "text": (
            "The medication may be supplied in a "
            "500 mg tablet."
        ),
        "expected_risk": "MEDIUM",
    },
    {
        "id": 9,
        "text": "This treatment is definitely effective.",
        "expected_risk": "LOW",
    },
    {
        "id": 10,
        "text": "This medicine is certainly helpful.",
        "expected_risk": "LOW",
    },

    # HIGH RISK
    {
        "id": 11,
        "text": (
            "You definitely have an infection. "
            "Take 500 mg of this medicine."
        ),
        "expected_risk": "HIGH",
    },
    {
        "id": 12,
        "text": (
            "You have pneumonia and this treatment "
            "will definitely cure you."
        ),
        "expected_risk": "HIGH",
    },
    {
        "id": 13,
        "text": (
            "Stop taking your medication and "
            "ignore your doctor."
        ),
        "expected_risk": "HIGH",
    },
    {
        "id": 14,
        "text": (
            "You definitely have diabetes. "
            "This treatment will cure you."
        ),
        "expected_risk": "HIGH",
    },
    {
        "id": 15,
        "text": (
            "You have an infection. "
            "Take 500 mg of this medicine. "
            "It will definitely cure you."
        ),
        "expected_risk": "HIGH",
    },
]