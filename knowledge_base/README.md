# Secure Coding Knowledge Base

Milestone 1 requires a secure coding knowledge base backed by a vector database.

This project seeds ChromaDB with concise reference chunks for:

- OWASP Top 10 concepts
- Python secure coding practices
- Java secure coding practices
- Code smell patterns
- RAG architecture basics

For final submission, you can add official PDFs or text files in this folder and extend `rag/ingest.py` later to load them with `pypdf` or LangChain document loaders.

The current vector DB implementation uses a local hash-based embedding function so the Milestone 1 demo can run without downloading an external embedding model.
