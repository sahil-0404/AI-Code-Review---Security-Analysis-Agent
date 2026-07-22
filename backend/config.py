from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
VECTOR_DB_DIR = BASE_DIR / "vector_db" / "chroma"
AUTH_DB_PATH = BASE_DIR / "vector_db" / "users.sqlite3"

ALLOWED_EXTENSIONS = {".py", ".java"}
SUPPORTED_LANGUAGES = {"python", "java"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024

CHROMA_COLLECTION = "secure_coding_knowledge_base"
for directory in (UPLOAD_DIR, KNOWLEDGE_BASE_DIR, VECTOR_DB_DIR):
    directory.mkdir(parents=True, exist_ok=True)
