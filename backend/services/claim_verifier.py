
import re
import torch
from sentence_transformers import SentenceTransformer, util


# ============================================================
# MEDICAL AI SAFETY MIDDLEWARE
# Semantic Medical Claim Verification Engine
# ============================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

SYNTHETIC_MARKER = (
    "[SYNTHETIC TEST CLAIM — VERIFY INDEPENDENTLY]"
)

SUPPORTED_THRESHOLD = 0.70
UNCERTAIN_THRESHOLD = 0.45
MAX_CLAIMS = 8
TOP_K = 3

embedding_model = None
knowledge_embeddings = None


# ============================================================
# CURATED LOCAL MEDICAL KNOWLEDGE BASE
# These are evidence statements, not a complete medical source.
# Add reputable, traceable references before clinical use.
# ============================================================

KNOWLEDGE_ITEMS = [
    ("headache", "Dehydration can contribute to headaches."),
    ("headache", "Lack of sleep can contribute to headaches."),
    ("headache", "Stress can trigger tension-type headaches."),
    ("headache", "Migraine can cause moderate to severe recurring headaches."),
    ("headache", "Headaches can have many different causes."),
    ("headache", "A sudden extremely severe headache can require urgent medical evaluation."),
    ("headache", "A headache with weakness, confusion, fainting, or difficulty speaking can require emergency evaluation."),
    ("fever", "Fever can occur when the body is responding to an infection."),
    ("fever", "Both viral and bacterial infections can cause fever."),
    ("fever", "Persistent or severe fever may require medical evaluation."),
    ("infection", "Antibiotics are used to treat certain bacterial infections."),
    ("infection", "Antibiotics do not treat viral infections such as the common cold."),
    ("cold_flu", "The common cold is usually caused by a viral infection."),
    ("cold_flu", "Common cold symptoms can include a runny nose, sore throat, sneezing, and cough."),
    ("cold_flu", "Influenza can cause fever, cough, body aches, fatigue, and headache."),
    ("cough", "A cough can occur with respiratory infections."),
    ("cough", "A persistent cough may require medical evaluation."),
    ("cough", "Coughing up blood requires prompt medical evaluation."),
    ("chest_pain", "Chest pain can have many different causes."),
    ("chest_pain", "Chest pain may require medical evaluation depending on severity and associated symptoms."),
    ("chest_pain", "Severe chest pain with difficulty breathing can require emergency medical care."),
    ("chest_pain", "Chest discomfort with sweating, nausea, fainting, or shortness of breath can require urgent evaluation."),
    ("breathing", "Severe difficulty breathing can be a medical emergency."),
    ("blood_pressure", "High blood pressure may not always cause noticeable symptoms."),
    ("blood_pressure", "Blood pressure measurement is used when evaluating hypertension."),
    ("blood_pressure", "Persistently high blood pressure should be evaluated by a healthcare professional."),
    ("diabetes", "Diabetes is diagnosed using medical evaluation and blood glucose testing."),
    ("diabetes", "Symptoms of diabetes can include increased thirst and frequent urination."),
    ("diabetes", "Unexplained weight loss can occur in some people with diabetes."),
    ("diabetes", "Symptoms alone are not sufficient to confirm a diagnosis of diabetes."),
    ("dehydration", "Dehydration occurs when the body loses more fluid than it takes in."),
    ("dehydration", "Dehydration can cause thirst, dry mouth, dizziness, and fatigue."),
    ("dehydration", "Severe dehydration can require medical treatment."),
    ("digestive", "Abdominal pain can have many different causes."),
    ("digestive", "Vomiting and diarrhea can contribute to dehydration."),
    ("digestive", "Persistent or severe abdominal pain should be medically evaluated."),
    ("digestive", "Blood in vomit or stool can require urgent medical evaluation."),
    ("allergy", "Allergic reactions can cause itching, rash, swelling, or respiratory symptoms."),
    ("allergy", "Severe allergic reactions can cause difficulty breathing."),
    ("allergy", "A severe allergic reaction with breathing difficulty requires emergency medical care."),
    ("medication", "Prescription medicines should be used according to guidance from a qualified healthcare professional."),
    ("medication", "A prescribed medicine should not be stopped without appropriate medical guidance."),
    ("medication", "Medication doses can depend on age, medical condition, other medicines, and individual health factors."),
    ("medication", "Medicines can cause side effects or interact with other medicines."),
    ("medication", "Medical advice may be necessary before starting a new medicine."),
    ("diagnosis", "A medical diagnosis may require history, physical examination, and appropriate testing."),
    ("diagnosis", "Symptoms can have multiple possible causes and do not always identify one specific disease."),
    ("diagnosis", "Online medical information should not replace professional evaluation when diagnosis is needed."),
    ("diagnosis", "Persistent or worsening symptoms should be evaluated by a healthcare professional."),
    ("emergency", "Loss of consciousness can require emergency medical evaluation."),
    ("emergency", "Sudden weakness or numbness on one side of the body can require emergency medical evaluation."),
    ("emergency", "Sudden difficulty speaking can require emergency medical evaluation."),
    ("emergency", "Severe uncontrolled bleeding can require emergency medical care."),
    ("emergency", "Seizures can require urgent medical assessment, particularly when new, prolonged, or repeated."),
    ("emergency", "Serious or rapidly worsening symptoms can require urgent medical evaluation."),
    
    ("diabetes", "Insulin is a hormone that helps regulate blood glucose levels."),
    ("diabetes", "The pancreas produces insulin, which helps glucose move from the blood into certain body cells."),
    ("diabetes", "Diabetes involves problems with insulin production, insulin action, or both, affecting blood glucose regulation."),
    # Additional diabetes evidence statements
    ("diabetes", "Type 1 diabetes involves autoimmune destruction of insulin-producing beta cells."),
    ("diabetes", "Type 2 diabetes involves problems with insulin action and may also involve inadequate insulin production."),
    ("diabetes", "Gestational diabetes is diabetes diagnosed during pregnancy that was not clearly diabetes before pregnancy."),
    ("diabetes", "Some people with gestational diabetes continue to have diabetes after pregnancy, while others do not."),
    ("diabetes", "Diabetes can cause increased thirst and frequent urination."),
    ("diabetes", "Diabetes may cause fatigue, blurred vision, and unexplained weight loss."),
    ("diabetes", "The HbA1c test reflects average blood glucose over approximately the previous two to three months."),
    ("diabetes", "Fasting plasma glucose and HbA1c are tests used to diagnose diabetes."),
    ("diabetes", "A healthcare professional interprets diabetes test results using established diagnostic criteria."),
    ("diabetes", "Diabetes can increase the risk of eye, kidney, nerve, and cardiovascular complications."),
    ("diabetes", "Diabetes management may include nutrition changes, physical activity, monitoring, and medication when indicated."),
    ("diabetes", "Diabetes treatment must be individualized to the person's circumstances and clinical needs."),
    ("diabetes", "Low blood glucose can cause sweating, shakiness, dizziness, confusion, and other symptoms."),
    ("diabetes", "Severely low blood glucose can be a medical emergency."),
    ("diabetes", "People with diabetes should not change prescribed medication doses solely on the basis of chatbot advice."),
    ("diabetes", "A single symptom cannot reliably establish whether a person has diabetes."),

]

MEDICAL_KNOWLEDGE_BASE = [
    {
        "id": index,
        "category": category,
        "claim": claim,
        "source": "Curated local medical knowledge base",
    }
    for index, (category, claim) in enumerate(KNOWLEDGE_ITEMS, start=1)
]


# ============================================================
# MODEL LOADING
# ============================================================

def get_knowledge_texts():
    return [item["claim"] for item in MEDICAL_KNOWLEDGE_BASE]


def load_embedding_model():
    global embedding_model, knowledge_embeddings

    if embedding_model is not None and knowledge_embeddings is not None:
        return

    print(f"Loading semantic verification model: {MODEL_NAME}")

    embedding_model = SentenceTransformer(MODEL_NAME)

    knowledge_embeddings = embedding_model.encode(
        get_knowledge_texts(),
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    print(
        "Semantic verification model loaded. "
        f"Knowledge entries: {len(MEDICAL_KNOWLEDGE_BASE)}"
    )


# ============================================================
# CLAIM EXTRACTION
# The marker applies to the following claim, not to the marker
# text itself. It is preserved as metadata for the verifier.
# ============================================================

def extract_claim_records(response_text):
    if not response_text:
        return []

    text = response_text.replace("\r\n", "\n").replace("\r", "\n")
    records = []
    pending_synthetic = False

    marker_pattern = r"\[\s*SYNTHETIC\s+TEST\s+CLAIM\b[^\]]*\]"

    skip_phrases = (
        "general medical information",
        "not a medical diagnosis",
        "important note",
        "main information",
        "important signs",
        "consult a healthcare professional",
        "consult a qualified healthcare professional",
    )

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        if re.search(marker_pattern, line, flags=re.IGNORECASE):
            line = re.sub(
                marker_pattern, "", line, flags=re.IGNORECASE
            ).strip()
            pending_synthetic = True

            if not line:
                continue

        line = re.sub(r"^#{1,6}\s*", "", line)
        line = line.replace("**", "").replace("__", "")
        line = re.sub(r"^\s*[-*]\s*", "", line).strip()

        parts = re.split(r"(?<=[.!?])\s+", line)

        for part in parts:
            claim = part.strip()
            claim = re.sub(r"^\s*[-*]\s*", "", claim).strip()

            if len(claim) < 15:
                continue

            lower_claim = claim.lower()

            if any(phrase in lower_claim for phrase in skip_phrases):
                continue

            if any(item["claim"] == claim for item in records):
                continue

            records.append({
                "claim": claim,
                "is_synthetic_test_claim": pending_synthetic,
            })

            pending_synthetic = False

            if len(records) >= MAX_CLAIMS:
                return records

    return records

def extract_claims(response_text):
    """Compatibility helper returning claim strings."""
    return [
        record["claim"]
        for record in extract_claim_records(response_text)
    ]


# ============================================================
# RESULT HELPERS
# ============================================================

def _hallucination_level(score):
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def _empty_result(note, verification_status="UNAVAILABLE"):
    return {
        "claims": [],
        "total_claims": 0,
        "supported_claims": 0,
        "uncertain_claims": 0,
        "unsupported_claims": 0,
        "verification_score": 0.0,
        "hallucination_score": 0.0,
        "hallucination_level": "UNKNOWN",
        "verification_status": verification_status,
        "knowledge_base_size": len(MEDICAL_KNOWLEDGE_BASE),
        "verification_method": "SEMANTIC_EVIDENCE_RETRIEVAL",
        "score_interpretation": "HEURISTIC_NOT_CONFIRMED_HALLUCINATION_RATE",
        "clinical_validation": "NOT_CLINICALLY_VALIDATED",
        "verification_note": note,
    }


# ============================================================
# ============================================================
# VERIFY ONE CLAIM
# Similarity retrieves evidence; it does not prove medical truth.
# ============================================================

def verify_single_claim(claim, is_synthetic_test_claim=False):
    load_embedding_model()

    claim_embedding = embedding_model.encode(
        claim,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )
    similarities = util.cos_sim(
        claim_embedding, knowledge_embeddings
    )[0]

    top_k = min(TOP_K, len(MEDICAL_KNOWLEDGE_BASE))
    top_results = torch.topk(similarities, k=top_k)

    best_index = int(top_results.indices[0].item())
    best_score = float(top_results.values[0].item())
    best_match = MEDICAL_KNOWLEDGE_BASE[best_index]

    confidence = round(max(0.0, min(best_score, 1.0)) * 100, 2)

    if best_score >= SUPPORTED_THRESHOLD:
        semantic_status = "SUPPORTED"
    elif best_score >= UNCERTAIN_THRESHOLD:
        semantic_status = "UNCERTAIN"
    else:
        semantic_status = "UNSUPPORTED"

    evidence_matches = []
    for score, index in zip(top_results.values, top_results.indices):
        evidence = MEDICAL_KNOWLEDGE_BASE[int(index.item())]
        evidence_matches.append({
            "evidence": evidence["claim"],
            "category": evidence["category"],
            "source": evidence["source"],
            "similarity": round(
                max(0.0, min(float(score.item()), 1.0)) * 100, 2
            ),
        })

    if is_synthetic_test_claim:
        status = "SYNTHETIC_REVIEW_REQUIRED"
        interpretation = (
            "Synthetic test claim. Evidence matches are retained, "
            "but this claim is not considered verified."
        )
    else:
        status = semantic_status
        if status == "SUPPORTED":
            interpretation = (
                "Similar evidence was retrieved. This is not independent "
                "proof that the claim is correct."
            )
        elif status == "UNCERTAIN":
            interpretation = (
                "Partial semantic similarity was found. Review the evidence."
            )
        else:
            interpretation = (
                "Sufficient semantic support was not found locally. "
                "This does not prove the claim is medically false."
            )

    return {
        "claim": claim,
        "status": status,
        "semantic_status": semantic_status,
        "confidence": confidence,
        "matched_evidence": best_match["claim"],
        "matched_category": best_match["category"],
        "source": best_match["source"],
        "evidence_matches": evidence_matches,
        "is_synthetic_test_claim": is_synthetic_test_claim,
        "claim_type": (
            "SYNTHETIC_TEST_CLAIM"
            if is_synthetic_test_claim else "ORDINARY_CLAIM"
        ),
        "interpretation": interpretation,
    }


# ============================================================
# VERIFY COMPLETE AI RESPONSE
# ============================================================

def verify_medical_claims(response_text):
    records = extract_claim_records(response_text)

    if not records:
        return _empty_result(
            "No verifiable claims were extracted. "
            "A lack of extracted claims is not successful verification.",
            verification_status="UNAVAILABLE",
        )

    try:
        results = [
            verify_single_claim(
                record["claim"],
                is_synthetic_test_claim=record["is_synthetic_test_claim"],
            )
            for record in records
        ]
    except Exception as exc:
        print(f"Claim verification failed: {exc}")
        return _empty_result(
            "Semantic verification could not complete. "
            "Do not interpret this as evidence that the response is safe.",
            verification_status="UNAVAILABLE",
        )

    synthetic_count = sum(
        item["is_synthetic_test_claim"] for item in results
    )
    ordinary_results = [
        item for item in results
        if not item["is_synthetic_test_claim"]
    ]

    supported = sum(
        item["status"] == "SUPPORTED" for item in ordinary_results
    )
    uncertain = sum(
        item["status"] == "UNCERTAIN" for item in ordinary_results
    )
    unsupported = sum(
        item["status"] == "UNSUPPORTED" for item in ordinary_results
    )
    ordinary_count = len(ordinary_results)

    if ordinary_count:
        verification_score = round(
            (supported + uncertain * 0.5) / ordinary_count * 100, 2
        )
        hallucination_score = round(100 - verification_score, 2)
        hallucination_level = _hallucination_level(hallucination_score)
    else:
        verification_score = 0.0
        hallucination_score = 0.0
        hallucination_level = "UNKNOWN"

    return {
        "claims": results,
        "total_claims": len(results),
        "ordinary_claims": ordinary_count,
        "synthetic_test_claim_count": synthetic_count,
        "supported_claims": supported,
        "uncertain_claims": uncertain,
        "unsupported_claims": unsupported,
        "verification_score": verification_score,
        "hallucination_score": hallucination_score,
        "hallucination_level": hallucination_level,
        "verification_status": "COMPLETED",
        "knowledge_base_size": len(MEDICAL_KNOWLEDGE_BASE),
        "verification_method": "SEMANTIC_EVIDENCE_RETRIEVAL",
        "score_interpretation": "HEURISTIC_NOT_CONFIRMED_HALLUCINATION_RATE",
        "clinical_validation": "NOT_CLINICALLY_VALIDATED",
        "verification_note": (
            "Semantic matches are retrieved from a curated local knowledge "
            "base. Synthetic test claims are marked for review and excluded "
            "from ordinary counts and scores. Similarity does not prove "
            "medical truth or falsity. Scores are heuristic, not a clinical "
            "safety probability."
        ),
    }
