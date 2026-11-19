import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = (
    BASE_DIR / "medical_ai_safety.db"
)


def get_connection():
    """
    Create and return a SQLite database connection.
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database():
    """
    Create the analysis_history table
    if it does not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            question TEXT NOT NULL,

            safe_response TEXT NOT NULL,

            risk_score INTEGER NOT NULL,

            risk_level TEXT NOT NULL,

            delivery_action TEXT NOT NULL,

            response_blocked INTEGER NOT NULL,

            flag_count INTEGER NOT NULL,

            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def save_analysis(
    question,
    safe_response,
    risk_score,
    risk_level,
    delivery_action,
    response_blocked,
    flag_count
):
    """
    Save one middleware analysis result.
    """

    connection = get_connection()

    cursor = connection.cursor()

    created_at = datetime.now().isoformat(
        timespec="seconds"
    )

    cursor.execute(
        """
        INSERT INTO analysis_history (
            question,
            safe_response,
            risk_score,
            risk_level,
            delivery_action,
            response_blocked,
            flag_count,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            question,
            safe_response,
            risk_score,
            risk_level,
            delivery_action,
            int(response_blocked),
            flag_count,
            created_at
        )
    )

    connection.commit()

    analysis_id = cursor.lastrowid

    connection.close()

    return analysis_id


def get_history(limit=50):
    """
    Return recent middleware analysis history.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            question,
            safe_response,
            risk_score,
            risk_level,
            delivery_action,
            response_blocked,
            flag_count,
            created_at
        FROM analysis_history
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            limit,
        )
    )

    rows = cursor.fetchall()

    connection.close()

    history = []

    for row in rows:

        history.append({
            "id": row["id"],
            "question": row["question"],
            "safe_response": row["safe_response"],
            "risk_score": row["risk_score"],
            "risk_level": row["risk_level"],
            "delivery_action": row[
                "delivery_action"
            ],
            "response_blocked": bool(
                row["response_blocked"]
            ),
            "flag_count": row["flag_count"],
            "created_at": row["created_at"]
        })

    return history


def get_dashboard_stats():
    """
    Calculate dashboard statistics from
    stored middleware analyses.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM analysis_history
        """
    )

    total = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM analysis_history
        WHERE risk_level = 'LOW'
        """
    )

    low_count = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM analysis_history
        WHERE risk_level = 'MEDIUM'
        """
    )

    medium_count = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM analysis_history
        WHERE risk_level = 'HIGH'
        """
    )

    high_count = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM analysis_history
        WHERE response_blocked = 1
        """
    )

    blocked_count = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT AVG(risk_score) AS average_score
        FROM analysis_history
        """
    )

    average_result = cursor.fetchone()[
        "average_score"
    ]

    average_score = (
        round(average_result, 2)
        if average_result is not None
        else 0
    )

    connection.close()

    return {
        "total_analyses": total,
        "low_risk": low_count,
        "medium_risk": medium_count,
        "high_risk": high_count,
        "blocked_responses": blocked_count,
        "average_risk_score": average_score
    }


def delete_history():
    """
    Delete all stored middleware history.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM analysis_history
        """
    )

    connection.commit()
    connection.close()