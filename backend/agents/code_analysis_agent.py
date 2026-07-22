import ast
import re


class CodeAnalysisAgent:

    # ---------------- PYTHON ---------------- #

    def analyze_python(self, code: str):

        findings = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return self._source_style_findings(code, "python")

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):

                body_length = len(node.body)

                if body_length > 25:
                    findings.append({
                        "type": "Long Function",
                        "severity": "Medium",
                        "line": node.lineno,
                        "message": f"Function '{node.name}' is too long ({body_length} statements)."
                    })

                if len(node.args.args) > 5:
                    findings.append({
                        "type": "Too Many Parameters",
                        "severity": "Low",
                        "line": node.lineno,
                        "message": f"Function '{node.name}' has {len(node.args.args)} parameters."
                    })

            if isinstance(node, (ast.If, ast.For, ast.While)):

                nesting = self._calculate_depth(node)

                if nesting >= 4:

                    findings.append({
                        "type": "Deep Nesting",
                        "severity": "Medium",
                        "line": node.lineno,
                        "message": "Deeply nested code."
                    })

        for lineno, line in enumerate(code.splitlines(), start=1):

            if len(line) > 120:

                findings.append({
                    "type": "Long Line",
                    "severity": "Low",
                    "line": lineno,
                    "message": "Line exceeds 120 characters."
                })

            if "TODO" in line or "FIXME" in line:

                findings.append({
                    "type": "Pending Work",
                    "severity": "Low",
                    "line": lineno,
                    "message": "TODO/FIXME comment found."
                })

        findings.extend(self._source_style_findings(code, "python"))
        return findings

    def _calculate_depth(self, node):

        depth = 1

        for child in ast.iter_child_nodes(node):

            if isinstance(child, (ast.If, ast.For, ast.While)):
                depth = max(depth, 1 + self._calculate_depth(child))

        return depth

    # ---------------- JAVA ---------------- #

    def analyze_java(self, code: str):

        findings = []

        lines = code.splitlines()

        # Long lines + TODO

        for lineno, line in enumerate(lines, start=1):

            if len(line) > 120:

                findings.append({
                    "type": "Long Line",
                    "severity": "Low",
                    "line": lineno,
                    "message": "Line exceeds 120 characters."
                })

            if "TODO" in line or "FIXME" in line:

                findings.append({
                    "type": "Pending Work",
                    "severity": "Low",
                    "line": lineno,
                    "message": "TODO/FIXME comment found."
                })

        # Long Method

        in_method = False
        start = 0
        braces = 0

        for lineno, line in enumerate(lines, start=1):

            s = line.strip()

            if (
                ("public" in s or "private" in s or "protected" in s)
                and "(" in s
                and ")" in s
                and "class" not in s
            ):

                in_method = True
                start = lineno

                braces = s.count("{") - s.count("}")

                params = s.split("(")[1].split(")")[0]

                if params.strip():

                    count = len(params.split(","))

                    if count > 5:

                        findings.append({
                            "type": "Too Many Parameters",
                            "severity": "Low",
                            "line": lineno,
                            "message": f"Method has {count} parameters."
                        })

                continue

            if in_method:

                braces += s.count("{")
                braces -= s.count("}")

                if braces == 0:

                    length = lineno - start

                    if length > 25:

                        findings.append({
                            "type": "Long Method",
                            "severity": "Medium",
                            "line": start,
                            "message": f"Method contains {length} lines."
                        })

                    in_method = False

        # Deep nesting
        deep_nesting_found = False

        for lineno, line in enumerate(lines, start=1):
            indent = len(line) - len(line.lstrip())

            if indent >= 16 and not deep_nesting_found:
                findings.append({
                    "type": "Deep Nesting",
                    "severity": "Medium",
                    "line": lineno,
                    "message": "Deep nesting detected."
                })

                deep_nesting_found = True

        findings.extend(self._source_style_findings(code, "java"))
        return findings

    @staticmethod
    def _source_style_findings(code: str, language: str) -> list[dict]:
        """Text-level checks that remain useful when a parser cannot build an AST."""
        findings = []
        lines = code.splitlines()
        comment_markers = ("#",) if language == "python" else ("//", "/*", "*")
        if len(lines) >= 8 and not any(line.strip().startswith(comment_markers) for line in lines):
            findings.append({
                "type": "Missing Comments",
                "severity": "Low",
                "line": 1,
                "message": "Add concise comments for non-obvious logic and public interfaces.",
            })

        for lineno, line in enumerate(lines, start=1):
            if line.rstrip() != line or "\t" in line:
                findings.append({
                    "type": "Formatting Issue",
                    "severity": "Low",
                    "line": lineno,
                    "message": "Use consistent spaces and remove trailing whitespace.",
                })
                break

            if language == "python":
                match = re.match(r"\s*def\s+([A-Za-z_][A-Za-z0-9_]*)", line)
                if match and not re.match(r"^[a-z_][a-z0-9_]*$", match.group(1)):
                    findings.append({
                        "type": "Python Naming Convention",
                        "severity": "Low",
                        "line": lineno,
                        "message": f"Function '{match.group(1)}' should use snake_case.",
                    })
            else:
                match = re.match(r"\s*(?:public|private|protected)?\s*(?:static\s+)?[\w<>\[\]]+\s+([A-Za-z_$][\w$]*)\s*\(", line)
                if match and "_" in match.group(1):
                    findings.append({
                        "type": "Java Naming Convention",
                        "severity": "Low",
                        "line": lineno,
                        "message": f"Method '{match.group(1)}' should use lowerCamelCase.",
                    })

        return findings
        
