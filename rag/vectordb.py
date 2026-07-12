import hashlib
import math
import re

from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from backend.config import CHROMA_COLLECTION, VECTOR_DB_DIR
from rag.documents import SEED_DOCUMENTS



def get_client() -> PersistentClient:
    return PersistentClient(path=str(VECTOR_DB_DIR))

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
def get_collection():
    return get_client().get_or_create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=embedding_function,
        metadata={"description": "Secure coding and OWASP knowledge base for Milestone 1"},
    )


def seed_knowledge_base() -> dict:
    collection = get_collection()
    existing_ids = set(collection.get(include=[])["ids"])

    ids = []
    documents = []
    metadatas = []
    for index, item in enumerate(SEED_DOCUMENTS, start=1):
        doc_id = f"seed-{index}"
        if doc_id in existing_ids:
            continue
        ids.append(doc_id)
        documents.append(item["text"])
        metadatas.append({"title": item["title"], "category": item["category"], "source": "seed"})

    if ids:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    return {"added": len(ids), "total": collection.count()}


def get_collection_stats() -> dict:
    collection = get_collection()
    return {
        "vector_db": "ChromaDB",
        "collection": CHROMA_COLLECTION,
        "documents": collection.count(),
        "path": str(VECTOR_DB_DIR),
    }


def search_knowledge_base(query: str, limit: int = 3) -> list[dict]:
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=max(1, min(limit, 10)))

    output = []
    for idx, document in enumerate(results.get("documents", [[]])[0]):
        metadata = results.get("metadatas", [[]])[0][idx]
        distance = results.get("distances", [[]])[0][idx] if results.get("distances") else None
        output.append(
            {
                "title": metadata.get("title"),
                "category": metadata.get("category"),
                "source": metadata.get("source"),
                "content": document,
                "distance": distance,
                "score": None if distance is None else round(1 / (1 + distance), 4),
            }
        )
    return output
