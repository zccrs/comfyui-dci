#!/usr/bin/env python3
"""
Test script for DCIFileSaver node
"""

import sys
import os
import tempfile

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from py.nodes.dci_file_saver_node import DCIFileSaver

def test_filename_parsing():
    """Test filename parsing functionality"""
    saver = DCIFileSaver()

    # Test cases for filename parsing
    test_cases = [
        # (input, expected_output)
        ("a.png", "a.dci"),
        ("icon.webp", "icon.dci"),
        ("test.jpg", "test.dci"),
        ("image.jpeg", "image.dci"),
        ("file.apng", "file.dci"),
        ("/home/user/icon.png", "icon.dci"),
        ("C:\\Users\\test\\image.webp", "image.dci"),
        ("../relative/path/file.jpg", "file.dci"),
        ("no_extension", "no_extension.dci"),
        ("", "icon.dci"),
        ("just_path/", "icon.dci"),
    ]

    print("Testing filename parsing:")
    for input_name, expected in test_cases:
        result = saver._parse_filename(input_name)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_name}' -> '{result}' (expected: '{expected}')")
        if result != expected:
            print(f"    ERROR: Expected '{expected}', got '{result}'")

def test_prefix_suffix():
    """Test prefix and suffix functionality"""
    saver = DCIFileSaver()

    test_cases = [
        # (filename, prefix, suffix, expected)
        ("test.dci", "", "", "test.dci"),
        ("test.dci", "prefix-", "", "prefix-test.dci"),
        ("test.dci", "", "-suffix", "test-suffix.dci"),
        ("test.dci", "prefix-", "-suffix", "prefix-test-suffix.dci"),
        ("test", "pre_", "_suf", "pre_test_suf.dci"),
    ]

    print("\nTesting prefix/suffix functionality:")
    for filename, prefix, suffix, expected in test_cases:
        result = saver._apply_prefix_suffix(filename, prefix, suffix)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{filename}' + '{prefix}' + '{suffix}' -> '{result}' (expected: '{expected}')")
        if result != expected:
            print(f"    ERROR: Expected '{expected}', got '{result}'")

def test_extension_removal():
    """Test image extension removal"""
    saver = DCIFileSaver()

    test_cases = [
        # (input, expected)
        ("test.png", "test"),
        ("image.PNG", "image"),
        ("file.webp", "file"),
        ("icon.JPEG", "icon"),
        ("picture.jpg", "picture"),
        ("animation.apng", "animation"),
        ("no_extension", "no_extension"),
        ("test.txt", "test.txt"),  # Non-image extension should remain
        ("file.dci", "file.dci"),  # DCI extension should remain
    ]

    print("\nTesting extension removal:")
    for input_name, expected in test_cases:
        result = saver._remove_image_extension(input_name)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_name}' -> '{result}' (expected: '{expected}')")
        if result != expected:
            print(f"    ERROR: Expected '{expected}', got '{result}'")

def test_full_workflow():
    """Test the complete workflow with mock binary data"""
    print("\nTesting full workflow:")

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        saver = DCIFileSaver()

        # Mock binary data
        test_data = b"Mock DCI binary data for testing"

        # Test cases
        test_cases = [
            {
                "input_filename": "a.png",
                "output_directory": temp_dir,
                "filename_prefix": "",
                "filename_suffix": "",
                "expected_filename": "a.dci",
            },
            {
                "input_filename": "/home/user/icon.webp",
                "output_directory": temp_dir,
                "filename_prefix": "prefix-",
                "filename_suffix": "-suffix",
                "expected_filename": "prefix-icon-suffix.dci",
            },
        ]

        for i, test_case in enumerate(test_cases):
            print(f"\n  Test case {i+1}:")
            print(f"    Input: {test_case['input_filename']}")
            print(f"    Prefix: '{test_case['filename_prefix']}'")
            print(f"    Suffix: '{test_case['filename_suffix']}'")

            try:
                result_filename, result_path = saver._execute(
                    binary_data=test_data,
                    input_filename=test_case['input_filename'],
                    output_directory=test_case['output_directory'],
                    filename_prefix=test_case['filename_prefix'],
                    filename_suffix=test_case['filename_suffix']
                )

                expected_path = os.path.join(temp_dir, test_case['expected_filename'])

                print(f"    Result filename: {result_filename}")
                print(f"    Result path: {result_path}")
                print(f"    Expected filename: {test_case['expected_filename']}")
                print(f"    Expected path: {expected_path}")

                # Check if file was created
                if os.path.exists(result_path):
                    print("    ✓ File created successfully")

                    # Check file content
                    with open(result_path, 'rb') as f:
                        saved_data = f.read()

                    if saved_data == test_data:
                        print("    ✓ File content matches")
                    else:
                        print("    ✗ File content mismatch")
                else:
                    print("    ✗ File was not created")

            except Exception as e:
                print(f"    ✗ Error during execution: {e}")

if __name__ == "__main__":
    print("DCIFileSaver Node Test Suite")
    print("=" * 40)

    test_filename_parsing()
    test_prefix_suffix()
    test_extension_removal()
    test_full_workflow()

    print("\n" + "=" * 40)
    print("Test suite completed!")
