# Agent Responsibilities

Milestone 1 requires the agent responsibilities and orchestration flow to be designed. The complete agent implementation belongs to later milestones.

## Code Analysis Agent

Responsibilities:

- Detect code smells.
- Identify long functions and duplicate logic.
- Check naming and formatting issues.
- Flag maintainability problems.

Expected output:

```json
{
  "severity": "medium",
  "issue": "Function is too long",
  "recommendation": "Split the function into smaller reusable functions."
}
```

## Security Analysis Agent

Responsibilities:

- Detect hardcoded credentials.
- Detect SQL injection patterns.
- Detect unsafe functions such as `eval`.
- Identify weak validation and insecure authentication patterns.
- Use the RAG knowledge base for secure coding references.

Expected output:

```json
{
  "severity": "high",
  "issue": "Hardcoded password detected",
  "recommendation": "Use environment variables or a secrets manager."
}
```

## Remediation Agent

Responsibilities:

- Suggest corrected code.
- Explain why the fix is safer.
- Keep the fix aligned with secure coding guidelines.

## PR Summary Agent

Responsibilities:

- Summarize total issues.
- Group issues by severity.
- Provide an overall quality score.
- Generate a final review summary suitable for a pull request.

## Orchestration Flow

```text
Code Submission
  -> Syntax Validation
  -> Code Analysis Agent
  -> Security Analysis Agent
  -> Remediation Agent
  -> PR Summary Agent
  -> Developer Dashboard
```
