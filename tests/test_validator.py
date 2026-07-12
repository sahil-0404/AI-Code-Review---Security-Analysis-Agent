from backend.validator import validate_code


def test_java_missing_closing_brace_reports_actionable_error():
    code = """public class SyntaxError {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
"""

    result = validate_code("java", code)

    assert result["valid"] is False
    assert result["language"] == "java"
    assert "Missing 1 closing brace" in result["message"]
    assert result["line"] == 4
    assert result["column"] == 6
    assert "Add a closing brace" in result["suggestion"]
    assert result["severity"] == "error"


def test_java_valid_code_still_passes():
    code = """public class SyntaxOk {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""

    result = validate_code("java", code)

    assert result["valid"] is True
    assert result["message"] == "Java syntax is valid."
