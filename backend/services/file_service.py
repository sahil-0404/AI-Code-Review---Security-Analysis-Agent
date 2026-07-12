from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from backend.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE, UPLOAD_DIR


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def language_from_extension(extension: str) -> str:
    if extension == ".py":
        return "python"
    if extension == ".java":
        return "java"
    raise HTTPException(status_code=400, detail="Only .py and .java files are supported.")


def ensure_allowed_file(filename: str) -> None:
    if get_file_extension(filename) not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .py and .java files are supported.")


async def save_upload(upload: UploadFile) -> tuple[Path, str]:
    if upload.filename is None:
        raise HTTPException(status_code=400, detail="No filename provided.")

    extension = get_file_extension(upload.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    content = await upload.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="Maximum upload size is 5 MB.")

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded.") from exc

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIR / f"{uuid4().hex}{Path(upload.filename).suffix.lower()}"
    destination.write_text(text, encoding="utf-8")
    return destination, text
