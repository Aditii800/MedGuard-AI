import json

from evaluation.evaluator import (
    run_evaluation
)


def main():

    print(
        "\n"
        "=========================================="
    )

    print(
        " Medical AI Safety Middleware Evaluation"
    )

    print(
        "==========================================\n"
    )

    evaluation = run_evaluation()

    print(
        json.dumps(
            evaluation,
            indent=4
        )
    )


if __name__ == "__main__":
    main()