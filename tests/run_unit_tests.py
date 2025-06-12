#!/usr/bin/env python3
"""
Simple unit test runner for new test files only
"""

import unittest
import sys
import os

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_unit_tests():
    """Run only the new unit test files"""
    # List of new unit test modules
    test_modules = [
        'test_dci_format',
        'test_pure_python_ar',
        'test_comfyui_nodes'
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Load only the specified test modules
    for module_name in test_modules:
        try:
            module_suite = loader.loadTestsFromName(module_name)
            suite.addTest(module_suite)
            print(f"✓ Loaded tests from {module_name}")
        except Exception as e:
            print(f"⚠ Failed to load {module_name}: {e}")

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_unit_tests()
    sys.exit(0 if success else 1)
