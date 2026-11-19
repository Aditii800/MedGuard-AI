
import os
from dotenv import load_dotenv

# Load environment variables from the backend .env file.
load_dotenv()

# ============================================================
# GROQ CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

GROQ_JUDGE_MODEL = os.getenv(
    "GROQ_JUDGE_MODEL",
    "openai/gpt-oss-120b"
)

GROQ_TEMPERATURE = float(
    os.getenv("GROQ_TEMPERATURE", "0.9")
)

GROQ_MAX_TOKENS = int(
    os.getenv("GROQ_MAX_TOKENS", "2000")
)

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY is not configured.")

# ============================================================
# GEMINI CONFIGURATION
# Retained for compatibility with other project modules.
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

if not GEMINI_API_KEY:
    print("INFO: GEMINI_API_KEY is not configured.")
