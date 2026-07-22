from fastapi import APIRouter, File, Header, HTTPException, UploadFile

from backend.agents.orchestrator import AgentOrchestrator
from backend.models.auth_models import LoginRequest, SignupRequest
from backend.models.request_models import PasteCodeRequest
from backend.services.auth_service import authenticate_user, create_user
from backend.services.file_service import get_file_extension, language_from_extension, save_upload
from backend.validator import validate_code
from rag.vectordb import get_collection_stats, search_knowledge_base, seed_knowledge_base


router = APIRouter()
orchestrator = AgentOrchestrator()


@router.post("/auth/signup", status_code=201)
def signup(payload: SignupRequest) -> dict:
    try:
        user = create_user(payload.name, payload.email, payload.password)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {"message": "Account created successfully.", "user": user}


@router.post("/auth/login")
def login(payload: LoginRequest) -> dict:
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"message": "Login successful.", "user": user}


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


def _validation_response(
    source: str,
    language: str,
    code: str,
    defer_remediation: bool = False,
) -> dict:
    validation = validate_code(language, code)
    return {
        "source": source,
        "language": language.lower(),
        "validation": validation,
        "analysis": orchestrator.analyze(
            code,
            language,
            validation,
            include_remediation=not defer_remediation,
        ),
    }


@router.post("/validate/paste")
def validate_pasted_code(
    payload: PasteCodeRequest,
    x_defer_remediation: str | None = Header(default=None),
) -> dict:
    return _validation_response(
        "paste",
        payload.language,
        payload.code,
        defer_remediation=x_defer_remediation == "true",
    )


@router.post("/validate/upload")
async def validate_uploaded_code(
    file: UploadFile = File(...),
    x_defer_remediation: str | None = Header(default=None),
) -> dict:
    _, code = await save_upload(file)
    language = language_from_extension(get_file_extension(file.filename or ""))
    return _validation_response(
        "upload",
        language,
        code,
        defer_remediation=x_defer_remediation == "true",
    )


@router.get("/knowledge/search")
def search_knowledge(query: str, limit: int = 3) -> dict:
    return {"query": query, "results": search_knowledge_base(query=query, limit=limit)}


@router.post("/knowledge/seed")
def seed_knowledge() -> dict:
    return seed_knowledge_base()
