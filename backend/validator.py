import ast

import javalang


def _last_non_empty_line(code: str) -> tuple[int, str]:
    lines = code.splitlines()
    for index in range(len(lines) - 1, -1, -1):
        if lines[index].strip():
            return index + 1, lines[index]
    return 1, ""


def _java_structure_diagnostic(code: str) -> dict | None:
    open_braces = code.count("{")
    close_braces = code.count("}")

    if open_braces > close_braces:
        line, text = _last_non_empty_line(code)
        missing_count = open_braces - close_braces
        return {
            "message": f"Missing {missing_count} closing brace {'}'!r}.",
            "line": line,
            "column": len(text) + 1,
            "suggestion": "Add a closing brace at the end of the file to close the open Java block or class.",
            "severity": "error",
        }

    if close_braces > open_braces:
        line, text = _last_non_empty_line(code)
        return {
            "message": "There is an extra closing brace '}'.",
            "line": line,
            "column": max(1, text.rfind("}") + 1),
            "suggestion": "Remove the extra closing brace or add the missing opening brace for the block.",
            "severity": "error",
        }

    return None


def validate_code(language: str, code: str) -> dict:
    normalized_language = language.strip().lower()

    if normalized_language == "python":
        return validate_python(code)
    if normalized_language == "java":
        return validate_java(code)

    return {
        "valid": False,
        "language": language,
        "message": "Unsupported language. Choose python or java.",
    }


def validate_python(code: str) -> dict:
    try:
        ast.parse(code)
        return {
            "valid": True,
            "language": "python",
            "message": "Python syntax is valid.",
            "line": None,
            "column": None,
        }
    except SyntaxError as exc:
        return {
            "valid": False,
            "language": "python",
            "message": exc.msg,
            "line": exc.lineno,
            "column": exc.offset,
        }


def validate_java(code: str) -> dict:
    try:
        javalang.parse.parse(code)
        return {
            "valid": True,
            "language": "java",
            "message": "Java syntax is valid.",
            "line": None,
            "column": None,
        }
    except javalang.parser.JavaSyntaxError as exc:
        position = getattr(exc, "at", None)
        diagnostic = _java_structure_diagnostic(code)
        if diagnostic:
            return {
                "valid": False,
                "language": "java",
                **diagnostic,
            }

        return {
            "valid": False,
            "language": "java",
            "message": getattr(exc, "description", None) or "Java syntax error.",
            "line": getattr(position, "line", None),
            "column": getattr(position, "column", None),
            "suggestion": "Review the Java syntax near the reported location for a missing type, semicolon, brace, or parenthesis.",
            "severity": "error",
        }
    except Exception as exc:
        return {
            "valid": False,
            "language": "java",
            "message": str(exc),
            "line": None,
            "column": None,
        }
