.PHONY: help install dev test lint format clean build publish docs

# Default target
help:
	@echo "ClaudeCode-Debugger Development Commands"
	@echo "========================================"
	@echo "install    - Install package in production mode"
	@echo "dev        - Install package in development mode with all dependencies"
	@echo "test       - Run all tests with coverage"
	@echo "lint       - Run linting checks (flake8, mypy)"
	@echo "format     - Format code with black and isort"
	@echo "clean      - Remove build artifacts and cache files"
	@echo "build      - Build distribution packages"
	@echo "publish    - Publish to PyPI (requires credentials)"
	@echo "docs       - Build documentation"

# Installation
install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pre-commit install

# Testing
test:
	pytest

test-verbose:
	pytest -vv

test-coverage:
	pytest --cov=claudecode_debugger --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 claudecode_debugger tests
	mypy claudecode_debugger

format:
	black claudecode_debugger tests
	isort claudecode_debugger tests

check:
	black --check claudecode_debugger tests
	isort --check-only claudecode_debugger tests
	flake8 claudecode_debugger tests
	mypy claudecode_debugger

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Building and publishing
build: clean
	python -m build

publish-test: build
	python -m twine upload --repository testpypi dist/*

publish: build
	python -m twine upload dist/*

# Documentation
docs:
	cd docs && make html

docs-serve:
	cd docs && python -m http.server --directory _build/html

# Development shortcuts
run:
	ccdebug

run-help:
	ccdebug --help