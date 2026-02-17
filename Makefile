.PHONY: help install dev clean test coverage lint format audit run docker-build docker-run

# Default target
help:
	@echo "AI Diagnostic - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install production dependencies"
	@echo "  make dev           Install development dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format        Format code with black and isort"
	@echo "  make lint          Run linting checks (flake8, pylint)"
	@echo "  make audit         Run security audit on dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run test suite"
	@echo "  make coverage      Run tests with coverage report"
	@echo "  make test-watch    Run tests in watch mode"
	@echo ""
	@echo "Development:"
	@echo "  make run           Start development server"
	@echo "  make run-prod      Start production server"
	@echo "  make shell         Open Python shell with project context"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         Remove temporary files and caches"
	@echo "  make clean-all     Deep clean including virtual environment"
	@echo "  make update        Update all dependencies"
	@echo ""
	@echo "Evaluation:"
	@echo "  make evaluate      Run diagnostic evaluation suite"
	@echo ""

# Installation
install:
	@echo "Installing production dependencies..."
	uv sync --no-dev

dev:
	@echo "Installing development dependencies..."
	uv sync

# Code quality
format:
	@echo "Formatting code..."
	uv run black app/ tests/ run_evaluation.py
	uv run isort app/ tests/ run_evaluation.py
	@echo "✓ Code formatted"

lint:
	@echo "Running linting checks..."
	@echo "\n=== Flake8 ==="
	uv run flake8 app/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	uv run flake8 app/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "\n=== Pylint ==="
	uv run pylint app/ tests/ || true
	@echo "\n✓ Linting complete"

audit:
	@echo "Running security audit..."
	uv run pip-audit
	@echo "✓ Security audit complete"

# Testing
test:
	@echo "Running test suite..."
	uv run pytest tests/ -v

coverage:
	@echo "Running tests with coverage..."
	uv run pytest tests/ \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-report=xml \
		-v
	@echo "\n✓ Coverage report generated in htmlcov/"

test-watch:
	@echo "Running tests in watch mode..."
	uv run pytest-watch tests/ -- -v

# Development server
run:
	@echo "Starting development server..."
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	@echo "Starting production server..."
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

shell:
	@echo "Opening Python shell..."
	uv run python

# Evaluation
evaluate:
	@echo "Running diagnostic evaluation..."
	uv run python run_evaluation.py 10 10
	@echo "\n✓ Evaluation complete. See evaluation_report.json"

# Maintenance
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.py,cover" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml
	rm -rf dist/ build/
	@echo "✓ Cleaned temporary files"

clean-all: clean
	@echo "Deep cleaning..."
	rm -rf .venv/
	rm -rf uv.lock
	@echo "✓ Deep clean complete"

update:
	@echo "Updating dependencies..."
	uv lock --upgrade
	uv sync
	@echo "✓ Dependencies updated"

# CI/CD simulation
ci: lint audit test coverage
	@echo "\n✓ All CI checks passed"

# Quick checks before commit
pre-commit: format lint test
	@echo "\n✓ Pre-commit checks passed"
