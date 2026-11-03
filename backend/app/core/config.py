import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "ResearchX"
    APP_ENV: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Paths
    DATA_DIR: str = str(BASE_DIR / "data")
    UPLOADS_DIR: str = str(BASE_DIR / "data" / "uploads")
    EXTRACTED_DIR: str = str(BASE_DIR / "data" / "extracted")
    SQLITE_DB_PATH: str = str(BASE_DIR / "data" / "researchx.db")
    QDRANT_STORAGE_PATH: str = str(BASE_DIR / "data" / "qdrant")

    # Models & Inference
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "llama3.2:1b"
    OLLAMA_FALLBACK_MODEL: str = "llama3.2:1b"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    RERANKER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ENABLE_RERANKER: bool = True
    ENABLE_VLM: bool = False
    VLM_MODEL_NAME: str = "moondream"

    # Retrieval Configuration Defaults
    DEFAULT_RETRIEVAL_MODE: str = "multimodal"  # text_only, hybrid, multimodal
    DEFAULT_TOP_K: int = 5
    DEFAULT_SCORE_THRESHOLD: float = 0.35
    BM25_WEIGHT: float = 0.35
    DENSE_WEIGHT: float = 0.65

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "allow"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.EXTRACTED_DIR, exist_ok=True)
if settings.QDRANT_STORAGE_PATH != ":memory:":
    os.makedirs(settings.QDRANT_STORAGE_PATH, exist_ok=True)
