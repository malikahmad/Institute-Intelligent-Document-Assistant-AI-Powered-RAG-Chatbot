import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
BASE = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE / 'institute_rag.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024
    UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", BASE / "uploads"))
    VECTOR_FOLDER = Path(os.getenv("VECTOR_FOLDER", BASE / "vector_db"))
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    ENABLE_RERANKER = os.getenv("ENABLE_RERANKER", "false").lower() == "true"
    RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    TOP_K = int(os.getenv("TOP_K", 8))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 900))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 150))
    OCR_ENABLED = os.getenv("OCR_ENABLED", "false").lower() == "true"
    TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")
    ADMIN_NAME = os.getenv("ADMIN_NAME", "Administrator")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
