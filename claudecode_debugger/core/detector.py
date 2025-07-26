"""Error detection module for ClaudeCode-Debugger."""

import re
from typing import Dict, List, Optional, Set, Tuple


class ErrorDetector:
    """Detects and classifies error types from text."""

    def __init__(self) -> None:
        """Initialize the error detector with pattern definitions."""
        self.patterns = {
            "typescript": [
                r"TS\d{4}:",
                r"error TS\d+:",
                r"Type .* is not assignable to type",
                r"Cannot find module",
                r"Object is possibly [\'\"]undefined[\'\"]",
                r"Property .* does not exist on type",
                r"Expected \d+ arguments?, but got \d+",
            ],
            "javascript": [
                r"TypeError:.*is not a function",
                r"ReferenceError:.*is not defined",
                r"SyntaxError: Unexpected token",
                r"Cannot read prop(?:erty)? [\'\"]?\w+[\'\"]? of undefined",
                r"Cannot access .* before initialization",
                r"Uncaught Error:",
                r"UnhandledPromiseRejectionWarning:",
            ],
            "python": [
                r"Traceback \(most recent call last\):",
                r'^\s*File "([^"]+)", line (\d+)',
                r"([\w\.]+Error):\s*(.+)",
                r"ImportError: No module named",
                r"IndentationError: unexpected indent",
                r"SyntaxError: invalid syntax",
                r"AttributeError:",
                r"ValueError:",
                r"KeyError:",
            ],
            "memory": [
                r"JavaScript heap out of memory",
                r"FATAL ERROR:.*Allocation failed",
                r"Maximum call stack size exceeded",
                r"MemoryError",
                r"java\.lang\.OutOfMemoryError",
                r"Cannot allocate memory",
                r"memory limit exceeded",
            ],
            "network": [
                r"CORS policy:",
                r"ERR_CONNECTION_REFUSED",
                r"ECONNREFUSED",
                r"fetch failed",
                r"NetworkError when attempting to fetch",
                r"ERR_NETWORK",
                r"timeout of \d+ms exceeded",
                r"ERR_INTERNET_DISCONNECTED",
                r"ETIMEDOUT",
            ],
            "react": [
                r"Invalid hook call",
                r"Objects are not valid as a React child",
                r"Cannot update a component",
                r"Too many re-renders",
                r"React Hook .* is called conditionally",
                r"Cannot read properties of null \(reading \'useContext\'\)",
            ],
            "build": [
                r"Module build failed",
                r"ERROR in \./",
                r"Failed to compile",
                r"Module not found: Error:",
                r"npm ERR!",
                r"error Command failed",
                r"Build failed",
            ],
        }

        # Compile patterns for performance
        self.compiled_patterns = {
            error_type: [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in patterns
            ]
            for error_type, patterns in self.patterns.items()
        }

    def detect(self, error_text: str) -> str:
        """
        Detect error type from text.

        Args:
            error_text: The error message or log to analyze.

        Returns:
            The detected error type (e.g., 'typescript', 'python').
        """
        if not error_text:
            return "general"

        scores = {}

        for error_type, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern.search(error_text):
                    score += 1
            scores[error_type] = score

        # Return the type with highest score
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return "general"

    def extract_key_info(self, error_text: str, error_type: str) -> Dict:
        """
        Extract key information from error text.

        Args:
            error_text: The error message to analyze.
            error_type: The detected error type.

        Returns:
            Dictionary containing extracted information.
        """
        info = {
            "files": list(self._extract_files(error_text)),
            "line_numbers": list(self._extract_line_numbers(error_text)),
            "error_codes": list(self._extract_error_codes(error_text, error_type)),
            "stack_trace": self._extract_stack_trace(error_text),
            "error_messages": list(self._extract_error_messages(error_text)),
        }

        # Remove duplicates while preserving order
        for key in info:
            if isinstance(info[key], list):
                info[key] = list(dict.fromkeys(info[key]))

        return info

    def _extract_files(self, text: str) -> Set[str]:
        """Extract file paths from error text."""
        patterns = [
            r'(?:File |at |from |in )"?([^\s"]+\.(?:ts|js|py|tsx|jsx|vue|java|cpp|c|h|rs))"?',
            r"([\/\w\-\.]+\.(?:ts|js|py|tsx|jsx|vue|java|cpp|c|h|rs))(?:\s|:|$)",
        ]

        files = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            files.update(matches)

        return files

    def _extract_line_numbers(self, text: str) -> Set[int]:
        """Extract line numbers from error text."""
        patterns = [
            r"line (\d+)",
            r":(\d+):(?:\d+)?",
            r"at line (\d+)",
            r"on line (\d+)",
        ]

        line_numbers: set[int] = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            line_numbers.update(int(match) for match in matches if match.isdigit())

        return line_numbers

    def _extract_error_codes(self, text: str, error_type: str) -> Set[str]:
        """Extract error codes based on error type."""
        codes: set[str] = set()

        if error_type == "typescript":
            # TypeScript error codes
            matches = re.findall(r"TS(\d{4})", text)
            codes.update(f"TS{match}" for match in matches)

        elif error_type == "python":
            # Python exception types
            matches = re.findall(r"(\w+Error):", text)
            codes.update(matches)

        elif error_type == "javascript":
            # JavaScript error types
            error_types = ["TypeError", "ReferenceError", "SyntaxError", "RangeError"]
            for error in error_types:
                if error in text:
                    codes.add(error)

        return codes

    def _extract_stack_trace(self, text: str) -> Optional[str]:
        """Extract stack trace if present."""
        # Look for typical stack trace patterns
        stack_patterns = [
            r"(Traceback \(most recent call last\):.*?)(?=\n\n|\Z)",
            r"(at .*\n(?:\s+at .*\n)*)",
            r"(Error:.*\n(?:\s+at .*\n)+)",
        ]

        for pattern in stack_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()

        return None

    def _extract_error_messages(self, text: str) -> Set[str]:
        """Extract specific error messages."""
        messages: set[str] = set()

        # Common error message patterns
        patterns = [
            r"Error: (.+?)(?:\n|$)",
            r"(?:Type|Reference|Syntax)Error: (.+?)(?:\n|$)",
            r"TS\d{4}: (.+?)(?:\n|$)",
            r"\w+Error: (.+?)(?:\n|$)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            messages.update(match.strip() for match in matches)

        return messages

    def get_severity(self, error_text: str, error_type: str) -> str:
        """
        Assess error severity.

        Args:
            error_text: The error message.
            error_type: The detected error type.

        Returns:
            Severity level: 'critical', 'high', 'medium', or 'low'.
        """
        # Critical indicators
        critical_keywords = [
            "build failed",
            "compilation failed",
            "fatal error",
            "out of memory",
            "segmentation fault",
            "kernel panic",
            "data loss",
            "security vulnerability",
            "authentication failed",
        ]

        # High severity indicators
        high_keywords = [
            "error",
            "exception",
            "failed",
            "cannot",
            "undefined",
            "null reference",
            "type error",
            "syntax error",
        ]

        # Check for keywords
        lower_text = error_text.lower()

        if any(keyword in lower_text for keyword in critical_keywords):
            return "critical"
        elif error_type in ["memory", "build"] or any(
            keyword in lower_text for keyword in high_keywords
        ):
            return "high"
        elif error_type in ["network", "typescript", "javascript"]:
            return "medium"
        else:
            return "low"
