#!/usr/bin/env python3
"""
Test script to verify DCI Preview Node fixes
- Font size parameter removed
- show_file_paths parameter removed
- File paths always shown
"""

import os
import sys
import tempfile
from PIL import Image, ImageDraw
from io import BytesIO

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from nodes import DCIPreviewNode
from dci_format import DCIIconBuilder
from dci_reader import DCIReader


def create_test_image(size=256, color=(255, 0, 0, 255), text="TEST"):
    """Create a test image"""
    image = Image.new('RGBA', (size, size), color)
    draw = ImageDraw.Draw(image)

    # Draw a simple pattern
    draw.rectangle([size//4, size//4, 3*size//4, 3*size//4],
                  fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)

    # Add text
    draw.text((size//2 - 20, size//2 - 5), text, fill=(0, 0, 0, 255))

    return image


def create_test_dci_binary():
    """Create a test DCI file and return its binary data"""
    builder = DCIIconBuilder()

    # Add a few test images
    test_image = create_test_image()

    # Add images with different parameters
    builder.add_icon_image(
        image=test_image,
        size=256,
        state='normal',
        tone='light',
        scale=1,
        format='webp'
    )

    builder.add_icon_image(
        image=test_image,
        size=256,
        state='normal',
        tone='dark',
        scale=2,
        format='png'
    )

    # Build to temporary file
    temp_path = tempfile.mktemp(suffix='.dci')
    builder.build(temp_path)

    # Read binary data
    with open(temp_path, 'rb') as f:
        binary_data = f.read()

    # Clean up
    os.remove(temp_path)

    return binary_data


def test_preview_node_parameters():
    """Test that the preview node has correct parameters"""
    print("Testing DCIPreviewNode parameters...")

    # Check INPUT_TYPES
    input_types = DCIPreviewNode.INPUT_TYPES()

    # Check required parameters
    required = input_types.get('required', {})
    assert 'dci_binary_data' in required, "Missing required parameter: dci_binary_data"

    # Check optional parameters
    optional = input_types.get('optional', {})

    # These should exist
    assert 'grid_columns' in optional, "Missing optional parameter: grid_columns"
    assert 'background_color' in optional, "Missing optional parameter: background_color"
    assert 'custom_bg_r' in optional, "Missing optional parameter: custom_bg_r"
    assert 'custom_bg_g' in optional, "Missing optional parameter: custom_bg_g"
    assert 'custom_bg_b' in optional, "Missing optional parameter: custom_bg_b"

    # These should NOT exist (removed)
    assert 'text_font_size' not in optional, "text_font_size parameter should be removed"
    assert 'show_file_paths' not in optional, "show_file_paths parameter should be removed"

    print("✓ Parameter structure is correct")

    # Check function signature
    import inspect
    sig = inspect.signature(DCIPreviewNode.preview_dci)
    params = list(sig.parameters.keys())

    # Should not have text_font_size or show_file_paths
    assert 'text_font_size' not in params, "text_font_size should not be in function signature"
    assert 'show_file_paths' not in params, "show_file_paths should not be in function signature"

    print("✓ Function signature is correct")


def test_preview_functionality():
    """Test that preview works correctly without the removed parameters"""
    print("\nTesting preview functionality...")

    # Create test DCI binary data
    binary_data = create_test_dci_binary()

    # Create preview node
    node = DCIPreviewNode()

    # Test preview with only required parameters
    result = node.preview_dci(dci_binary_data=binary_data)

    assert 'ui' in result, "Result should have 'ui' key"
    assert 'text' in result['ui'], "UI should have 'text' key"
    assert 'images' in result['ui'], "UI should have 'images' key"

    # Check that text contains file paths
    text_content = result['ui']['text'][0]
    assert '📂 文件路径列表:' in text_content, "File paths section should always be present"
    assert '.webp' in text_content or '.png' in text_content, "File paths should be shown"

    print("✓ Preview functionality works correctly")
    print("✓ File paths are always shown in the output")

    # Test with custom background color
    result2 = node.preview_dci(
        dci_binary_data=binary_data,
        grid_columns=2,
        background_color='dark_gray'
    )

    assert 'ui' in result2, "Result with custom params should work"
    print("✓ Custom parameters work correctly")


def test_text_formatting():
    """Test that text formatting doesn't use HTML"""
    print("\nTesting text formatting...")

    # Create test DCI binary data
    binary_data = create_test_dci_binary()

    # Create preview node
    node = DCIPreviewNode()

    # Get preview result
    result = node.preview_dci(dci_binary_data=binary_data)

    # Check text content
    text_content = result['ui']['text'][0]

    # Should not contain HTML tags
    assert '<span' not in text_content, "Text should not contain HTML span tags"
    assert '</span>' not in text_content, "Text should not contain HTML closing tags"
    assert 'font-size:' not in text_content, "Text should not contain CSS styles"

    print("✓ Text formatting does not use HTML")

    # Check that all expected sections are present
    expected_sections = [
        '📁 DCI 数据源:',
        '🖼️  图像总数:',
        '📊 文件总大小:',
        '📏 图标尺寸:',
        '🎭 图标状态:',
        '🎨 色调类型:',
        '🔍 缩放因子:',
        '🗂️  图像格式:',
        '📂 文件路径列表:',
        '📋 详细图像信息:'
    ]

    for section in expected_sections:
        assert section in text_content, f"Missing section: {section}"

    print("✓ All expected sections are present")


def main():
    """Main test function"""
    print("DCI Preview Node Fix Verification")
    print("=" * 60)

    try:
        # Test parameter structure
        test_preview_node_parameters()

        # Test preview functionality
        test_preview_functionality()

        # Test text formatting
        test_text_formatting()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("\nVerified fixes:")
        print("  ✓ text_font_size parameter removed")
        print("  ✓ show_file_paths parameter removed")
        print("  ✓ File paths always shown in output")
        print("  ✓ Text formatting uses plain text (no HTML)")
        print("  ✓ All functionality works correctly")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
