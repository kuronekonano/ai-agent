# =====================================================
# Makefile for ai-agent Python project
# =====================================================

# Python interpreter and tools
PYTHON := python
PIP := $(PYTHON) -m pip
UV := uv

# Source and test directories
SRC_DIR := src
TEST_DIR := src\tests

# Tools
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy
PYTEST := $(PYTHON) -m pytest

# Project version (read from pyproject.toml)
VERSION := $(shell python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")

# Default target
.PHONY: help
help:
	@echo "Available make targets:"
	@echo "  format         - Run black + isort to format code"
	@echo "  c   - Run ruff + mypy for static checks"
	@echo "  lint           - Alias for static_check"
	@echo "  test           - Run unit tests"
	@echo "  install        - Install project dependencies via uv"
	@echo "  run            - Start AI agent CLI"
	@echo "  demo           - Run demonstration script"
	@echo "  clean          - Remove __pycache__ and temporary files"
	@echo "  venv           - Activate uv virtual environment"
	@echo "  release-test   - Build & deploy to test environment"
	@echo "  release-prod   - Build & deploy to production environment"

# ----------------------
# Code formatting
# ----------------------
.PHONY: format
format:
	@echo "Running isort..."
	$(ISORT) $(SRC_DIR) $(TEST_DIR)
	@echo "Running black..."
	$(BLACK) $(SRC_DIR) $(TEST_DIR)

# ----------------------
# Static checks
# ----------------------
.PHONY: static_check lint
static_check lint:
	@echo "Running ruff..."
	$(RUFF) check $(SRC_DIR) $(TEST_DIR)
	@echo "Running mypy..."
	cd $(SRC_DIR) && $(MYPY) .

# ----------------------
# Tests
# ----------------------
.PHONY: test
test:
	@echo "Running unit tests..."
	$(PYTEST) $(TEST_DIR)

# ----------------------
# Dependency management
# ----------------------
.PHONY: install
install:
	@echo "Installing project dependencies via uv..."
	$(UV) sync

# ----------------------
# ----------------------
# Project execution
# ----------------------
.PHONY: run demo
run:
	@echo "Starting ai-agent CLI..."
	$(PYTHON) -m ai_agent --help

demo:
	@echo "Running demo..."
	$(PYTHON) scripts/run_demo.py

# ----------------------
# Virtual environment helper
# ----------------------
.PHONY: venv
venv:
	@echo "Activating uv virtual environment..."
	$(UV) venv activate

# ----------------------
# Clean up
# ----------------------
.PHONY: clean
clean:
	@echo "Removing __pycache__ and temporary files..."
	-find $(SRC_DIR) $(TEST_DIR) -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	-find . -name "*.pyc" -delete 2>/dev/null || true
	-find . -name "*.pyo" -delete 2>/dev/null || true

# ----------------------
# Release targets
# ----------------------
.PHONY: release-test release-prod

release-test:
	@echo "Releasing ai-agent v$(VERSION) to TEST environment..."
	@echo "Build..."
	$(UV) build
	@echo "Deploy to TEST environment..."
	@echo "  (Placeholder: replace with your staging deploy script)"
	@echo "Release-test done."

release-prod:
	@echo "Releasing ai-agent v$(VERSION) to PROD environment..."
	@echo "Build..."
	$(UV) build
	@echo "Deploy to PROD environment..."
	@echo "  (Placeholder: replace with your production deploy script)"
	@echo "Release-prod done."
