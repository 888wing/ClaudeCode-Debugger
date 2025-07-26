"""Tests for ErrorDetector module."""

import pytest

from claudecode_debugger.core.detector import ErrorDetector


class TestErrorDetector:
    """Test cases for ErrorDetector class."""

    @pytest.fixture
    def detector(self):
        """Create ErrorDetector instance."""
        return ErrorDetector()

    @pytest.mark.parametrize(
        "error_text,expected_type",
        [
            # TypeScript errors
            ("TS2322: Type 'string' is not assignable to type 'number'", "typescript"),
            ("error TS2339: Property 'foo' does not exist on type", "typescript"),
            ("Cannot find module '@/components/Header'", "typescript"),
            # JavaScript errors
            ("TypeError: Cannot read property 'name' of undefined", "javascript"),
            ("ReferenceError: foo is not defined", "javascript"),
            ("SyntaxError: Unexpected token }", "javascript"),
            # Python errors
            ("Traceback (most recent call last):\n  File 'app.py'", "python"),
            ("ImportError: No module named requests", "python"),
            ("IndentationError: unexpected indent", "python"),
            # Memory errors
            ("FATAL ERROR: JavaScript heap out of memory", "memory"),
            ("Maximum call stack size exceeded", "memory"),
            # Network errors
            ("CORS policy: No 'Access-Control-Allow-Origin'", "network"),
            ("ERR_CONNECTION_REFUSED", "network"),
            ("fetch failed", "network"),
        ],
    )
    def test_detect_error_type(self, detector, error_text, expected_type):
        """Test error type detection."""
        result = detector.detect(error_text)
        assert result == expected_type

    def test_detect_empty_error(self, detector):
        """Test detection with empty error text."""
        assert detector.detect("") == "general"
        assert detector.detect(None) == "general"

    def test_extract_files(self, detector):
        """Test file extraction."""
        error_text = """
        File "app.py", line 42, in process
        at src/components/Header.tsx:15:8
        Error in /home/user/project/main.js
        """

        info = detector.extract_key_info(error_text, "general")
        files = info["files"]

        assert "app.py" in files
        assert "Header.tsx" in files
        assert "main.js" in files

    def test_extract_line_numbers(self, detector):
        """Test line number extraction."""
        error_text = """
        File "app.py", line 42
        at Header.tsx:15:8
        Error on line 100
        """

        info = detector.extract_key_info(error_text, "general")
        lines = info["line_numbers"]

        assert 42 in lines
        assert 15 in lines
        assert 100 in lines

    def test_extract_typescript_error_codes(self, detector):
        """Test TypeScript error code extraction."""
        error_text = "TS2322: Type error\nTS2339: Property not found"

        info = detector.extract_key_info(error_text, "typescript")
        codes = info["error_codes"]

        assert "TS2322" in codes
        assert "TS2339" in codes

    def test_extract_python_error_codes(self, detector):
        """Test Python error code extraction."""
        error_text = """
        Traceback (most recent call last):
        TypeError: unsupported operand
        ValueError: invalid literal
        """

        info = detector.extract_key_info(error_text, "python")
        codes = info["error_codes"]

        assert "TypeError" in codes
        assert "ValueError" in codes

    def test_severity_assessment(self, detector):
        """Test error severity assessment."""
        # Critical
        assert (
            detector.get_severity("FATAL ERROR: out of memory", "memory") == "critical"
        )
        assert detector.get_severity("Build failed", "build") == "critical"

        # High
        assert detector.get_severity("TypeError: undefined", "javascript") == "high"

        # Medium
        assert detector.get_severity("CORS error", "network") == "medium"

        # Low
        assert detector.get_severity("Warning: deprecated", "general") == "low"

    def test_complex_error_detection(self, detector):
        """Test detection with complex real-world errors."""
        typescript_error = """
        src/components/Dashboard.tsx:45:12 - error TS2322: Type 'string' is not assignable to type 'number'.
        
        45   const count: number = "10";
                   ~~~~~
        
        Found 1 error.
        """

        assert detector.detect(typescript_error) == "typescript"
        info = detector.extract_key_info(typescript_error, "typescript")
        assert "Dashboard.tsx" in info["files"]
        assert 45 in info["line_numbers"]
        assert "TS2322" in info["error_codes"]
