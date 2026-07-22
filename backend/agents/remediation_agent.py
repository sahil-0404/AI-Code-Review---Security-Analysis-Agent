import json

import requests


class RemediationAgent:
    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.model = "llama3.2"

    def generate_fix(self, code: str, findings: list[dict]) -> list[dict]:
        if not findings:
            return []

        prompt = f"""
You are an expert secure code reviewer. Respond with only valid JSON.
Return a JSON array. Every item must contain: issue, explanation, root_cause,
recommendation, step_by_step_fix (an array), fixed_code, best_practice, and
additional_improvements. Explain only static source findings; never claim the
program compiled or executed.

Findings:
{json.dumps(findings, indent=2)}

Source:
{code}
"""
        try:
            response = requests.post(
                self.url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=120,
            )
            raw_result = response.json()["response"].replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw_result)
            if not isinstance(parsed, list):
                raise ValueError("The remediation model did not return an array.")
            return [self._normalize(item, code) for item in parsed if isinstance(item, dict)]
        except Exception as error:
            return [self._fallback(finding, code, str(error)) for finding in findings[:3]]

    @staticmethod
    def _normalize(item: dict, code: str) -> dict:
        recommendation = item.get("recommendation", "Review and correct the reported source finding.")
        return {
            "issue": item.get("issue", "Static Analysis Finding"),
            "explanation": item.get("explanation", "The source contains a review finding."),
            "root_cause": item.get("root_cause", "The implementation needs a safer or clearer pattern."),
            "recommendation": recommendation,
            "step_by_step_fix": item.get("step_by_step_fix", [recommendation, "Validate the updated source."]),
            "fixed_code": item.get("fixed_code", code),
            "best_practice": item.get("best_practice", "Follow language conventions and secure coding guidance."),
            "additional_improvements": item.get("additional_improvements", "Add automated tests for the corrected behavior."),
        }

    @classmethod
    def _fallback(cls, finding: dict, code: str, error: str) -> dict:
        recommendation = finding.get("message", "Review and correct the reported source finding.")
        return cls._normalize({
            "issue": finding.get("type", "Static Analysis Finding"),
            "explanation": f"Static analysis identified this finding. The remediation service was unavailable: {error}",
            "root_cause": "The source matches a risky, non-standard, or invalid implementation pattern.",
            "recommendation": recommendation,
            "step_by_step_fix": ["Locate the reported line.", recommendation, "Run validation and analysis again."],
            "fixed_code": code,
            "best_practice": "Use secure APIs, validate untrusted input, and keep compiler diagnostics at zero.",
            "additional_improvements": "Add a regression test to prevent the issue from returning.",
        }, code)
