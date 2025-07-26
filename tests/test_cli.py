"""Tests for CLI interface."""

import pytest
from click.testing import CliRunner

from claudecode_debugger.cli import main


class TestCLI:
    """Test cases for CLI interface."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_help_command(self, runner):
        """Test help command."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "ClaudeCode-Debugger" in result.output
        assert "Smart debug prompt generator" in result.output

    def test_basic_error_input(self, runner):
        """Test basic error input."""
        result = runner.invoke(main, ["TypeError: Cannot read property"])
        assert result.exit_code == 0
        assert "JavaScript" in result.output or "Debug" in result.output

    def test_file_input(self, runner, tmp_path):
        """Test file input option."""
        # Create test error file
        error_file = tmp_path / "error.log"
        error_file.write_text(
            "TS2322: Type 'string' is not assignable to type 'number'"
        )

        result = runner.invoke(main, ["-f", str(error_file)])
        assert result.exit_code == 0
        assert "TypeScript" in result.output or "TS2322" in result.output

    def test_type_override(self, runner):
        """Test error type override."""
        result = runner.invoke(main, ["Some error", "-t", "python"])
        assert result.exit_code == 0
        # Should use Python template
        assert "Python" in result.output or "backend-system-architect" in result.output

    def test_output_to_file(self, runner, tmp_path):
        """Test output to file."""
        output_file = tmp_path / "debug-prompt.md"

        result = runner.invoke(main, ["TypeError: undefined", "-o", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Saved to" in result.output

        # Check file content
        content = output_file.read_text()
        assert "Debug" in content

    def test_list_templates(self, runner):
        """Test listing templates."""
        result = runner.invoke(main, ["--list-templates"])
        assert result.exit_code == 0
        assert "Available Templates" in result.output
        assert "typescript" in result.output
        assert "python" in result.output

    def test_empty_input_error(self, runner):
        """Test error with no input."""
        result = runner.invoke(main, [])
        assert result.exit_code == 1
        assert "No error content provided" in result.output

    def test_verbose_mode(self, runner):
        """Test verbose output."""
        result = runner.invoke(main, ["TypeError: Cannot read property", "-v"])
        assert result.exit_code == 0
        assert "Analysis Details" in result.output

    def test_custom_agent(self, runner):
        """Test custom agent selection."""
        result = runner.invoke(
            main, ["Some error", "--agent", "frontend-system-builder"]
        )
        assert result.exit_code == 0
        # Should mention the custom agent
        assert "frontend-system-builder" in result.output
