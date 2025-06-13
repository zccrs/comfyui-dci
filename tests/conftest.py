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

# Check for optional dependencies
HAS_TORCH = False
HAS_COMFYUI = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    pass

try:
    import folder_paths
    HAS_COMFYUI = True
except ImportError:
    pass

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
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "requires_torch: mark test as requiring torch"
    )
    config.addinivalue_line(
        "markers", "requires_comfyui: mark test as requiring ComfyUI environment"
    )
    config.addinivalue_line(
        "markers", "pure_python: mark test as pure Python (no torch/ComfyUI required)"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip tests based on available dependencies"""
    skip_torch = pytest.mark.skip(reason="torch not available")
    skip_comfyui = pytest.mark.skip(reason="ComfyUI environment not available")

    for item in items:
        # Skip torch-dependent tests if torch is not available
        if "requires_torch" in item.keywords and not HAS_TORCH:
            item.add_marker(skip_torch)

        # Skip ComfyUI-dependent tests if ComfyUI is not available
        if "requires_comfyui" in item.keywords and not HAS_COMFYUI:
            item.add_marker(skip_comfyui)

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment for each test"""
    # Ensure clean environment
    original_cwd = os.getcwd()
    yield
    # Cleanup after test
    os.chdir(original_cwd)

@pytest.fixture
def has_torch():
    """Fixture to check if torch is available"""
    return HAS_TORCH

@pytest.fixture
def has_comfyui():
    """Fixture to check if ComfyUI is available"""
    return HAS_COMFYUI

@pytest.fixture
def skip_if_no_torch():
    """Fixture to skip test if torch is not available"""
    if not HAS_TORCH:
        pytest.skip("torch not available")

@pytest.fixture
def skip_if_no_comfyui():
    """Fixture to skip test if ComfyUI is not available"""
    if not HAS_COMFYUI:
        pytest.skip("ComfyUI environment not available")
