#!/usr/bin/env python3
"""
Test runner for all unit tests
"""

import unittest
import sys
import os

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """Run all unit tests"""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    # Return success status
    return result.wasSuccessful()

def run_specific_test_module(module_name):
    """Run tests from a specific module"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(module_name)

    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    return result.wasSuccessful()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        success = run_specific_test_module(module_name)
    else:
        # Run all tests
        success = run_all_tests()

    sys.exit(0 if success else 1)
