from .code_analysis_agent import CodeAnalysisAgent
from .remediation_agent import RemediationAgent
from .security_agent import SecurityAgent


class AgentOrchestrator:
    def __init__(self):
        self.code_agent = CodeAnalysisAgent()
        self.security_agent = SecurityAgent()
        self.remediation_agent = RemediationAgent()

    def analyze(self, code: str, language: str, validation: dict | None = None) -> dict:
        """Run source analysis whether or not the compiler accepted the program."""
        language = language.lower()
        validation = validation or {"valid": True}
        static_only = not validation.get("valid", True)

        if language == "python":
            code_quality = self.code_agent.analyze_python(code)
            security = self.security_agent.analyze_python(code)
        elif language == "java":
            code_quality = self.code_agent.analyze_java(code)
            security = self.security_agent.analyze_java(code)
        else:
            code_quality, security = [], []

        compiler_finding = None
        if static_only:
            compiler_finding = {
                "type": "Compiler or Syntax Error",
                "severity": "High",
                "line": validation.get("line"),
                "message": validation.get("message", "Source validation failed."),
                "static_analysis": True,
            }
            code_quality.insert(0, compiler_finding)

        findings = code_quality + security
        remediation = self.remediation_agent.generate_fix(code, findings)
        if static_only:
            remediation.insert(0, self._compiler_remediation(code, validation))

        high = sum(item.get("severity") == "High" for item in findings)
        medium = sum(item.get("severity") == "Medium" for item in findings)
        low = sum(item.get("severity") == "Low" for item in findings)
        mode = "static_source_analysis" if static_only else "validated_source_analysis"

        return {
            "code_quality": code_quality,
            "security": security,
            "remediation": remediation,
            "summary": {
                "total_findings": len(findings),
                "high": high,
                "medium": medium,
                "low": low,
                "validation_failed": static_only,
                "analysis_mode": mode,
                "compiler_errors": 0 if validation.get("valid", True) else 1,
                "code_review_findings": len(code_quality),
                "security_findings": len(security),
                "ai_recommendations": len(remediation),
            },
            "metrics": {
                "analysis_mode": mode,
                "source_executed": False,
                "source_compiled": bool(validation.get("valid", True)),
                "code_review_findings": len(code_quality),
                "security_findings": len(security),
                "ai_recommendations": len(remediation),
            },
            "timeline": [
                {"stage": "Validation", "status": "completed", "detail": validation.get("message")},
                {"stage": "Code Review", "status": "completed", "detail": "Static source analysis completed."},
                {"stage": "Security Analysis", "status": "completed", "detail": "Static security pattern analysis completed."},
                {"stage": "AI Remediation", "status": "completed", "detail": "Recommendations generated without executing source."},
            ],
        }

    @staticmethod
    def _compiler_remediation(code: str, validation: dict) -> dict:
        message = validation.get("message", "Source validation failed.")
        suggestion = validation.get("suggestion") or "Correct the reported syntax or compiler error and validate again."
        line = validation.get("line")
        location = f" at line {line}" if line else ""
        return {
            "issue": "Compiler or Syntax Error",
            "explanation": f"Validation reported '{message}'{location}. Static analysis continued, but the program was not compiled or executed.",
            "root_cause": "The source contains a syntax or compiler error that prevents successful validation.",
            "recommendation": suggestion,
            "step_by_step_fix": [
                f"Review the compiler diagnostic{location}.",
                suggestion,
                "Validate the corrected source before relying on runtime behavior.",
            ],
            "fixed_code": code,
            "best_practice": "Treat compiler diagnostics as release blockers and keep validation in the development workflow.",
            "additional_improvements": "After fixing the syntax, rerun the review to confirm code-quality and security findings.",
            "static_analysis": True,
        }
