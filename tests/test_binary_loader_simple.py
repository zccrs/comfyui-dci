#!/usr/bin/env python3
"""
Simple test for BinaryFileLoader modifications (without heavy dependencies)
"""

import os
import tempfile
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_binary_file_loader_interface():
    """Test BinaryFileLoader interface without actually running it"""

    print("Testing BinaryFileLoader Interface")
    print("=" * 40)

    # Import the class definition
    try:
        # Mock the dependencies that cause import issues
        sys.modules['torch'] = type(sys)('torch')
        sys.modules['torch.nn'] = type(sys)('torch.nn')
        sys.modules['torch.nn.functional'] = type(sys)('torch.nn.functional')
        sys.modules['torchvision'] = type(sys)('torchvision')
        sys.modules['torchvision.transforms'] = type(sys)('torchvision.transforms')
        sys.modules['torchvision.transforms.functional'] = type(sys)('torchvision.transforms.functional')

        from py.nodes import BinaryFileLoader

        print("✓ Successfully imported BinaryFileLoader")

        # Check class attributes
        input_types = BinaryFileLoader.INPUT_TYPES()
        print(f"✓ Input types: {input_types}")

        return_types = BinaryFileLoader.RETURN_TYPES
        return_names = BinaryFileLoader.RETURN_NAMES

        print(f"✓ Return types: {return_types}")
        print(f"✓ Return names: {return_names}")

        # Verify the interface changes
        expected_return_types = ("BINARY_DATA", "STRING")
        expected_return_names = ("binary_data", "file_path")

        if return_types == expected_return_types:
            print("✓ Return types are correct")
        else:
            print(f"✗ Return types mismatch. Expected: {expected_return_types}, Got: {return_types}")
            return False

        if return_names == expected_return_names:
            print("✓ Return names are correct")
        else:
            print(f"✗ Return names mismatch. Expected: {expected_return_names}, Got: {return_names}")
            return False

        print("\n✅ BinaryFileLoader interface is correctly updated!")
        print("- Now outputs both binary_data and file_path")
        print("- Output name changed from 'dci_file_path' to 'file_path'")
        print("- Suitable for loading any binary file, not just DCI files")

        return True

    except Exception as e:
        print(f"✗ Failed to import or test BinaryFileLoader: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_expected_behavior():
    """Test the expected behavior description"""

    print("\n\nExpected Behavior After Fix")
    print("=" * 40)

    print("Before fix:")
    print("- BinaryFileLoader.RETURN_TYPES = ('BINARY_DATA',)")
    print("- BinaryFileLoader.RETURN_NAMES = ('binary_data',)")
    print("- Only returned binary data, no file path")

    print("\nAfter fix:")
    print("- BinaryFileLoader.RETURN_TYPES = ('BINARY_DATA', 'STRING')")
    print("- BinaryFileLoader.RETURN_NAMES = ('binary_data', 'file_path')")
    print("- Returns both binary data and the file path")
    print("- Output name 'file_path' is more generic than 'dci_file_path'")

    print("\nUsage in ComfyUI workflow:")
    print("1. Connect file_path input to specify which file to load")
    print("2. Use binary_data output for further processing")
    print("3. Use file_path output to know which file was actually loaded")
    print("4. Can load any binary file format, not limited to DCI files")

if __name__ == "__main__":
    success = test_binary_file_loader_interface()
    test_expected_behavior()

    if success:
        print("\n🎉 BinaryFileLoader modifications verified successfully!")
    else:
        print("\n❌ BinaryFileLoader modifications verification failed!")
        sys.exit(1)
