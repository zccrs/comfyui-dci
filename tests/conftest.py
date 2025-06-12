#!/usr/bin/env python3
"""
Pytest configuration file
"""

import pytest
import os
import sys
import tempfile
import shutil

# Add project path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data"""
    temp_dir = tempfile.mkdtemp(prefix="comfyui_dci_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def temp_dir():
    """Create a temporary directory for individual tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def sample_binary_data():
    """Provide sample binary data for testing"""
    return b"Sample binary data for testing purposes"

@pytest.fixture
def sample_dci_content():
    """Provide sample DCI content for testing"""
    return b"DCI\x00\x01\x01\x00\x00"  # Basic DCI header

def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers to tests based on their names
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.nodeid or "test_" in item.nodeid:
            item.add_marker(pytest.mark.unit)

        # Mark slow tests
        if any(keyword in item.nodeid.lower() for keyword in ["slow", "large", "comprehensive"]):
            item.add_marker(pytest.mark.slow)

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment for each test"""
    # Ensure clean environment
    original_cwd = os.getcwd()
    yield
    # Cleanup after test
    os.chdir(original_cwd)
