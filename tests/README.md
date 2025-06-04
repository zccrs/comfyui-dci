# Tests Directory

This directory contains all test files for the ComfyUI DCI Extension.

## Test Files

### Core Functionality Tests
- **test_dci.py**: Basic DCI format functionality tests
- **test_dci_preview.py**: DCI preview functionality tests
- **test_binary_nodes.py**: Binary file handling node tests
- **test_new_dci_nodes.py**: New DCI node architecture tests
- **test_node_loading.py**: Node loading and registration tests

### Simple Tests
- **simple_test.py**: Simple functionality verification
- **simple_binary_test.py**: Basic binary operations test

## Running Tests

### Individual Tests
```bash
# Run specific test file
python tests/test_dci.py
python tests/test_dci_preview.py
```

### All Tests
```bash
# Run all tests (if using pytest)
pytest tests/

# Or run all Python test files
python -m unittest discover tests/
```

## Test Structure

Each test file follows the pattern:
- Setup test environment
- Create test data
- Execute functionality
- Verify results
- Cleanup

## Test Data

Test files may create temporary DCI files and other test artifacts. These are typically cleaned up automatically after tests complete.

## Coverage

Tests cover:
- DCI file creation and reading
- Node functionality and integration
- Binary data handling
- Preview generation
- Metadata extraction
- Error handling and edge cases
