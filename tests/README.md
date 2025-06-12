# ComfyUI DCI Extension - Test Suite

This directory contains comprehensive unit tests for the ComfyUI DCI Extension.

## Test Structure

### Unit Tests (New)
- `test_dci_format.py` - Tests for DCI format creation and parsing
- `test_pure_python_ar.py` - Tests for pure Python AR implementation
- `test_comfyui_nodes.py` - Tests for ComfyUI nodes
- `test_runner.py` - Test runner for all unit tests
- `conftest.py` - Pytest configuration and fixtures

### Legacy Tests (Integration)
The existing test files serve as integration tests:
- `test_dci_preview_*.py` - DCI preview functionality tests
- `test_dci_file_saver.py` - DCI file saving tests
- `test_binary_*.py` - Binary file handling tests
- `test_node_*.py` - Node registration and connectivity tests
- `test_real_dci_files.py` - Real DCI file processing tests
- And many more...

## Running Tests

### Using the Test Runner
```bash
# Run all unit tests
cd tests
python test_runner.py

# Run specific test module
python test_runner.py test_dci_format
```

### Using unittest
```bash
# Run all unit tests
python -m unittest discover tests -p "test_*.py" -v

# Run specific test class
python -m unittest tests.test_dci_format.TestDCIFormat -v

# Run specific test method
python -m unittest tests.test_dci_format.TestDCIFormat.test_basic_dci_creation -v
```

### Using pytest (if available)
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=py --cov-report=html

# Run only unit tests
python -m pytest tests/ -m unit

# Run only integration tests
python -m pytest tests/ -m integration
```

### Using Makefile
```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests
make test-integration

# Run with coverage
make test-coverage
```

## GitHub Actions

Tests are automatically run on GitHub Actions when:
- Code is pushed to main/master/develop branches
- Pull requests are created
- Manual workflow dispatch is triggered

The CI pipeline runs tests on multiple Python versions (3.8, 3.9, 3.10, 3.11) and includes:
- Unit tests
- Integration tests
- Cross-platform testing (Linux, Windows, macOS)
- Code coverage reporting

## Test Categories

### Unit Tests
- **DCI Format Tests**: Test DCI file creation, parsing, and structure validation
- **Pure Python AR Tests**: Test AR archive creation and extraction without external dependencies
- **ComfyUI Node Tests**: Test node initialization, execution, and integration

### Integration Tests
- **Legacy Test Files**: Existing test files that test complete workflows
- **Real File Processing**: Tests with actual DCI files and real-world scenarios
- **Cross-platform Compatibility**: Tests that verify functionality across different operating systems

## Test Features

### Automatic Test Discovery
- Tests are automatically discovered by pattern matching (`test_*.py`)
- Test classes must start with `Test`
- Test methods must start with `test_`

### Fixtures and Setup
- Temporary directories are automatically created and cleaned up
- Sample data is provided through fixtures
- Test environment is properly isolated

### Skip Conditions
- Tests are automatically skipped if required modules are not available
- This allows tests to run even in incomplete environments
- Graceful degradation for missing dependencies

### Coverage Reporting
- Code coverage is measured and reported
- HTML coverage reports are generated
- Coverage data is uploaded to Codecov (optional)

## Writing New Tests

### Unit Test Template
```python
import unittest
import tempfile
import shutil

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def test_feature_functionality(self):
        """Test specific functionality"""
        # Test implementation
        self.assertTrue(True)  # Replace with actual test

    @unittest.skipIf(condition, "reason")
    def test_conditional_feature(self):
        """Test that may be skipped"""
        # Test implementation
        pass
```

### Best Practices
1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Use `setUp()` and `tearDown()` or `addCleanup()` for resource management
3. **Descriptive Names**: Test names should clearly describe what is being tested
4. **Skip Conditions**: Use `@unittest.skipIf()` for tests that require specific conditions
5. **Assertions**: Use appropriate assertion methods (`assertEqual`, `assertTrue`, etc.)
6. **Documentation**: Include docstrings explaining what each test does

## Troubleshooting

### Common Issues
1. **Import Errors**: Make sure the project path is correctly added to `sys.path`
2. **Missing Dependencies**: Install test dependencies with `make dev-install`
3. **Permission Errors**: Ensure test directories are writable
4. **Path Issues**: Use `os.path.join()` for cross-platform path handling

### Debug Mode
Run tests with verbose output to see detailed information:
```bash
python -m unittest tests.test_module -v
```

### Test Isolation
If tests are interfering with each other:
1. Check that temporary files are properly cleaned up
2. Ensure global state is not modified
3. Use separate test directories for each test

## Contributing

When adding new functionality:
1. Write unit tests for new features
2. Update existing tests if behavior changes
3. Ensure all tests pass before submitting
4. Add integration tests for complex workflows
5. Update this documentation if needed
