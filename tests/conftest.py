"""Pytest configuration and fixtures."""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from click.testing import CliRunner

# Add the parent directory to the path to import the package
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_cwd)


@pytest.fixture
def sample_error_log() -> str:
    """Sample error log for testing."""
    return """
Traceback (most recent call last):
  File "main.py", line 42, in process_data
    result = divide_numbers(10, 0)
  File "utils.py", line 15, in divide_numbers
    return a / b
ZeroDivisionError: division by zero
"""


@pytest.fixture
def sample_config() -> dict:
    """Sample configuration for testing."""
    return {
        "templates": {
            "default": {
                "format": "markdown",
                "include_context": True,
                "max_lines": 50,
            }
        },
        "output": {
            "copy_to_clipboard": True,
            "save_to_file": False,
        },
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)
