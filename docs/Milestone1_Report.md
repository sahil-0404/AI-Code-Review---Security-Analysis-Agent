# Milestone 1 Report

## Project Title

AI Code Review and Security Analysis Agent

## Milestone 1 Objective

The objective of Milestone 1 is to prepare the foundation for an AI-based code review and security analysis system. This milestone focuses on research, architecture design, code submission, syntax validation, and a secure coding knowledge base using a vector database.

## Scope Completed

- Studied OWASP Top 10 vulnerability categories.
- Studied secure coding practices for Python and Java.
- Studied common code smell patterns.
- Designed the system architecture for the complete project.
- Designed agent responsibilities for future milestones.
- Built a code submission module for pasted code and uploaded files.
- Added syntax validation for Python and Java.
- Created a ChromaDB-backed secure coding knowledge base.
- Added a basic frontend to interact with the backend.

## Milestone 1 Implementation

### Code Submission Module

The code submission module supports two input modes:

- Paste code directly into the frontend.
- Upload `.py` or `.java` files.

The backend validates file extensions and reads uploaded source files as UTF-8 text.

### Syntax Validation

Python syntax validation uses the built-in `ast` module.

Java syntax validation uses the `javalang` parser.

The API returns a structured response with:

- Validation status
- Language
- Error message
- Line number
- Column number

### Secure Coding Knowledge Base

The knowledge base is stored in ChromaDB, a vector database suitable for local RAG development. This Milestone 1 version uses a local hash-based embedding function so the demo can run without downloading external AI models.

The seeded documents include:

- OWASP injection guidance
- Cryptographic failure guidance
- Broken access control guidance
- Python secure coding practices
- Java secure coding practices
- Code smell guidance
- RAG architecture notes

## System Architecture

```text
Developer
   |
   v
Frontend Code Submission UI
   |
   v
FastAPI Backend
   |
   +--> File Upload / Paste Code Handler
   |
   +--> Syntax Validator
   |       +--> Python AST Parser
   |       +--> Java javalang Parser
   |
   +--> Secure Coding Knowledge Base Search
           |
           v
       ChromaDB Vector Database
           |
           v
       Secure Coding / OWASP / RAG Chunks
```

## Future Agent Design

Milestone 1 requires the agents to be designed, not fully implemented. The planned agents are:

### Code Analysis Agent

Responsible for identifying code smells, maintainability issues, naming problems, and complexity risks.

### Security Analysis Agent

Responsible for detecting security vulnerabilities such as injection, hardcoded secrets, insecure authentication, weak validation, and unsafe functions.

### Remediation Agent

Responsible for suggesting secure fixes and improved code snippets.

### PR Summary Agent

Responsible for generating a pull request style summary with severity counts, quality score, and recommended next steps.

## Data Flow

```text
Start
  |
  v
User submits code
  |
  v
Backend receives pasted code or uploaded file
  |
  v
Validate language and file extension
  |
  v
Run syntax parser
  |
  +--> Invalid syntax: return error details
  |
  +--> Valid syntax: return success response
  |
  v
Knowledge base can be searched for secure coding references
  |
  v
End
```

## Data Model

```text
CodeSubmission
- id
- source_type
- filename
- language
- code
- validation_status
- validation_message
- created_at

KnowledgeDocument
- id
- title
- category
- source
- content
- embedding

ValidationResult
- valid
- language
- message
- line
- column
```

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | API welcome message |
| GET | `/api/status` | Backend and knowledge base status |
| POST | `/api/validate/paste` | Validate pasted Python or Java code |
| POST | `/api/validate/upload` | Validate uploaded `.py` or `.java` file |
| GET | `/api/knowledge/search` | Search secure coding knowledge base |
| POST | `/api/knowledge/seed` | Seed the ChromaDB knowledge base |

## How To Run

```bash
cd AI-Code-Review-Agent
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
python -m rag.ingest
uvicorn backend.app:app --reload
```

Open:

```text
frontend/index.html
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

## Internship Rules And Conditions Alignment

This milestone is implemented as an original educational project foundation. It avoids copying a complete external project and keeps the work aligned with the stated milestone tasks:

- Only Milestone 1 features are implemented.
- Future agents are documented as planned responsibilities.
- The vector database requirement is included through ChromaDB.
- The project is structured so later milestones can be added without redesigning the foundation.

## Conclusion

Milestone 1 is complete with a working code submission module, syntax validation for Python and Java, a ChromaDB vector database knowledge base, frontend interaction, and complete architecture documentation.
