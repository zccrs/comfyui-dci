#!/usr/bin/env python3
"""
Test for Binary File Loader direct binary output (without ComfyUI dependencies)
"""

import os
import tempfile
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_binary_loader_direct_output():
    """Test that BinaryFileLoader now outputs binary data directly"""

    print("Testing Binary File Loader Direct Output")
    print("=" * 45)

    # Create test binary data (simulating the URL content from your example)
    test_url = b"https://software.download.prss.microsoft.com/dbazure/Win10_22H2_Chinese_Simplified_x64v1.iso?t=718c01b0-4a37-4736-a6fb-8a4a3bff36d2&P1=1718451384&P2=601&P3=2&P4=piSBQL3mTSfOK0GUSkjY%2bg5wJL0AUFe3pja1WfyZEuHwPp5MrHuEWDhP%2fJz284EmFvMMR%2bLzdWNLU8Y9cCvEnupwJeIWlsEr%2fRjTaa9B17Cqbex9ObyNk1XM3baDWpMPhqWrbBw0vuYomiuofiN3enJuxnSSOmF9Tc1tyY4VpAp%2frq29eytd0VzMkjWXbbV1FQ7NFYJ0lwvaQFymOR0I1ZdQpa9du%2bmvuNgPItiG%2fKHVVBk%2fDhg2%2fMjhMWH84noxksk8lRLlPOq9qFxO3g3bTGB0Im7F%2bH4PWbs9ap5JMSTw6RZdexdiFRVBCozNpjiarFQuwJo%2bmNUxUZIXricwjA%3d%3d"

    # Create temporary test file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(test_url)
        temp_file_path = temp_file.name

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

        # Test the loader
        loader = BinaryFileLoader()
        result = loader.load_binary_file(temp_file_path)

        if result[0] is not None:
            binary_data, file_path = result

            print(f"✓ Loaded file: {os.path.basename(file_path)}")
            print(f"✓ File size: {len(binary_data)} bytes")
            print(f"✓ Content type: {type(binary_data)}")
            print(f"✓ Content matches: {binary_data == test_url}")

            # Verify it's direct binary data, not a dictionary
            if isinstance(binary_data, bytes):
                print("✓ Output is direct binary data (bytes)")
            else:
                print(f"✗ Output is not direct binary data, got: {type(binary_data)}")
                return False

            # Verify the content is exactly what we expect
            if binary_data == test_url:
                print("✓ Binary content matches expected data exactly")
            else:
                print("✗ Binary content does not match expected data")
                return False

            # Show a preview of the content (first 100 characters)
            content_preview = binary_data.decode('utf-8')[:100]
            print(f"✓ Content preview: {content_preview}...")

            return True

        else:
            print("✗ Failed to load binary file")
            return False

    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        try:
            os.unlink(temp_file_path)
        except:
            pass


def test_expected_vs_old_behavior():
    """Demonstrate the difference between old and new behavior"""

    print("\n\nBehavior Comparison")
    print("=" * 30)

    print("OLD BEHAVIOR (before fix):")
    print("binary_data = {")
    print("    'content': b'https://software.download...',")
    print("    'filename': '新建 文本文档.txt',")
    print("    'size': 531,")
    print("    'source_path': 'C:\\\\Users\\\\...'")
    print("}")
    print("# User had to access: binary_data['content']")

    print("\nNEW BEHAVIOR (after fix):")
    print("binary_data = b'https://software.download...'")
    print("# User can use binary_data directly!")

    print("\n✅ The Binary File Loader now outputs binary data directly")
    print("✅ No need to access ['content'] key anymore")
    print("✅ Simpler and more intuitive interface")


if __name__ == "__main__":
    success = test_binary_loader_direct_output()
    test_expected_vs_old_behavior()

    if success:
        print("\n🎉 Binary File Loader direct output test passed!")
        print("The loader now outputs binary data directly as requested.")
    else:
        print("\n❌ Binary File Loader direct output test failed!")
        sys.exit(1)
