
import os
from pathlib import Path
from dotenv import load_dotenv


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_NAME = "DocMind"
BASE_DIR = Path(__file__).resolve().parent.parent


# --------------------------------------------------
# ENVIRONMENT VARIABLES
# --------------------------------------------------

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE, override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# --------------------------------------------------
# LLM CONFIGURATION
# --------------------------------------------------

LLM_MODEL = "openai/gpt-oss-120b"
TEMPERATURE = 0.0


# --------------------------------------------------
# DOCUMENT CONFIGURATION
# --------------------------------------------------

DOCS_DIR = BASE_DIR / "docs_dir"


# --------------------------------------------------
# VECTOR DATABASE CONFIGURATION
# --------------------------------------------------

VECTOR_DB_PATH = BASE_DIR / "vector_db"
COLLECTION_NAME = "document_collection"


# --------------------------------------------------
# TEXT SPLITTING CONFIGURATION
# --------------------------------------------------

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 500


# --------------------------------------------------
# HUGGING FACE EMBEDDING CONFIGURATION
# --------------------------------------------------

EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"


# --------------------------------------------------
# CONFIGURATION VALIDATION
# --------------------------------------------------

def validate_config():
    """
    Validate the required configuration
    for the DocMind RAG application.
    """

    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Please check your .env file."
        )

    # Create required directories if they do not exist
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

    return True
