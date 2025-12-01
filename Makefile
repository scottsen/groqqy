.PHONY: help install install-dev test test-unit test-integration test-examples lint format clean docs

# Default target
help:
	@echo "Groqqy Development Tasks"
	@echo ""
	@echo "  make install         - Install groqqy in development mode"
	@echo "  make install-dev     - Install with dev dependencies"
	@echo "  make test            - Run all tests"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-examples   - Run example tests only"
	@echo "  make lint            - Run linters (flake8, mypy)"
	@echo "  make format          - Format code with black"
	@echo "  make clean           - Remove build artifacts"
	@echo "  make docs            - Generate documentation"
	@echo ""

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	@echo "Running all tests..."
	pytest tests/ -v

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/ -v

test-examples:
	@echo "Running example tests..."
	pytest tests/examples/ -v

test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=groqqy --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

# Code Quality
lint:
	@echo "Running flake8..."
	flake8 groqqy/ tests/ --max-line-length=100 --ignore=E203,W503
	@echo "Running mypy..."
	mypy groqqy/ --ignore-missing-imports

format:
	@echo "Formatting code with black..."
	black groqqy/ tests/ examples/

format-check:
	@echo "Checking code format..."
	black --check groqqy/ tests/ examples/

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .eggs/
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	rm -rf test_output*/ *_output/ *.tmp *.bak
	@echo "Clean complete!"

# Container testing
container-test:
	@echo "Running container tests..."
	./container_test.sh

# Documentation
docs:
	@echo "Documentation available in docs/ directory"
	@echo "  docs/USER_GUIDE.md       - Comprehensive usage guide"
	@echo "  docs/ARCHITECTURE.md     - Design and architecture"
	@echo "  docs/TEACHING_GUIDE.md   - Teaching and learning guide"

# Development workflow
dev-setup: install-dev
	@echo "Development environment ready!"
	@echo "Next steps:"
	@echo "  1. Set GROQ_API_KEY environment variable"
	@echo "  2. Run 'make test' to verify setup"
	@echo "  3. Run 'python examples/basic_chat.py' to test"

# Quick checks before commit
pre-commit: format lint test
	@echo "✅ Pre-commit checks passed!"
