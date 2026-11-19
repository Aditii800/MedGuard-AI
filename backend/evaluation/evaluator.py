from evaluation.test_cases import TEST_CASES

from services.safety_service import (
    analyze_ai_response
)


def run_evaluation():
    """
    Evaluate the rule-based middleware using
    a controlled synthetic test dataset.

    These metrics measure performance only on
    this test dataset. They are not clinical
    safety or diagnostic accuracy metrics.
    """

    results = []

    correct = 0

    true_positive = 0
    false_positive = 0
    false_negative = 0
    true_negative = 0

    detected_rules = set()

    total_flag_count = 0

    for case in TEST_CASES:

        analysis = analyze_ai_response(
            case["text"]
        )

        predicted_risk = analysis[
            "risk_level"
        ]

        expected_risk = case[
            "expected_risk"
        ]

        is_correct = (
            predicted_risk == expected_risk
        )

        if is_correct:
            correct += 1

        # ----------------------------------------------------
        # Binary safety evaluation
        #
        # LOW = no major safety concern
        # MEDIUM/HIGH = safety concern
        # ----------------------------------------------------

        expected_unsafe = (
            expected_risk in [
                "MEDIUM",
                "HIGH"
            ]
        )

        predicted_unsafe = (
            predicted_risk in [
                "MEDIUM",
                "HIGH"
            ]
        )

        if (
            expected_unsafe
            and predicted_unsafe
        ):
            true_positive += 1

        elif (
            not expected_unsafe
            and predicted_unsafe
        ):
            false_positive += 1

        elif (
            expected_unsafe
            and not predicted_unsafe
        ):
            false_negative += 1

        else:
            true_negative += 1

        flags = analysis.get(
            "flags",
            []
        )

        total_flag_count += len(
            flags
        )

        for flag in flags:
            detected_rules.add(
                flag["code"]
            )

        results.append({
            "id": case["id"],
            "text": case["text"],
            "expected_risk":
                expected_risk,
            "predicted_risk":
                predicted_risk,
            "risk_score":
                analysis["risk_score"],
            "delivery_action":
                analysis["delivery_action"],
            "flag_count":
                analysis["flag_count"],
            "flags": [
                flag["code"]
                for flag in flags
            ],
            "correct":
                is_correct
        })

    total_cases = len(
        TEST_CASES
    )

    accuracy = (
        correct / total_cases
        if total_cases
        else 0
    )

    precision_denominator = (
        true_positive
        + false_positive
    )

    precision = (
        true_positive
        / precision_denominator
        if precision_denominator
        else 0
    )

    recall_denominator = (
        true_positive
        + false_negative
    )

    recall = (
        true_positive
        / recall_denominator
        if recall_denominator
        else 0
    )

    f1_denominator = (
        precision + recall
    )

    f1_score = (
        2 * precision * recall
        / f1_denominator
        if f1_denominator
        else 0
    )

    return {
        "evaluation_type": (
            "Controlled Synthetic "
            "Middleware Evaluation"
        ),

        "total_cases":
            total_cases,

        "correct_predictions":
            correct,

        "risk_classification_accuracy":
            round(
                accuracy * 100,
                2
            ),

        "binary_safety_metrics": {
            "precision": round(
                precision * 100,
                2
            ),
            "recall": round(
                recall * 100,
                2
            ),
            "f1_score": round(
                f1_score * 100,
                2
            )
        },

        "confusion_matrix": {
            "true_positive":
                true_positive,
            "false_positive":
                false_positive,
            "false_negative":
                false_negative,
            "true_negative":
                true_negative
        },

        "rule_coverage": {
            "unique_rules_triggered":
                len(detected_rules),
            "rules_triggered":
                sorted(
                    list(
                        detected_rules
                    )
                ),
            "total_flags_detected":
                total_flag_count
        },

        "results":
            results,

        "disclaimer": (
            "Results are measured on a controlled "
            "synthetic dataset and do not represent "
            "clinical accuracy, diagnostic accuracy, "
            "or real-world medical safety."
        )
    }