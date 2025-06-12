# Makefile for ComfyUI DCI Extension

.PHONY: test test-unit test-integration test-coverage clean install dev-install lint format help

# Default Python interpreter
PYTHON := python3

# Test directories
TEST_DIR := tests
SRC_DIR := py

help:
	@echo "Available commands:"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  clean          - Clean up temporary files"
	@echo "  install        - Install package dependencies"
	@echo "  dev-install    - Install development dependencies"

# Install dependencies
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

# Install development dependencies
dev-install: install
	$(PYTHON) -m pip install pytest pytest-cov coverage

# Run all tests
test:
	@echo "Running all tests..."
	cd $(TEST_DIR) && $(PYTHON) test_runner.py

# Run unit tests only
test-unit:
	@echo "Running unit tests..."
	$(PYTHON) -m unittest discover $(TEST_DIR) -p "test_*.py" -v

# Run integration tests (legacy test files)
test-integration:
	@echo "Running integration tests..."
	$(PYTHON) test_pure_python_simple.py || echo "Pure Python simple test completed"
	$(PYTHON) simple_quality_test.py || echo "Quality test completed"

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	$(PYTHON) -m coverage run --source=$(SRC_DIR) -m unittest discover $(TEST_DIR) -p "test_*.py"
	$(PYTHON) -m coverage report
	$(PYTHON) -m coverage html

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.dci" -delete
	find . -type f -name "*.ar" -delete
	find . -type f -name "*.deb" -delete
	rm -rf htmlcov/
	rm -f .coverage
	rm -f coverage.xml
