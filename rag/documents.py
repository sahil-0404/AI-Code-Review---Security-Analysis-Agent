SEED_DOCUMENTS = [
    {
        "title": "OWASP Top 10 - Injection",
        "category": "owasp",
        "text": (
            "Injection happens when untrusted data is sent to an interpreter as part of a command "
            "or query. Secure code should use parameterized queries, validate inputs, and avoid "
            "building commands by string concatenation."
        ),
    },
    {
        "title": "OWASP Top 10 - Cryptographic Failures",
        "category": "owasp",
        "text": (
            "Sensitive data must be protected in transit and at rest. Applications should use "
            "strong encryption, avoid hardcoded secrets, and never store plain text passwords."
        ),
    },
    {
        "title": "OWASP Top 10 - Broken Access Control",
        "category": "owasp",
        "text": (
            "Access control checks must be enforced on the server side. Users should only access "
            "resources and actions allowed by their roles and permissions."
        ),
    },
    {
        "title": "Python Secure Coding - Dangerous Functions",
        "category": "python",
        "text": (
            "Avoid eval, exec, and unsafe deserialization on untrusted input. Prefer safer parsers "
            "and explicit allowlists for accepted values."
        ),
    },
    {
        "title": "Python Secure Coding - Secrets",
        "category": "python",
        "text": (
            "Passwords, API keys, tokens, and database URLs should be loaded from environment "
            "variables or secret managers instead of being written directly in source code."
        ),
    },
    {
        "title": "Java Secure Coding - SQL Queries",
        "category": "java",
        "text": (
            "Java applications should use PreparedStatement for database queries. Concatenating "
            "user input into SQL strings can create SQL injection vulnerabilities."
        ),
    },
    {
        "title": "Java Secure Coding - Input Validation",
        "category": "java",
        "text": (
            "Validate input length, type, range, and format before using it in security-sensitive "
            "operations. Use allowlists where possible."
        ),
    },
    {
        "title": "Code Smells - Large Methods",
        "category": "code_smell",
        "text": (
            "Large methods are difficult to test and review. Split long methods into smaller units "
            "with clear responsibilities."
        ),
    },
    {
        "title": "RAG Architecture",
        "category": "rag",
        "text": (
            "Retrieval-Augmented Generation stores trusted documents in a vector database. A query "
            "is embedded, relevant chunks are retrieved, and the language model uses that context "
            "to produce grounded answers."
        ),
    },
]
