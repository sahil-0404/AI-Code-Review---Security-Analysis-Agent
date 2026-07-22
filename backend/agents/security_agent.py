import re


class SecurityAgent:

    def analyze_python(self, code: str):
        findings = []
        lines = code.splitlines()

        patterns = [
            {
                "name": "Use of eval()",
                "regex": r"\beval\s*\(",
                "severity": "High",
                "message": "Avoid using eval() as it can execute arbitrary code."
            },
            {
                "name": "Use of exec()",
                "regex": r"\bexec\s*\(",
                "severity": "High",
                "message": "Avoid using exec() with untrusted input."
            },
            {
                "name": "Command Injection",
                "regex": r"os\.system\s*\(",
                "severity": "High",
                "message": "os.system() may lead to command injection."
            },
            {
                "name": "Subprocess Shell",
                "regex": r"subprocess\..*shell\s*=\s*True",
                "severity": "High",
                "message": "shell=True can introduce command injection."
            },
            {
                "name": "Hardcoded Password",
                "regex": r"(password|passwd|pwd)\s*=\s*['\"].+['\"]",
                "severity": "High",
                "message": "Hardcoded password detected."
            },
            {
                "name": "Hardcoded API Key",
                "regex": r"(api_key|apikey|secret|token)\s*=\s*['\"].+['\"]",
                "severity": "High",
                "message": "Hardcoded secret detected."
            },
            {
                "name": "Unsafe Deserialization",
                "regex": r"\bpickle\.loads?\s*\(|\byaml\.load\s*\(",
                "severity": "High",
                "message": "Unsafe deserialization can execute attacker-controlled payloads."
            },
            {
                "name": "Weak Input Validation",
                "regex": r"request\.(args|form|json).*\b(eval|exec)\s*\(",
                "severity": "High",
                "message": "Untrusted request data is passed to a dangerous API."
            }
        ]

        for lineno, line in enumerate(lines, start=1):
            for rule in patterns:
                if re.search(rule["regex"], line):
                    findings.append({
                        "type": rule["name"],
                        "severity": rule["severity"],
                        "line": lineno,
                        "message": rule["message"]
                    })

            # Basic SQL Injection detection
            if (
                ("SELECT" in line.upper() or "INSERT" in line.upper() or "UPDATE" in line.upper())
                and ("+" in line or "%" in line or ".format(" in line or "f\"" in line or "f'" in line)
            ):
                findings.append({
                    "type": "Possible SQL Injection",
                    "severity": "High",
                    "line": lineno,
                    "message": "SQL query appears to be dynamically constructed."
                })

        return findings

    def analyze_java(self, code: str):
        findings = []
        lines = code.splitlines()

        patterns = [
            {
                "name": "Runtime.exec",
                "regex": r"Runtime\.getRuntime\(\)\.exec",
                "severity": "High",
                "message": "Runtime.exec() can be dangerous."
            },
            {
                "name": "Hardcoded Password",
                "regex": r"(password|passwd|pwd)\s*=\s*\".+\"",
                "severity": "High",
                "message": "Hardcoded password detected."
            },
            {
                "name": "Hardcoded Secret",
                "regex": r"(secret|token|apikey|apiKey)\s*=\s*\".+\"",
                "severity": "High",
                "message": "Hardcoded secret detected."
            },
            {
                "name": "Unsafe SQL Execution",
                "regex": r"\bStatement\s*\.\s*execute(?:Query|Update)?\s*\(",
                "severity": "High",
                "message": "Use PreparedStatement for database queries built from external input."
            },
            {
                "name": "Weak Cryptography",
                "regex": r"MessageDigest\.getInstance\s*\(\s*\"(?:MD5|SHA-1)\"",
                "severity": "Medium",
                "message": "MD5 and SHA-1 are not suitable for security-sensitive hashing."
            }
        ]

        for lineno, line in enumerate(lines, start=1):
            for rule in patterns:
                if re.search(rule["regex"], line):
                    findings.append({
                        "type": rule["name"],
                        "severity": rule["severity"],
                        "line": lineno,
                        "message": rule["message"]
                    })

            if (
                ("SELECT" in line.upper() or "INSERT" in line.upper())
                and "+"
                in line
            ):
                findings.append({
                    "type": "Possible SQL Injection",
                    "severity": "High",
                    "line": lineno,
                    "message": "SQL query is built using string concatenation."
                })

        return findings
