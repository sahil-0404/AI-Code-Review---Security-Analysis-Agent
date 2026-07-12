from fastapi import APIRouter, File, UploadFile

from backend.models.request_models import PasteCodeRequest
from backend.services.file_service import language_from_extension, get_file_extension, save_upload
from backend.validator import validate_code
from rag.vectordb import get_collection_stats, search_knowledge_base, seed_knowledge_base

router = APIRouter()


@router.get("/status")
def status() -> dict:
    return {
        "status": "running",
        "milestone": "Milestone 1",
        "features": [
            "paste code submission",
            "file upload submission",
            "python syntax validation",
            "java syntax validation",
            "ChromaDB knowledge base",
        ],
        "knowledge_base": get_collection_stats(),
    }


@router.post("/validate/paste")
def validate_pasted_code(payload: PasteCodeRequest) -> dict:
    result = validate_code(payload.language, payload.code)
    return {
        "source": "paste",
        "language": payload.language.lower(),
        "validation": result,
    }


@router.post("/validate/upload")
async def validate_uploaded_code(file: UploadFile = File(...)) -> dict:
    saved_path, code = await save_upload(file)
    language = language_from_extension(get_file_extension(file.filename or ""))
    result = validate_code(language, code)

    return {
        "source": "upload",
        "filename": file.filename,
        "saved_as": saved_path.name,
        "language": language,
        "validation": result,
    }


@router.get("/knowledge/search")
def search_knowledge(query: str, limit: int = 3) -> dict:
    return {
        "query": query,
        "results": search_knowledge_base(query=query, limit=limit),
    }


@router.post("/knowledge/seed")
def seed_knowledge() -> dict:
    return seed_knowledge_base()
