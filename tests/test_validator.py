import importlib
import sys
import types

from backend.agents.orchestrator import AgentOrchestrator
from backend.models.request_models import PasteCodeRequest
from backend.validator import validate_code


def test_java_compiler_diagnostic_has_actionable_system_fix():
    code = """class hello
{
    public static void main()
    {
        system.out.println(\"Hello\");
    }
}
"""
    result = validate_code("java", code)
    assert result["valid"] is False
    assert result["message"] == "package system does not exist"
    assert result["line"] == 5
    assert "Java is case-sensitive" in result["suggestion"]


def test_java_valid_code_passes_real_compilation():
    result = validate_code("java", """public class SyntaxOk { public static void main(String[] args) {} }""")
    assert result["valid"] is True
    assert result["message"] == "Java compilation successful."


def test_invalid_java_receives_static_analysis_and_remediation(monkeypatch):
    orchestrator = AgentOrchestrator()
    monkeypatch.setattr(orchestrator.remediation_agent, "generate_fix", lambda *_args: [])
    validation = validate_code("java", "class Broken {\n  Runtime.getRuntime().exec(\"whoami\");")

    analysis = orchestrator.analyze("class Broken {\n  Runtime.getRuntime().exec(\"whoami\");", "java", validation)

    assert validation["valid"] is False
    assert analysis["summary"]["analysis_mode"] == "static_source_analysis"
    assert analysis["code_quality"]
    assert analysis["security"]
    assert analysis["remediation"]
    assert analysis["metrics"]["source_compiled"] is False
    assert analysis["timeline"]
    assert "not compiled or executed" in analysis["remediation"][0]["explanation"]


def test_invalid_python_receives_static_analysis_and_remediation(monkeypatch):
    orchestrator = AgentOrchestrator()
    monkeypatch.setattr(orchestrator.remediation_agent, "generate_fix", lambda *_args: [])
    code = "def BadName(:\n    password = 'secret'\n"
    validation = validate_code("python", code)

    analysis = orchestrator.analyze(code, "python", validation)

    assert validation["valid"] is False
    assert analysis["summary"]["analysis_mode"] == "static_source_analysis"
    assert analysis["security"]
    assert analysis["remediation"]


def _routes_without_rag_startup(monkeypatch):
    rag_module = types.ModuleType("rag.vectordb")
    rag_module.get_collection_stats = lambda: {}
    rag_module.search_knowledge_base = lambda **_kwargs: []
    rag_module.seed_knowledge_base = lambda: {}
    monkeypatch.setitem(sys.modules, "rag.vectordb", rag_module)
    sys.modules.pop("backend.routes", None)
    return importlib.import_module("backend.routes")


def test_route_always_returns_analysis_for_invalid_source(monkeypatch):
    routes = _routes_without_rag_startup(monkeypatch)
    expected = {"summary": {}, "code_quality": [], "security": [], "remediation": [], "metrics": {}, "timeline": []}
    called = {}

    def analyze(code, language, validation):
        called.update({"code": code, "language": language, "validation": validation})
        return expected

    monkeypatch.setattr(routes.orchestrator, "analyze", analyze)
    response = routes.validate_pasted_code(PasteCodeRequest(language="python", code="def broken(:\n"))

    assert response["validation"]["valid"] is False
    assert response["analysis"] == expected
    assert called["validation"]["valid"] is False


def test_valid_source_keeps_existing_analysis_workflow(monkeypatch):
    orchestrator = AgentOrchestrator()
    monkeypatch.setattr(orchestrator.remediation_agent, "generate_fix", lambda *_args: [])
    validation = validate_code("python", "def ok():\n    return 1\n")
    analysis = orchestrator.analyze("def ok():\n    return 1\n", "python", validation)

    assert validation["valid"] is True
    assert analysis["summary"]["analysis_mode"] == "validated_source_analysis"
    assert analysis["metrics"]["source_compiled"] is True
