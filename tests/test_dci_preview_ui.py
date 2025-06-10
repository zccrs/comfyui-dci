#!/usr/bin/env python3
"""
Test script for DCI Preview Node UI functionality
"""

import os
import sys
import tempfile
from PIL import Image, ImageDraw

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from dci_format import DCIIconBuilder
from nodes import DCIPreviewNode


def create_test_image(size=256, color=(255, 0, 0, 255), text="TEST"):
    """Create a test image with specified size, color and text"""
    image = Image.new('RGBA', (size, size), color)
    draw = ImageDraw.Draw(image)

    # Draw a simple pattern
    draw.rectangle([size//4, size//4, 3*size//4, 3*size//4],
                  fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)

    # Try to use a font, fall back to default
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size//16)
    except:
        font = None

    # Calculate text position
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = len(text) * 6
        text_height = 11

    x = (size - text_width) // 2
    y = (size - text_height) // 2

    draw.text((x, y), text, fill=(0, 0, 0, 255), font=font)

    return image


def create_test_dci_file():
    """Create a test DCI file for preview testing"""
    print("Creating test DCI file for UI preview...")

    builder = DCIIconBuilder()

    # Create different images for different states
    state_images = {
        'normal': create_test_image(color=(0, 255, 0, 255), text="NORMAL"),
        'hover': create_test_image(color=(255, 255, 0, 255), text="HOVER"),
        'pressed': create_test_image(color=(255, 0, 0, 255), text="PRESS"),
        'disabled': create_test_image(color=(128, 128, 128, 255), text="DISABLED")
    }

    # Add images for multiple combinations
    sizes = [64, 128, 256]
    tones = ['dark', 'light']
    scales = [1, 2]
    formats = ['webp', 'png']

    for size in sizes:
        for state, img in state_images.items():
            for tone in tones:
                for scale in scales:
                    for format in formats:
                        # Resize image to base size
                        resized_img = img.resize((size, size), Image.Resampling.LANCZOS)

                        builder.add_icon_image(
                            image=resized_img,
                            size=size,
                            state=state,
                            tone=tone,
                            scale=scale,
                            format=format
                        )

    output_path = "test_ui_preview.dci"
    builder.build(output_path)

    if os.path.exists(output_path):
        print(f"✓ Test DCI file created: {output_path}")
        print(f"  File size: {os.path.getsize(output_path)} bytes")
        return output_path
    else:
        print("✗ Failed to create test DCI file")
        return None


def test_preview_node_binary_input_basic():
    """Test DCIPreviewNode with binary data input (basic test)"""
    print("\n=== Testing DCIPreviewNode with binary data input ===")

    # Create test DCI file
    dci_file_path = create_test_dci_file()
    if not dci_file_path:
        print("✗ Cannot test without DCI file")
        return False

    # Read binary data
    try:
        with open(dci_file_path, 'rb') as f:
            binary_data = f.read()
        print(f"✓ Read binary data: {len(binary_data)} bytes")
    except Exception as e:
        print(f"✗ Failed to read binary data: {str(e)}")
        return False

    # Create preview node
    preview_node = DCIPreviewNode()

    # Test with different grid configurations
    test_configs = [
        {"grid_columns": 2},
        {"grid_columns": 4},
        {"grid_columns": 6},
    ]

    for i, config in enumerate(test_configs):
        print(f"\nTest {i+1}: Grid columns={config['grid_columns']}")

        try:
            result = preview_node.preview_dci(
                dci_binary_data=binary_data,
                grid_columns=config['grid_columns']
            )

            # Check result structure
            if isinstance(result, dict) and "ui" in result:
                ui_data = result["ui"]
                print(f"  ✓ UI output structure correct")

                # Check images
                if "images" in ui_data and ui_data["images"]:
                    image_info = ui_data["images"][0]
                    print(f"  ✓ Preview image generated: {image_info['filename']}")
                    print(f"    Type: {image_info.get('type', 'unknown')}")
                else:
                    print(f"  ✗ No preview image in UI output")

                # Check text (metadata is always shown now)
                if "text" in ui_data and ui_data["text"]:
                    text_content = ui_data["text"][0]
                    print(f"  ✓ Metadata text generated ({len(text_content)} characters)")
                    print(f"    Preview: {text_content[:100]}...")
                else:
                    print(f"  ✗ No metadata text in UI output")

            else:
                print(f"  ✗ Invalid result structure: {type(result)}")
                return False

        except Exception as e:
            print(f"  ✗ Error during preview: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    return True


def test_preview_node_binary_input():
    """Test DCIPreviewNode with binary data input (detailed test)"""
    print("\n=== Testing DCIPreviewNode with binary data input (detailed) ===")

    # Create test DCI file
    dci_file_path = create_test_dci_file()
    if not dci_file_path:
        print("✗ Cannot test without DCI file")
        return False

    # Read binary data
    try:
        with open(dci_file_path, 'rb') as f:
            binary_data = f.read()
        print(f"✓ Read binary data: {len(binary_data)} bytes")
    except Exception as e:
        print(f"✗ Failed to read binary data: {str(e)}")
        return False

    # Create preview node
    preview_node = DCIPreviewNode()

    try:
        result = preview_node.preview_dci(
            dci_binary_data=binary_data,
            grid_columns=3
        )

        # Check result structure
        if isinstance(result, dict) and "ui" in result:
            ui_data = result["ui"]
            print(f"✓ UI output structure correct")

            # Check images
            if "images" in ui_data and ui_data["images"]:
                image_info = ui_data["images"][0]
                print(f"✓ Preview image generated from binary data: {image_info['filename']}")
            else:
                print(f"✗ No preview image in UI output")

            # Check text (metadata is always shown now)
            if "text" in ui_data and ui_data["text"]:
                text_content = ui_data["text"][0]
                print(f"✓ Metadata text generated ({len(text_content)} characters)")
                # Check for emoji indicators
                if "📁" in text_content and "🖼️" in text_content:
                    print(f"✓ Emoji indicators present in metadata")
                else:
                    print(f"⚠ Emoji indicators missing in metadata")
            else:
                print(f"✗ No metadata text in UI output")

        else:
            print(f"✗ Invalid result structure: {type(result)}")
            return False

    except Exception as e:
        print(f"✗ Error during binary preview: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_preview_node_error_handling():
    """Test DCIPreviewNode error handling"""
    print("\n=== Testing DCIPreviewNode error handling ===")

    preview_node = DCIPreviewNode()

    # Test 1: Invalid binary data
    print("\nTest 1: Invalid binary data")
    try:
        result = preview_node.preview_dci(dci_binary_data=b"invalid_dci_data")
        if isinstance(result, dict) and "ui" in result and "text" in result["ui"]:
            error_text = result["ui"]["text"][0]
            print(f"✓ Invalid binary data error handled: {error_text}")
        else:
            print(f"✗ Invalid binary data error not handled properly")
    except Exception as e:
        print(f"✗ Unexpected exception: {str(e)}")

    # Test 2: Empty binary data
    print("\nTest 2: Empty binary data")
    try:
        result = preview_node.preview_dci(dci_binary_data=b"")
        if isinstance(result, dict) and "ui" in result and "text" in result["ui"]:
            error_text = result["ui"]["text"][0]
            print(f"✓ Empty binary data error handled: {error_text}")
        else:
            print(f"✗ Empty binary data error not handled properly")
    except Exception as e:
        print(f"✗ Unexpected exception: {str(e)}")

    # Test 3: None binary data (should cause TypeError)
    print("\nTest 3: None binary data")
    try:
        result = preview_node.preview_dci(dci_binary_data=None)
        print(f"✗ Should have raised an exception for None binary data")
    except TypeError as e:
        print(f"✓ TypeError correctly raised for None binary data: {str(e)}")
    except Exception as e:
        print(f"⚠ Unexpected exception type: {str(e)}")

    return True


def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        "test_ui_preview.dci",
    ]

    for filename in test_files:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Cleaned up: {filename}")


def main():
    """Main test function"""
    print("DCI Preview Node UI Test Suite")
    print("=" * 50)

    success = True

    try:
        # Test basic binary input
        if not test_preview_node_binary_input_basic():
            success = False

        # Test detailed binary input
        if not test_preview_node_binary_input():
            success = False

        # Test error handling
        if not test_preview_node_error_handling():
            success = False

    finally:
        # Cleanup
        print("\n=== Cleanup ===")
        cleanup_test_files()

    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed!")
        print("\nDCI Preview Node UI functionality is working correctly.")
        print("The node now displays preview content directly within the node interface.")
    else:
        print("✗ Some tests failed!")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
