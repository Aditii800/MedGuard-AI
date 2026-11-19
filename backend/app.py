
from flask import Flask, request, jsonify
from flask_cors import CORS

from services.ai_service import generate_medical_response
from services.emergency_guard import (
    detect_emergency_question,
    emergency_safe_response,
)
from services.safety_service import analyze_ai_response
from services.claim_verifier import verify_medical_claims
from services.response_guard import guard_response
from detection.risk_classifier import classify_risk

from database import (
    init_database,
    save_analysis,
    get_history,
    get_dashboard_stats,
    delete_history,
)

from evaluation.evaluator import run_evaluation


app = Flask(__name__)
CORS(app)

init_database()


# ============================================================
# HYBRID RISK AND FINAL RESPONSE GUARD
# ============================================================

def apply_hybrid_risk(
    safety_analysis,
    claim_verification,
    question="",
    ai_response="",
):
    """
    Apply hybrid heuristic scoring, verification fail-safe,
    and original-question emergency screening.

    Scores are experimental indicators, not clinical probabilities.
    """

    hybrid = classify_risk(
        safety_analysis,
        claim_verification,
    )

    risk_score = hybrid["risk_score"]
    risk_level = hybrid["risk_level"]
    risk_message = hybrid["risk_message"]

    verification_status = claim_verification.get(
        "verification_status",
        "UNAVAILABLE",
    )

    # A missing status is not evidence that verification succeeded.
    if verification_status != "COMPLETED" and risk_level == "LOW":
        risk_score = max(risk_score, 30)
        risk_level = "MEDIUM"
        risk_message = (
            "Claim verification was unavailable or inconclusive. "
            "The generated response is withheld pending review."
        )

    safety_analysis.update({
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_message": risk_message,
        "rule_based_score": hybrid["rule_based_score"],
        "semantic_risk_score": hybrid["semantic_risk_score"],
        "score_breakdown": hybrid["score_breakdown"],
        "scoring_method": hybrid["scoring_method"],
        "verification_status": verification_status,
    })

    # Always guard the original generated answer.
    safety_analysis.update(
        guard_response(
            ai_response,
            safety_analysis,
        )
    )

    # Emergency screening uses the original user question.
    emergency_type = detect_emergency_question(question)
    safety_analysis["emergency_override"] = bool(emergency_type)

    if emergency_type:
        safety_analysis.update({
            "risk_score": max(60, risk_score),
            "risk_level": "HIGH",
            "risk_message": (
                "The original question triggered a possible emergency "
                "safety rule. The generated answer has been withheld."
            ),
            "delivery_action": "BLOCK",
            "response_blocked": True,
            "safe_response": emergency_safe_response(emergency_type),
            "guard_message": (
                "The generated answer was withheld because the original "
                "question triggered an emergency safety rule."
            ),
            "emergency_context": True,
        })

    return safety_analysis


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Medical AI Safety Middleware Backend is Running",
        "version": "Major Project - Hybrid Safety Middleware",
        "ai_provider": "Configured provider from backend/services/ai_service.py",
        "claim_verification_model": (
            "Configured AI-based claim verifier; see backend/services/claim_verifier.py"
        ),
        "safety_engine": (
            "AI response generation + model-based claim verification + "
            "rule-based safety detection + hybrid heuristic risk scoring + "
            "emergency override + response guard + SQLite history + evaluation"
        ),
    })


# ============================================================
# ANALYZE MEDICAL QUESTION
# ============================================================

@app.route("/api/analyze", methods=["POST"])
def analyze_question():
    try:
        data = request.get_json(silent=True) or {}
        question = str(data.get("question", "")).strip()

        if not question:
            return jsonify({
                "success": False,
                "message": "Please enter a medical question",
            }), 400

        # 1. Generate the response.
        print("STEP 1: Generating AI medical response...")
        ai_response = generate_medical_response(question)
        print("AI response generation completed.")

        # 2. Verify claims.
        print("STEP 2: Verifying medical claims...")
        claim_verification = verify_medical_claims(ai_response)
        print(
            "Claim verification status:",
            claim_verification.get("verification_status", "UNAVAILABLE"),
        )

        # 3. Detect response safety indicators.
        print("STEP 3: Running rule-based safety analysis...")
        safety_analysis = analyze_ai_response(ai_response)

        # 4. Apply hybrid scoring and emergency override.
        print("STEP 4: Applying final safety decision...")
        safety_analysis = apply_hybrid_risk(
            safety_analysis,
            claim_verification,
            question,
            ai_response,
        )

        print("Final risk:", safety_analysis["risk_level"])
        print("Delivery action:", safety_analysis["delivery_action"])

        # 5. Persist the final, guarded response.
        analysis_id = save_analysis(
            question=question,
            safe_response=safety_analysis["safe_response"],
            risk_score=safety_analysis["risk_score"],
            risk_level=safety_analysis["risk_level"],
            delivery_action=safety_analysis["delivery_action"],
            response_blocked=safety_analysis["response_blocked"],
            flag_count=safety_analysis["flag_count"],
        )

        # 6. Return the original response for clearly labeled research
        # inspection, plus the actual guarded response for delivery.
        # The frontend must not present ai_response as trusted advice.
        response = {
            "success": True,
            "analysis_id": analysis_id,
            "question": question,

            "ai_response": ai_response,
            "safe_response": safety_analysis["safe_response"],

            "claim_verification": claim_verification,
            "verification_status": safety_analysis["verification_status"],
            "verification_score": claim_verification["verification_score"],
            "verified_claim_count": claim_verification["total_claims"],
            "supported_claim_count": claim_verification["supported_claims"],
            "uncertain_claim_count": claim_verification["uncertain_claims"],
            "unsupported_claim_count": claim_verification["unsupported_claims"],

            "delivery_action": safety_analysis["delivery_action"],
            "response_blocked": safety_analysis["response_blocked"],
            "guard_message": safety_analysis["guard_message"],
            "safety_explanations": safety_analysis["safety_explanations"],

            "flags": safety_analysis["flags"],
            "flag_count": safety_analysis["flag_count"],
            "has_safety_concern": safety_analysis["has_safety_concern"],

            "medication_context": safety_analysis["medication_context"],
            "emergency_context": safety_analysis.get("emergency_context", False),
            "emergency_override": safety_analysis["emergency_override"],
            "safe_language_detected": safety_analysis["safe_language_detected"],

            "risk_score": safety_analysis["risk_score"],
            "risk_level": safety_analysis["risk_level"],
            "risk_message": safety_analysis["risk_message"],
            "rule_based_score": safety_analysis["rule_based_score"],
            "semantic_risk_score": safety_analysis["semantic_risk_score"],
            "scoring_method": safety_analysis["scoring_method"],
            "score_breakdown": safety_analysis["score_breakdown"],
        }

        return jsonify(response), 200

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error),
        }), 400

    except Exception as error:
        app.logger.exception("Analysis request failed")
        return jsonify({
            "success": False,
            "message": "Response analysis failed. Check the backend terminal.",
        }), 500


# ============================================================
# CONTROLLED SAFETY TEST
# ============================================================

@app.route("/api/test-safety", methods=["POST"])
def test_safety():
    try:
        data = request.get_json(silent=True) or {}
        response_text = str(data.get("response", "")).strip()
        question = str(data.get("question", "")).strip()

        if not response_text:
            return jsonify({
                "success": False,
                "message": "Please provide a response to test",
            }), 400

        claim_verification = verify_medical_claims(response_text)
        safety_analysis = analyze_ai_response(response_text)

        safety_analysis = apply_hybrid_risk(
            safety_analysis,
            claim_verification,
            question,
            response_text,
        )

        return jsonify({
            "success": True,
            "tested_response": response_text,
            "claim_verification": claim_verification,
            "analysis": safety_analysis,
        }), 200

    except Exception:
        app.logger.exception("Safety test failed")
        return jsonify({
            "success": False,
            "message": "Safety analysis test failed.",
        }), 500


# ============================================================
# HISTORY
# ============================================================

@app.route("/api/history", methods=["GET"])
def history():
    try:
        limit = request.args.get("limit", default=50, type=int)
        limit = max(1, min(limit, 100))
        history_data = get_history(limit=limit)

        return jsonify({
            "success": True,
            "count": len(history_data),
            "history": history_data,
        }), 200

    except Exception:
        app.logger.exception("History retrieval failed")
        return jsonify({
            "success": False,
            "message": "Unable to retrieve history.",
        }), 500


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    try:
        return jsonify({
            "success": True,
            "dashboard": get_dashboard_stats(),
        }), 200

    except Exception:
        app.logger.exception("Dashboard retrieval failed")
        return jsonify({
            "success": False,
            "message": "Unable to load dashboard.",
        }), 500


# ============================================================
# DELETE HISTORY
# ============================================================

@app.route("/api/history", methods=["DELETE"])
def clear_history():
    try:
        delete_history()
        return jsonify({
            "success": True,
            "message": "Analysis history deleted successfully.",
        }), 200

    except Exception:
        app.logger.exception("History deletion failed")
        return jsonify({
            "success": False,
            "message": "Unable to delete history.",
        }), 500


# ============================================================
# MIDDLEWARE EVALUATION
# ============================================================

@app.route("/api/evaluation", methods=["GET"])
def evaluation():
    try:
        return jsonify({
            "success": True,
            "evaluation": run_evaluation(),
        }), 200

    except Exception:
        app.logger.exception("Evaluation failed")
        return jsonify({
            "success": False,
            "message": "Unable to run middleware evaluation.",
        }), 500


# ============================================================
# CLAIM VERIFICATION TEST
# ============================================================

@app.route("/api/test-claims", methods=["POST"])
def test_claims():
    try:
        data = request.get_json(silent=True) or {}
        response_text = str(data.get("response", "")).strip()

        if not response_text:
            return jsonify({
                "success": False,
                "message": "Please provide medical text to verify.",
            }), 400

        return jsonify({
            "success": True,
            "verification": verify_medical_claims(response_text),
        }), 200

    except Exception:
        app.logger.exception("Claim verification failed")
        return jsonify({
            "success": False,
            "message": "Medical claim verification failed.",
        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
