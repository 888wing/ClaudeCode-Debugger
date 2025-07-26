# Contributing to ClaudeCode-Debugger

Thank you for your interest in contributing to ClaudeCode-Debugger! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Make (optional but recommended)

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ClaudeCode-Debugger.git
   cd ClaudeCode-Debugger
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install in development mode:
   ```bash
   make dev
   # Or manually:
   pip install -e ".[dev]"
   pre-commit install
   ```

## 📝 Development Process

### 1. Create a Branch

Create a branch for your feature or bugfix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bugfix-name
```

### 2. Make Your Changes

- Write clean, readable code following PEP 8
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Update tests for your changes
- Update documentation if needed

### 3. Code Quality

Before committing, ensure your code passes all checks:

```bash
# Format code
make format

# Run linting
make lint

# Run tests
make test

# Or run all checks
make check
```

### 4. Commit Your Changes

Write clear, concise commit messages:

```bash
git add .
git commit -m "feat: add error similarity detection"
# or
git commit -m "fix: handle empty error messages gracefully"
```

Commit message format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions or changes
- `refactor:` for code refactoring
- `style:` for code style changes
- `chore:` for maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/test_detector.py

# Run with verbose output
pytest -vv
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names
- Include both positive and negative test cases
- Aim for high test coverage (>80%)

Example test:

```python
def test_detect_typescript_error():
    detector = ErrorDetector()
    error_text = "TS2322: Type 'string' is not assignable to type 'number'"
    
    result = detector.detect(error_text)
    
    assert result == "typescript"
    assert detector.extract_error_code(error_text) == "TS2322"
```

## 📚 Documentation

### Docstring Format

Use Google-style docstrings:

```python
def detect_error(error_text: str) -> str:
    """Detect the type of error from text.
    
    Args:
        error_text: The error message or log to analyze.
        
    Returns:
        The detected error type (e.g., 'typescript', 'python').
        
    Raises:
        ValueError: If error_text is empty.
        
    Example:
        >>> detect_error("TS2322: Type error")
        'typescript'
    """
```

### Updating Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update CHANGELOG.md for all changes

## 🎯 Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Coverage hasn't decreased
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## 🏗️ Project Structure

```
claudecode_debugger/
├── __init__.py
├── cli.py              # CLI entry point
├── core/
│   ├── __init__.py
│   ├── detector.py     # Error detection logic
│   ├── generator.py    # Prompt generation
│   └── analyzer.py     # Error analysis
├── templates/          # Built-in templates
├── plugins/           # Plugin system
└── utils/             # Utility functions
```

## 🔧 Adding New Features

### Adding Error Patterns

1. Update patterns in `detector.py`
2. Add tests for new patterns
3. Update documentation

### Adding Templates

1. Create YAML template in `templates/`
2. Register in template loader
3. Add example in documentation

### Adding Plugins

1. Inherit from `Plugin` base class
2. Implement required methods
3. Add tests and documentation

## 📮 Getting Help

- 💬 [GitHub Discussions](https://github.com/888wing/ClaudeCode-Debugger/discussions)
- 🐛 [Issue Tracker](https://github.com/888wing/ClaudeCode-Debugger/issues)
- 📧 Contact maintainers

## 🙏 Recognition

Contributors will be recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Project documentation

Thank you for contributing to ClaudeCode-Debugger!