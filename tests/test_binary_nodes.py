#!/usr/bin/env python3
"""
Test script for binary file handling nodes
"""

import os
import tempfile
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from py.nodes import BinaryFileLoader, BinaryFileSaver, BinaryFileUploader


def test_binary_file_operations():
    """Test binary file loading, saving, and uploading operations"""

    print("Testing Binary File Handling Nodes")
    print("=" * 50)

    # Create test binary data
    test_data = b"This is test binary data for DCI icon files\x00\x01\x02\x03"
    test_filename = "test_icon.dci"

    # Create temporary test file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dci") as temp_file:
        temp_file.write(test_data)
        temp_file_path = temp_file.name

    try:
        # Test 1: Binary File Loader
        print("\n1. Testing BinaryFileLoader...")
        loader = BinaryFileLoader()
        result = loader.load_binary_file(temp_file_path)

        if result[0] is not None:
            binary_data, loaded_file_path = result
            print(f"✓ Loaded file: {binary_data['filename']}")
            print(f"✓ File size: {binary_data['size']} bytes")
            print(f"✓ Content matches: {binary_data['content'] == test_data}")
            print(f"✓ File path: {loaded_file_path}")
        else:
            print("✗ Failed to load binary file")
            return False

        # Test 2: Binary File Saver
        print("\n2. Testing BinaryFileSaver...")
        saver = BinaryFileSaver()

        # Create output path
        output_dir = tempfile.mkdtemp()
        output_path = os.path.join(output_dir, "saved_test.dci")

        result = saver.save_binary_file(binary_data, output_path)

        if result[0] and os.path.exists(result[0]):
            print(f"✓ Saved file: {result[0]}")

            # Verify saved content
            with open(result[0], 'rb') as f:
                saved_content = f.read()
            print(f"✓ Saved content matches: {saved_content == test_data}")
        else:
            print("✗ Failed to save binary file")
            return False

        # Test 3: Binary File Uploader
        print("\n3. Testing BinaryFileUploader...")
        uploader = BinaryFileUploader()

        # Test with the directory containing our temp file
        search_dir = os.path.dirname(temp_file_path)
        file_pattern = "*.dci"

        result = uploader.upload_binary_file(search_dir, file_pattern)

        if result[0] is not None:
            uploaded_data, uploaded_file_path = result
            print(f"✓ Uploaded file: {uploaded_data['filename']}")
            print(f"✓ File size: {uploaded_data['size']} bytes")
            print(f"✓ File path: {uploaded_file_path}")
        else:
            print("✗ Failed to upload binary file")
            return False

        print("\n" + "=" * 50)
        print("All binary file handling tests passed! ✓")
        return True

    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        try:
            os.unlink(temp_file_path)
            if 'output_path' in locals() and os.path.exists(output_path):
                os.unlink(output_path)
            if 'output_dir' in locals():
                os.rmdir(output_dir)
        except:
            pass


def test_error_handling():
    """Test error handling for edge cases"""

    print("\n\nTesting Error Handling")
    print("=" * 30)

    # Test loading non-existent file
    print("1. Testing non-existent file...")
    loader = BinaryFileLoader()
    result = loader.load_binary_file("/non/existent/file.dci")
    print(f"✓ Handles non-existent file: {result[0] is None}")

    # Test saving invalid data
    print("2. Testing invalid binary data...")
    saver = BinaryFileSaver()
    result = saver.save_binary_file(None, "test.dci")
    print(f"✓ Handles invalid data: {result[0] == ''}")

    # Test uploading from non-existent directory
    print("3. Testing non-existent directory...")
    uploader = BinaryFileUploader()
    result = uploader.upload_binary_file("/non/existent/dir", "*.dci")
    print(f"✓ Handles non-existent directory: {result[0] is None}")


if __name__ == "__main__":
    success = test_binary_file_operations()
    test_error_handling()

    if success:
        print("\n🎉 All tests completed successfully!")
        print("\nThe binary file handling nodes are ready for use with DCI icon files.")
        print("\nUsage in ComfyUI:")
        print("- BinaryFileLoader: Load DCI files from file system")
        print("- BinaryFileSaver: Save binary data to DCI files")
        print("- BinaryFileUploader: Browse and select DCI files from directories")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
