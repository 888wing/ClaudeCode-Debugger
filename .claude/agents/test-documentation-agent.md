# test-documentation-agent

**Purpose**: 確保代碼品質和文檔完整

**Activation**: 
- Manual: `--agent test-documentation-agent`
- Automatic: Test creation, documentation writing, coverage analysis, CI/CD setup

**Core Capabilities**:
- 單元測試設計 (pytest)
- 整合測試
- 文檔生成
- 使用範例
- CI/CD 配置
- Coverage reporting
- API documentation

**Specialized Knowledge**:
- Pytest fixtures and parametrization
- Test-driven development
- Documentation standards (NumPy, Google)
- Sphinx documentation
- GitHub Actions workflows
- Code coverage tools
- Benchmark testing

**Integration Points**:
- Works with project-setup-agent for initial structure
- Coordinates with QA persona for test strategies
- Integrates with Scribe persona for documentation
- Leverages DevOps persona for CI/CD

**Test Structure**:

### Unit Tests
```python
# tests/unit/test_detector.py
import pytest
from claudecode_debugger.core.detector import ErrorDetector

class TestErrorDetector:
    @pytest.fixture
    def detector(self):
        return ErrorDetector()
    
    @pytest.mark.parametrize("error_text,expected_type", [
        ("TS2322: Type 'string' is not assignable", "typescript"),
        ("TypeError: Cannot read property", "javascript"),
        ("Traceback (most recent call last):", "python"),
        ("FATAL ERROR: JavaScript heap out of memory", "memory"),
        ("CORS policy: No 'Access-Control'", "network"),
    ])
    def test_detect_error_type(self, detector, error_text, expected_type):
        """Test error type detection"""
        assert detector.detect(error_text) == expected_type
    
    def test_extract_key_info(self, detector):
        """Test key information extraction"""
        error_text = '''
        File "app.py", line 42, in process
        TypeError: unsupported operand type(s)
        '''
        info = detector.extract_key_info(error_text, "python")
        
        assert "app.py" in info['files']
        assert 42 in info['line_numbers']
        assert "TypeError" in str(info['error_codes'])
```

### Integration Tests
```python
# tests/integration/test_cli.py
from click.testing import CliRunner
from claudecode_debugger.cli import main

class TestCLI:
    def test_basic_command(self):
        """Test basic CLI command"""
        runner = CliRunner()
        result = runner.invoke(main, ['test error'])
        
        assert result.exit_code == 0
        assert 'Debug Prompt' in result.output
    
    def test_file_input(self, tmp_path):
        """Test file input option"""
        error_file = tmp_path / "error.log"
        error_file.write_text("TS2322: Type error")
        
        runner = CliRunner()
        result = runner.invoke(main, ['-f', str(error_file)])
        
        assert result.exit_code == 0
        assert 'TypeScript' in result.output
```

### Performance Tests
```python
# tests/performance/test_performance.py
import pytest
import time
from claudecode_debugger.core.detector import ErrorDetector

def test_large_file_performance(benchmark):
    """Test performance with large error logs"""
    detector = ErrorDetector()
    large_error = "Error line\n" * 10000
    
    result = benchmark(detector.detect, large_error)
    assert result is not None

@pytest.mark.slow
def test_concurrent_processing():
    """Test concurrent error processing"""
    # Implementation
    pass
```

**Documentation Structure**:

### README.md Template
```markdown
# ClaudeCode-Debugger

[![CI](https://github.com/888wing/ClaudeCode-Debugger/workflows/CI/badge.svg)](https://github.com/888wing/ClaudeCode-Debugger/actions)
[![Coverage](https://codecov.io/gh/888wing/ClaudeCode-Debugger/branch/main/graph/badge.svg)](https://codecov.io/gh/888wing/ClaudeCode-Debugger)
[![PyPI](https://img.shields.io/pypi/v/claudecode-debugger.svg)](https://pypi.org/project/claudecode-debugger/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Smart debug prompt generator for Claude Code - Transform error messages into actionable debug prompts.

## ✨ Features

- 🔍 **Automatic Error Detection** - Intelligently identifies error types across multiple languages
- 🤖 **Smart Agent Selection** - Chooses the optimal Claude Code agent for each error type
- 📋 **One-Click Copy** - Instantly copy generated prompts to clipboard
- 🎨 **Beautiful Output** - Rich, colorful terminal output for better readability
- 📊 **Error Analysis** - Provides severity assessment and fix time estimates
- 🔧 **Extensible Templates** - Customize prompts with YAML templates
- 📈 **Learning System** - Improves suggestions based on historical solutions

## 🚀 Quick Start

### Installation

```bash
pip install claudecode-debugger
```

### Basic Usage

```bash
# Analyze error from command line
ccdebug "TypeError: Cannot read property 'name' of undefined"

# Read from file
ccdebug -f error.log

# Copy to clipboard
ccdebug -c

# Interactive mode
ccdebug -i
```

## 📖 Documentation

Full documentation available at [https://claudecode-debugger.readthedocs.io](https://claudecode-debugger.readthedocs.io)

### Examples

#### TypeScript Error
```bash
$ ccdebug "TS2322: Type 'string' is not assignable to type 'number'"

🚨 TypeScript Compilation Error - HIGH Priority Debug

## Error Summary
Detected 1 error(s) affecting:
- Unknown file

## Debug Tasks
1. **Type Safety Analysis**
   - Review type definitions
   - Check for implicit any usage
   
[Copied to clipboard!]
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

### API Documentation
```python
"""
ClaudeCode-Debugger API Documentation

.. module:: claudecode_debugger
   :synopsis: Smart debug prompt generator for Claude Code

.. moduleauthor:: 888wing
"""

class ErrorDetector:
    """
    Detects and classifies error types from text.
    
    Example:
        >>> detector = ErrorDetector()
        >>> error_type = detector.detect("TS2322: Type error")
        >>> print(error_type)
        'typescript'
    
    Attributes:
        patterns (Dict[str, List[str]]): Error patterns by type
    """
    
    def detect(self, error_text: str) -> str:
        """
        Detect error type from text.
        
        Args:
            error_text: The error message or log
            
        Returns:
            str: Detected error type
            
        Example:
            >>> detector.detect("TypeError: undefined")
            'javascript'
        """
```

**CI/CD Configuration**:
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
        
    - name: Run tests
      run: |
        pytest --cov=claudecode_debugger --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```