"""Advanced error detection module for ClaudeCode-Debugger."""

import hashlib
import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error categories for classification."""

    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    MEMORY = "memory"
    NETWORK = "network"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    DJANGO = "django"
    FASTAPI = "fastapi"
    DATABASE = "database"
    DOCKER = "docker"
    CICD = "cicd"
    BUILD = "build"
    SECURITY = "security"
    ASYNC = "async"
    GENERAL = "general"


@dataclass
class ErrorPattern:
    """Represents an error pattern with metadata."""

    pattern: str
    category: ErrorCategory
    weight: float = 1.0
    extract_groups: List[str] = field(default_factory=list)
    multiline: bool = False
    context_lines: int = 0

    def __post_init__(self) -> None:
        """Compile pattern for performance."""
        flags = re.IGNORECASE | re.MULTILINE
        if self.multiline:
            flags |= re.DOTALL
        self._compiled = re.compile(self.pattern, flags)

    def search(self, text: str) -> Optional[re.Match]:
        """Search for pattern in text."""
        return self._compiled.search(text)

    def findall(self, text: str) -> List[Tuple]:
        """Find all matches in text."""
        return self._compiled.findall(text)


@dataclass
class ErrorMatch:
    """Represents a matched error with confidence score."""

    category: ErrorCategory
    confidence: float
    matches: List[re.Match]
    extracted_info: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"
    context: Optional[str] = None


class AdvancedErrorDetector:
    """Advanced error detection with ML-ready features and pattern matching."""

    def __init__(self, custom_patterns: Optional[List[ErrorPattern]] = None):
        """Initialize the advanced error detector."""
        self.patterns = self._initialize_patterns()
        if custom_patterns:
            self.patterns.extend(custom_patterns)

        # Cache for performance
        self._cache: Dict[str, List[ErrorMatch]] = {}
        self._cache_size = 1000

        # ML classifier placeholder
        self.ml_classifier = None

    def _initialize_patterns(self) -> List[ErrorPattern]:
        """Initialize comprehensive error patterns."""
        patterns = []

        # TypeScript/JavaScript patterns
        patterns.extend(
            [
                ErrorPattern(
                    r"(?:error )?TS(\d{4}):\s*(.+?)(?:\n|$)",
                    ErrorCategory.TYPESCRIPT,
                    weight=2.0,
                    extract_groups=["error_code", "message"],
                ),
                ErrorPattern(
                    r'Type\s+[\'"`](.+?)[\'"`]\s+is not assignable to type\s+[\'"`](.+?)[\'"`]',
                    ErrorCategory.TYPESCRIPT,
                    weight=1.5,
                    extract_groups=["source_type", "target_type"],
                ),
                ErrorPattern(
                    r'Cannot find module\s+[\'"`](.+?)[\'"`]',
                    ErrorCategory.TYPESCRIPT,
                    weight=1.5,
                    extract_groups=["module_name"],
                ),
                ErrorPattern(
                    r'Property\s+[\'"`](\w+)[\'"`]\s+does not exist on type\s+[\'"`](.+?)[\'"`]',
                    ErrorCategory.TYPESCRIPT,
                    weight=1.5,
                    extract_groups=["property", "type"],
                ),
                ErrorPattern(
                    r"(TypeError|ReferenceError|SyntaxError|RangeError):\s*(.+?)(?:\n|$)",
                    ErrorCategory.JAVASCRIPT,
                    weight=2.0,
                    extract_groups=["error_type", "message"],
                ),
                ErrorPattern(
                    r'Cannot read prop(?:erty)?\s+[\'"`]?(\w+)[\'"`]?\s+of\s+(undefined|null)',
                    ErrorCategory.JAVASCRIPT,
                    weight=1.8,
                    extract_groups=["property", "object_type"],
                ),
                ErrorPattern(
                    r"UnhandledPromiseRejectionWarning:\s*(.+)",
                    ErrorCategory.JAVASCRIPT,
                    weight=1.7,
                    extract_groups=["message"],
                ),
            ]
        )

        # Python patterns
        patterns.extend(
            [
                ErrorPattern(
                    r"Traceback \(most recent call last\):(.*?)(?=\n(?:[A-Z]\w+Error:|$))",
                    ErrorCategory.PYTHON,
                    weight=2.0,
                    multiline=True,
                    context_lines=5,
                    extract_groups=["traceback"],
                ),
                ErrorPattern(
                    r'File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+(\w+)',
                    ErrorCategory.PYTHON,
                    weight=1.5,
                    extract_groups=["file", "line", "function"],
                ),
                ErrorPattern(
                    r"(\w+Error):\s*(.+?)(?:\n|$)",
                    ErrorCategory.PYTHON,
                    weight=1.8,
                    extract_groups=["error_type", "message"],
                ),
                ErrorPattern(
                    r"async def\s+\w+.*?await.*?(?:asyncio\.)?(?:TimeoutError|CancelledError)",
                    ErrorCategory.ASYNC,
                    weight=1.6,
                    multiline=True,
                ),
            ]
        )

        # Memory patterns
        patterns.extend(
            [
                ErrorPattern(
                    r"JavaScript heap out of memory", ErrorCategory.MEMORY, weight=2.5
                ),
                ErrorPattern(
                    r"FATAL ERROR:.*?Allocation failed.*?process out of memory",
                    ErrorCategory.MEMORY,
                    weight=2.5,
                    multiline=True,
                ),
                ErrorPattern(
                    r"Maximum call stack size exceeded",
                    ErrorCategory.MEMORY,
                    weight=2.0,
                ),
                ErrorPattern(
                    r"java\.lang\.OutOfMemoryError:\s*(.+)",
                    ErrorCategory.MEMORY,
                    weight=2.5,
                    extract_groups=["heap_space"],
                ),
            ]
        )

        # Network patterns
        patterns.extend(
            [
                ErrorPattern(
                    r"CORS (?:policy|error):.*?(?:Access-Control-Allow-Origin|blocked)",
                    ErrorCategory.NETWORK,
                    weight=2.0,
                    multiline=True,
                ),
                ErrorPattern(
                    r"(ERR_CONNECTION_REFUSED|ECONNREFUSED|ETIMEDOUT|ENOTFOUND)",
                    ErrorCategory.NETWORK,
                    weight=2.0,
                    extract_groups=["error_code"],
                ),
                ErrorPattern(
                    r"fetch failed.*?(?:reason:\s*(.+))?",
                    ErrorCategory.NETWORK,
                    weight=1.8,
                    extract_groups=["reason"],
                ),
                ErrorPattern(
                    r'WebSocket connection to\s+[\'"`](.+?)[\'"`]\s+failed',
                    ErrorCategory.NETWORK,
                    weight=1.8,
                    extract_groups=["url"],
                ),
            ]
        )

        # Framework-specific patterns
        patterns.extend(
            [
                # React
                ErrorPattern(
                    r"Invalid hook call.*?Hooks can only be called inside",
                    ErrorCategory.REACT,
                    weight=2.0,
                    multiline=True,
                ),
                ErrorPattern(
                    r"Too many re-renders\.\s*React limits",
                    ErrorCategory.REACT,
                    weight=2.0,
                ),
                ErrorPattern(
                    r"Objects are not valid as a React child.*?found:\s*(.+)",
                    ErrorCategory.REACT,
                    weight=1.8,
                    extract_groups=["object_type"],
                ),
                # Vue
                ErrorPattern(
                    r"\[Vue warn\]:\s*(.+?)(?:\n|$)",
                    ErrorCategory.VUE,
                    weight=1.8,
                    extract_groups=["message"],
                ),
                ErrorPattern(
                    r"Unknown custom element:\s*<(.+?)>",
                    ErrorCategory.VUE,
                    weight=1.7,
                    extract_groups=["component"],
                ),
                # Angular
                ErrorPattern(
                    r"ERROR\s+(?:in|Error):\s*(.+?)(?:\n|$)",
                    ErrorCategory.ANGULAR,
                    weight=1.8,
                    extract_groups=["message"],
                ),
                ErrorPattern(
                    r"NG\d{4}:\s*(.+)",
                    ErrorCategory.ANGULAR,
                    weight=2.0,
                    extract_groups=["message"],
                ),
                # Django
                ErrorPattern(
                    r"django\.(?:core|db|utils)\.exceptions\.(\w+):\s*(.+)",
                    ErrorCategory.DJANGO,
                    weight=2.0,
                    extract_groups=["exception_type", "message"],
                ),
                ErrorPattern(
                    r"OperationalError:.*?no such table:\s*(\w+)",
                    ErrorCategory.DJANGO,
                    weight=1.8,
                    extract_groups=["table_name"],
                ),
                # FastAPI
                ErrorPattern(
                    r"fastapi\.exceptions\.(\w+):\s*(.+)",
                    ErrorCategory.FASTAPI,
                    weight=2.0,
                    extract_groups=["exception_type", "message"],
                ),
                ErrorPattern(
                    r"pydantic\.error_wrappers\.ValidationError.*?(\d+)\s+validation errors?",
                    ErrorCategory.FASTAPI,
                    weight=1.8,
                    extract_groups=["error_count"],
                ),
            ]
        )

        # Database patterns
        patterns.extend(
            [
                ErrorPattern(
                    r"(?:psycopg2|mysql|sqlite3)\.(?:\w+\.)?(\w+Error):\s*(.+)",
                    ErrorCategory.DATABASE,
                    weight=2.0,
                    extract_groups=["error_type", "message"],
                ),
                ErrorPattern(
                    r"SQLSTATE\[(\w+)\].*?:\s*(.+)",
                    ErrorCategory.DATABASE,
                    weight=2.0,
                    extract_groups=["sql_state", "message"],
                ),
                ErrorPattern(
                    r"MongoError:\s*(.+)",
                    ErrorCategory.DATABASE,
                    weight=1.8,
                    extract_groups=["message"],
                ),
            ]
        )

        # Docker patterns
        patterns.extend(
            [
                ErrorPattern(
                    r"docker:\s*Error response from daemon:\s*(.+)",
                    ErrorCategory.DOCKER,
                    weight=2.0,
                    extract_groups=["message"],
                ),
                ErrorPattern(
                    r'ERROR:\s*Service\s+[\'"`](\w+)[\'"`]\s+failed to build:\s*(.+)',
                    ErrorCategory.DOCKER,
                    weight=2.0,
                    extract_groups=["service", "reason"],
                ),
                ErrorPattern(
                    r"container_linux\.go:\d+:.*?(?:starting container process|exec).*?:\s*(.+)",
                    ErrorCategory.DOCKER,
                    weight=1.8,
                    extract_groups=["message"],
                ),
            ]
        )

        # CI/CD patterns
        patterns.extend(
            [
                ErrorPattern(
                    r"##\[error\](.+)",
                    ErrorCategory.CICD,
                    weight=2.0,
                    extract_groups=["message"],
                ),
                ErrorPattern(
                    r'The job was canceled because\s+"(.+?)"',
                    ErrorCategory.CICD,
                    weight=1.8,
                    extract_groups=["reason"],
                ),
                ErrorPattern(
                    r"npm ERR!\s+(.+?)(?:\n|$)",
                    ErrorCategory.BUILD,
                    weight=1.8,
                    extract_groups=["message"],
                ),
                ErrorPattern(
                    r"ERROR:\s*Failed to build\s+(.+)",
                    ErrorCategory.BUILD,
                    weight=2.0,
                    extract_groups=["target"],
                ),
            ]
        )

        return patterns

    def detect_multi_label(
        self, error_text: str, confidence_threshold: float = 0.3
    ) -> List[ErrorMatch]:
        """
        Detect multiple error types with confidence scores.

        Args:
            error_text: The error message or log to analyze.
            confidence_threshold: Minimum confidence to include a category.

        Returns:
            List of ErrorMatch objects sorted by confidence.
        """
        if not error_text:
            return []

        # Check cache
        text_hash = hashlib.md5(error_text.encode()).hexdigest()
        cache_key = f"{text_hash}_{confidence_threshold}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Score each category
        category_scores: Dict[ErrorCategory, Dict[str, Any]] = defaultdict(
            lambda: {"score": 0, "matches": [], "info": {}}
        )

        for pattern in self.patterns:
            matches = (
                list(pattern.findall(error_text)) if pattern.extract_groups else []
            )
            if not matches and pattern.search(error_text):
                matches = [pattern.search(error_text)]

            if matches:
                score = pattern.weight * len(matches)
                category_scores[pattern.category]["score"] += score
                category_scores[pattern.category]["matches"].extend(matches)

                # Extract named groups
                if pattern.extract_groups and matches:
                    for i, group_name in enumerate(pattern.extract_groups):
                        if isinstance(matches[0], tuple) and i < len(matches[0]):
                            if (
                                group_name
                                not in category_scores[pattern.category]["info"]
                            ):
                                category_scores[pattern.category]["info"][
                                    group_name
                                ] = []
                            category_scores[pattern.category]["info"][
                                group_name
                            ].extend([m[i] for m in matches if isinstance(m, tuple)])

        # Normalize scores and create ErrorMatch objects
        results = []
        total_score = sum(cat["score"] for cat in category_scores.values())

        if total_score > 0:
            for category, data in category_scores.items():
                confidence = data["score"] / total_score
                if confidence >= confidence_threshold:
                    # Determine severity
                    severity = self._calculate_severity(
                        error_text, category, confidence
                    )

                    error_match = ErrorMatch(
                        category=category,
                        confidence=confidence,
                        matches=data["matches"],
                        extracted_info=data["info"],
                        severity=severity,
                    )
                    results.append(error_match)

        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)

        # ML classifier enhancement (if available)
        if self.ml_classifier:
            results = self._enhance_with_ml(error_text, results)

        # Cache result
        if len(self._cache) < self._cache_size:
            self._cache[cache_key] = results

        return results

    def extract_comprehensive_info(self, error_text: str) -> Dict[str, Any]:
        """
        Extract comprehensive information from error text.

        Args:
            error_text: The error message to analyze.

        Returns:
            Dictionary containing all extracted information.
        """
        # Detect error types first
        error_matches = self.detect_multi_label(error_text)

        info = {
            "error_categories": [
                (m.category.value, m.confidence) for m in error_matches
            ],
            "severity": error_matches[0].severity if error_matches else "unknown",
            "files": list(self._extract_files_advanced(error_text)),
            "line_numbers": list(self._extract_line_numbers_advanced(error_text)),
            "functions": list(self._extract_functions(error_text)),
            "variables": list(self._extract_variables(error_text)),
            "urls": list(self._extract_urls(error_text)),
            "stack_traces": self._extract_stack_traces(error_text),
            "error_codes": list(self._extract_error_codes_advanced(error_text)),
            "timestamps": list(self._extract_timestamps(error_text)),
            "environment": self._extract_environment_info(error_text),
            "suggestions": self._generate_suggestions(error_matches),
        }

        # Merge extracted info from patterns
        for match in error_matches:
            for key, values in match.extracted_info.items():
                if key not in info:
                    info[key] = []
                info[key].extend(values)

        # Remove duplicates while preserving order
        for key in info:
            if isinstance(info[key], list):
                info[key] = list(dict.fromkeys(info[key]))

        return info

    def _extract_files_advanced(self, text: str) -> Set[str]:
        """Extract file paths with advanced patterns."""
        patterns = [
            # Standard file paths
            r'(?:File|at|from|in)\s*["\']?([^\s"\']+\.(?:ts|tsx|js|jsx|py|java|cpp|c|h|rs|go|rb|php|swift|kt|scala|r|m|mm|vue|svelte|astro))["\']?',
            # Absolute paths
            r"([/\\](?:[\w\-\.]+[/\\])*[\w\-\.]+\.(?:ts|tsx|js|jsx|py|java|cpp|c|h|rs|go|rb|php|swift|kt|scala|r|m|mm|vue|svelte|astro))",
            # Relative paths
            r"((?:\.{1,2}[/\\])*(?:[\w\-\.]+[/\\])*[\w\-\.]+\.(?:ts|tsx|js|jsx|py|java|cpp|c|h|rs|go|rb|php|swift|kt|scala|r|m|mm|vue|svelte|astro))",
            # Windows paths
            r"([A-Za-z]:\\(?:[\w\-\.]+\\)*[\w\-\.]+\.(?:ts|tsx|js|jsx|py|java|cpp|c|h|rs|go|rb|php|swift|kt|scala|r|m|mm|vue|svelte|astro))",
            # Stack trace specific
            r"^\s*at\s+.*?\(([^:)]+\.(?:ts|tsx|js|jsx)):(\d+):(\d+)\)",
            # Python traceback
            r'File\s+"([^"]+\.py)"',
        ]

        files = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    files.add(match[0])
                else:
                    files.add(match)

        # Filter out invalid paths
        valid_files = set()
        for file in files:
            if len(file) > 3 and not file.startswith("..."):
                valid_files.add(file)

        return valid_files

    def _extract_line_numbers_advanced(self, text: str) -> Set[int]:
        """Extract line numbers with context."""
        patterns = [
            r"line\s+(\d+)",
            r":(\d+):(?:\d+)?",
            r"at\s+line\s+(\d+)",
            r"on\s+line\s+(\d+)",
            r"\[(\d+),\s*\d+\]",  # [line, column]
            r"L(\d+)",  # GitHub style
        ]

        line_numbers = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    line_num = int(match)
                    if 0 < line_num < 100000:  # Reasonable line number range
                        line_numbers.add(line_num)
                except ValueError:
                    continue

        return line_numbers

    def _extract_functions(self, text: str) -> Set[str]:
        """Extract function names from stack traces."""
        patterns = [
            r"at\s+(\w+(?:\.\w+)*)\s*\(",
            r"in\s+(\w+)\s*\n",
            r'File\s+"[^"]+",\s+line\s+\d+,\s+in\s+(\w+)',
            r"(\w+(?:\.\w+)*)\s*\([^)]*\)\s*at",
            r"function\s+(\w+)",
            r"def\s+(\w+)",
        ]

        functions = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            functions.update(match for match in matches if match and len(match) > 1)

        return functions

    def _extract_variables(self, text: str) -> Set[str]:
        """Extract variable names from error messages."""
        patterns = [
            r"['\"](\w+)['\"] is not defined",
            r"Cannot read (?:property|prop) ['\"](\w+)['\"]",
            r"Cannot access ['\"](\w+)['\"] before initialization",
            r"Property ['\"](\w+)['\"] does not exist",
            r"undefined variable ['\"](\w+)['\"]",
            r"name ['\"](\w+)['\"] is not defined",
        ]

        variables = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            variables.update(
                match for match in matches if match and match.isidentifier()
            )

        return variables

    def _extract_urls(self, text: str) -> Set[str]:
        """Extract URLs from error messages."""
        url_pattern = r'https?://[^\s\'"<>]+'
        urls = set(re.findall(url_pattern, text))

        # Also extract API endpoints
        api_patterns = [
            r"/api/[\w/]+",
            r"/v\d+/[\w/]+",
            r"localhost:\d+[\w/]*",
        ]

        for pattern in api_patterns:
            urls.update(re.findall(pattern, text))

        return urls

    def _extract_stack_traces(self, text: str) -> List[Dict[str, Any]]:
        """Extract multiple stack traces with structure."""
        stack_traces = []

        # Python traceback
        python_pattern = r"Traceback \(most recent call last\):(.*?)(?=\n(?:[A-Z]\w+Error:|Traceback|$))"
        for match in re.finditer(python_pattern, text, re.DOTALL):
            trace_text = match.group(1).strip()
            frames = []

            frame_pattern = r'File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+(\w+)\n\s*(.+)'
            for frame_match in re.finditer(frame_pattern, trace_text):
                frames.append(
                    {
                        "file": frame_match.group(1),
                        "line": int(frame_match.group(2)),
                        "function": frame_match.group(3),
                        "code": frame_match.group(4).strip(),
                    }
                )

            if frames:
                stack_traces.append(
                    {"type": "python", "frames": frames, "raw": trace_text}
                )

        # JavaScript/Node.js stack trace
        js_pattern = r"(?:Error:|TypeError:|ReferenceError:).*?\n((?:\s*at\s+.*\n)+)"
        for match in re.finditer(js_pattern, text, re.MULTILINE):
            trace_text = match.group(1)
            frames = []

            frame_pattern = r"at\s+(?:(\w+(?:\.\w+)*)\s+\()?([^:)]+):(\d+):(\d+)\)?"
            for frame_match in re.finditer(frame_pattern, trace_text):
                frames.append(
                    {
                        "function": frame_match.group(1) or "<anonymous>",
                        "file": frame_match.group(2),
                        "line": int(frame_match.group(3)),
                        "column": int(frame_match.group(4)),
                    }
                )

            if frames:
                stack_traces.append(
                    {"type": "javascript", "frames": frames, "raw": trace_text}
                )

        return stack_traces

    def _extract_error_codes_advanced(self, text: str) -> Set[str]:
        """Extract error codes from various sources."""
        codes = set()

        # TypeScript
        codes.update(re.findall(r"TS(\d{4})", text))

        # HTTP status codes
        codes.update(re.findall(r"(?:status|code):\s*(\d{3})", text, re.IGNORECASE))

        # System error codes
        codes.update(re.findall(r"(?:errno|code):\s*([A-Z_]+)", text))

        # SQL state codes
        codes.update(re.findall(r"SQLSTATE\[(\w+)\]", text))

        # Custom error codes
        codes.update(re.findall(r"(?:ERROR|ERR)[_-](\w+)", text))

        return codes

    def _extract_timestamps(self, text: str) -> Set[str]:
        """Extract timestamps from logs."""
        patterns = [
            r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}",
            r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}",
            r"\[\d{2}:\d{2}:\d{2}\]",
        ]

        timestamps = set()
        for pattern in patterns:
            timestamps.update(re.findall(pattern, text))

        return timestamps

    def _extract_environment_info(self, text: str) -> Dict[str, Any]:
        """Extract environment information."""
        env_info = {}

        # Node.js version
        node_match = re.search(r"node[:\s]+v?([\d\.]+)", text, re.IGNORECASE)
        if node_match:
            env_info["node_version"] = node_match.group(1)

        # Python version
        python_match = re.search(r"python[:\s]+v?([\d\.]+)", text, re.IGNORECASE)
        if python_match:
            env_info["python_version"] = python_match.group(1)

        # OS information
        os_patterns = [
            (r"darwin|macos|mac os", "macos"),
            (r"windows|win32|win64", "windows"),
            (r"linux|ubuntu|debian|centos|fedora", "linux"),
        ]

        for pattern, os_name in os_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                env_info["os"] = os_name
                break

        # Environment variables mentioned
        env_vars = re.findall(
            r'(?:process\.env\.|ENV\[|os\.environ\[)[\'"](\w+)[\'"]', text
        )
        if env_vars:
            env_info["env_variables"] = list(set(env_vars))

        return env_info

    def _calculate_severity(
        self, text: str, category: ErrorCategory, confidence: float
    ) -> str:
        """Calculate error severity with advanced logic."""
        severity_score = confidence

        # Critical indicators
        critical_patterns = [
            (r"fatal|crash|panic|critical", 0.3),
            (r"data loss|corruption|security breach", 0.4),
            (r"out of memory|heap overflow|stack overflow", 0.3),
            (r"authentication failed|unauthorized|forbidden", 0.25),
        ]

        # High severity indicators
        high_patterns = [
            (r"error|exception|failure", 0.2),
            (r"cannot|unable|failed to", 0.15),
            (r"undefined|null reference|type error", 0.15),
            (r"timeout|connection refused|network error", 0.15),
        ]

        # Check patterns
        lower_text = text.lower()

        for pattern, weight in critical_patterns:
            if re.search(pattern, lower_text):
                severity_score += weight

        for pattern, weight in high_patterns:
            if re.search(pattern, lower_text):
                severity_score += weight * 0.7

        # Category-based adjustments
        if category in [ErrorCategory.MEMORY, ErrorCategory.SECURITY]:
            severity_score += 0.2
        elif category in [ErrorCategory.BUILD, ErrorCategory.DOCKER]:
            severity_score += 0.15
        elif category in [ErrorCategory.DATABASE, ErrorCategory.NETWORK]:
            severity_score += 0.1

        # Determine final severity
        if severity_score >= 0.8:
            return "critical"
        elif severity_score >= 0.6:
            return "high"
        elif severity_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _generate_suggestions(self, error_matches: List[ErrorMatch]) -> List[str]:
        """Generate suggestions based on detected errors."""
        suggestions = []

        for match in error_matches[:3]:  # Top 3 categories
            if match.category == ErrorCategory.TYPESCRIPT:
                if "error_code" in match.extracted_info:
                    code = match.extracted_info["error_code"][0]
                    suggestions.append(f"Check TypeScript error TS{code} documentation")

            elif match.category == ErrorCategory.MEMORY:
                suggestions.extend(
                    [
                        "Increase heap size with --max-old-space-size",
                        "Check for memory leaks and infinite loops",
                        "Profile memory usage with debugging tools",
                    ]
                )

            elif match.category == ErrorCategory.NETWORK:
                suggestions.extend(
                    [
                        "Check network connectivity and firewall settings",
                        "Verify API endpoints and CORS configuration",
                        "Review timeout settings and retry logic",
                    ]
                )

            elif match.category == ErrorCategory.DATABASE:
                suggestions.extend(
                    [
                        "Check database connection string",
                        "Verify database permissions and credentials",
                        "Review SQL queries for syntax errors",
                    ]
                )

        return list(dict.fromkeys(suggestions))[:5]  # Top 5 unique suggestions

    def _enhance_with_ml(
        self, text: str, results: List[ErrorMatch]
    ) -> List[ErrorMatch]:
        """Enhance results with ML classifier (placeholder for future implementation)."""
        # This is where ML classifier integration would go
        # For now, just return the original results
        return results

    def add_custom_pattern(self, pattern: ErrorPattern):
        """Add a custom error pattern."""
        self.patterns.append(pattern)

    def stream_detect(
        self, file_path: Union[str, Path], chunk_size: int = 8192
    ) -> List[ErrorMatch]:
        """
        Stream detection for large log files.

        Args:
            file_path: Path to the log file.
            chunk_size: Size of chunks to read.

        Returns:
            List of detected errors.
        """
        file_path = Path(file_path)
        all_matches = []
        overlap = 1024  # Overlap to catch errors spanning chunks

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            previous_chunk = ""

            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                # Combine with overlap from previous chunk
                combined = previous_chunk[-overlap:] + chunk

                # Detect errors in combined chunk
                matches = self.detect_multi_label(combined)
                all_matches.extend(matches)

                previous_chunk = chunk

        # Deduplicate and merge results
        return self._merge_matches(all_matches)

    def _merge_matches(self, matches: List[ErrorMatch]) -> List[ErrorMatch]:
        """Merge duplicate matches from streaming."""
        # Group by category
        category_matches = defaultdict(list)
        for match in matches:
            category_matches[match.category].append(match)

        # Merge each category
        merged = []
        for category, cat_matches in category_matches.items():
            if not cat_matches:
                continue

            # Average confidence scores
            avg_confidence = sum(m.confidence for m in cat_matches) / len(cat_matches)

            # Merge extracted info
            merged_info = {}
            for match in cat_matches:
                for key, values in match.extracted_info.items():
                    if key not in merged_info:
                        merged_info[key] = []
                    merged_info[key].extend(values)

            # Deduplicate
            for key in merged_info:
                merged_info[key] = list(dict.fromkeys(merged_info[key]))

            # Use highest severity
            severity = max(
                (m.severity for m in cat_matches),
                key=lambda s: ["low", "medium", "high", "critical"].index(s),
            )

            merged_match = ErrorMatch(
                category=category,
                confidence=avg_confidence,
                matches=[],
                extracted_info=merged_info,
                severity=severity,
            )
            merged.append(merged_match)

        return sorted(merged, key=lambda x: x.confidence, reverse=True)
