from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router
from rag.vectordb import seed_knowledge_base

app = FastAPI(
    title="AI Code Review and Security Analysis Agent",
    description="Milestone 1 backend: code submission, syntax validation, and vector DB knowledge base.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.on_event("startup")
def startup():
    seed_knowledge_base()


@app.get("/")
def root() -> dict:
    return {
        "message": "AI Code Review and Security Analysis Agent - Milestone 1 API",
        "docs": "/docs",
    }
