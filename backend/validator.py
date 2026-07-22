"""Language validation with compiler-quality diagnostics."""

import ast
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


JAVAC_FALLBACK = Path(r"C:\Program Files\Java\jdk-26.0.1\bin\javac.exe")
JAVAC_ERROR_PATTERN = re.compile(
    r"^.*?\.java:(?P<line>\d+):(?:\s*(?P<column>\d+):)?\s*error:\s*(?P<message>.+)$"
)


def _result(
    *,
    valid: bool,
    language: str,
    message: str,
    line: int | None = None,
    column: int | None = None,
    suggestion: str | None = None,
    details: list[str] | None = None,
) -> dict[str, Any]:
    """Build the stable response returned by every validator path."""
    return {
        "valid": valid,
        "language": language,
        "message": message,
        "line": line,
        "column": column,
        "suggestion": suggestion,
        "details": details or [],
    }


def validate_code(language: str, code: str) -> dict[str, Any]:
    try:
        normalized_language = (language or "").strip().lower()
        if normalized_language == "python":
            return validate_python(code)
        if normalized_language == "java":
            return validate_java(code)
        return _result(
            valid=False,
            language=language or "",
            message="Unsupported language. Choose python or java.",
            suggestion="Select Python or Java before validating the source code.",
        )
    except Exception as exc:  # Validation must never make the API fail.
        return _result(
            valid=False,
            language=(language or "").strip().lower(),
            message="Validation could not be completed.",
            suggestion="Review the source and try validation again.",
            details=[str(exc)],
        )


def validate_python(code: str) -> dict[str, Any]:
    try:
        ast.parse(code)
        return _result(
            valid=True,
            language="python",
            message="Python syntax is valid.",
        )
    except SyntaxError as exc:
        return _result(
            valid=False,
            language="python",
            message=exc.msg,
            line=exc.lineno,
            column=exc.offset,
            suggestion="Correct the Python syntax at the reported location.",
            details=[line for line in (exc.text or "").splitlines() if line],
        )
    except Exception as exc:
        return _result(
            valid=False,
            language="python",
            message="Python validation could not be completed.",
            suggestion="Review the source and try validation again.",
            details=[str(exc)],
        )


def _javac_path() -> str | None:
    discovered = shutil.which("javac")
    if discovered:
        return discovered
    if JAVAC_FALLBACK.is_file():
        return str(JAVAC_FALLBACK)
    return None


def _java_filename(code: str) -> str:
    """Use the public class name when Java requires the source file to match it."""
    public_class = re.search(r"\bpublic\s+(?:class|interface|enum|record)\s+([A-Za-z_$][\w$]*)", code)
    if public_class:
        return f"{public_class.group(1)}.java"
    return "Hello.java"


def _suggestion_for_java_error(message: str) -> str:
    normalized = message.lower()
    if "package system does not exist" in normalized:
        return "Java is case-sensitive.\nUse System.out.println(...) instead of system.out.println(...)."
    if "';' expected" in normalized:
        return "Missing semicolon. Add ';' at the end of the statement."
    if "cannot find symbol" in normalized:
        return "Check the spelling and make sure the symbol is declared or imported."
    if "reached end of file while parsing" in normalized:
        return "Missing closing brace. Add the closing '}' for the open block or class."
    if "class, interface, enum, or record expected" in normalized or "class, interface, enum expected" in normalized:
        return "Unexpected brace or misplaced code. Move the code inside a class or remove the extra brace."
    return "Review the compiler error at the reported line and correct the Java source."


def _parse_java_error(output: str) -> tuple[int | None, int | None, str]:
    for diagnostic in output.splitlines():
        match = JAVAC_ERROR_PATTERN.match(diagnostic.strip())
        if match:
            return (
                int(match.group("line")),
                int(match.group("column")) if match.group("column") else None,
                match.group("message").strip(),
            )

    for diagnostic in output.splitlines():
        if "error:" in diagnostic:
            return None, None, diagnostic.split("error:", 1)[1].strip()
    return None, None, "Java compilation failed."


def validate_java(code: str) -> dict[str, Any]:
    """Compile Java source in isolation and translate javac output to JSON."""
    try:
        javac = _javac_path()
        if not javac:
            return _result(
                valid=False,
                language="java",
                message="Java compiler (javac) not found.",
                suggestion="Install a JDK or add javac to the system PATH.",
            )

        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / _java_filename(code)
            source_file.write_text(code, encoding="utf-8")
            completed = subprocess.run(
                [javac, "-d", directory, source_file.name],
                cwd=directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
                check=False,
            )

        compiler_output = "\n".join(
            part.rstrip("\n") for part in (completed.stdout, completed.stderr) if part
        )
        details = compiler_output.splitlines()
        if completed.returncode == 0:
            return _result(
                valid=True,
                language="java",
                message="Java compilation successful.",
                details=details,
            )

        line, column, message = _parse_java_error(compiler_output)
        return _result(
            valid=False,
            language="java",
            message=message,
            line=line,
            column=column,
            suggestion=_suggestion_for_java_error(message),
            details=details,
        )
    except subprocess.TimeoutExpired:
        return _result(
            valid=False,
            language="java",
            message="Java compilation timed out.",
            suggestion="Simplify the source and try validation again.",
        )
    except Exception as exc:
        return _result(
            valid=False,
            language="java",
            message="Java validation could not be completed.",
            suggestion="Verify that a JDK is installed and try validation again.",
            details=[str(exc)],
        )
