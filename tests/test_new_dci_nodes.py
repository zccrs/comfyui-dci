#!/usr/bin/env python3
"""
Test script for new DCI nodes: DCIImage, DCIFileNode, and DCIPreviewFromBinary
"""

import os
import sys
import numpy as np
import torch
from PIL import Image, ImageDraw

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nodes import DCIImage, DCIFileNode, DCIPreviewFromBinary


def create_test_image(size=(256, 256), color='red', text='Test'):
    """Create a test image with specified color and text"""
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)

    # Try to use a font, fall back to default if not available
    try:
        from PIL import ImageFont
        font = ImageFont.load_default()
    except:
        font = None

    # Calculate text position (center)
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = len(text) * 6  # Rough estimate
        text_height = 11

    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill='white', font=font)
    return img


def pil_to_tensor(pil_image):
    """Convert PIL Image to ComfyUI tensor format"""
    # Convert to RGB if necessary
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')

    # Convert to numpy array
    img_array = np.array(pil_image)

    # Convert to 0-1 range and add batch dimension
    img_tensor = torch.from_numpy(img_array.astype(np.float32) / 255.0).unsqueeze(0)

    return img_tensor


def test_dci_image_node():
    """Test DCIImage node"""
    print("Testing DCIImage node...")

    # Create test image
    test_img = create_test_image(color='blue', text='Normal')
    test_tensor = pil_to_tensor(test_img)

    # Create DCIImage node
    dci_image_node = DCIImage()

    # Test creating DCI image data
    result = dci_image_node.create_dci_image(
        image=test_tensor,
        icon_size=64,
        icon_state='normal',
        tone_type='dark',
        scale=2,
        image_format='webp'
    )

    dci_image_data = result[0]

    print(f"  Created DCI image data:")
    print(f"    Path: {dci_image_data['path']}")
    print(f"    Size: {dci_image_data['size']}px")
    print(f"    State: {dci_image_data['state']}")
    print(f"    Tone: {dci_image_data['tone']}")
    print(f"    Scale: {dci_image_data['scale']}x")
    print(f"    Format: {dci_image_data['format']}")
    print(f"    Actual size: {dci_image_data['actual_size']}px")
    print(f"    File size: {dci_image_data['file_size']} bytes")

    return dci_image_data


def test_dci_file_node():
    """Test DCIFileNode"""
    print("\nTesting DCIFileNode...")

    # Create multiple test images
    test_images = []

    # Normal state images
    for scale in [1, 2]:
        for tone in ['dark', 'light']:
            color = 'blue' if tone == 'dark' else 'lightblue'
            text = f'N{scale}x'
            test_img = create_test_image(color=color, text=text)
            test_tensor = pil_to_tensor(test_img)

            dci_image_node = DCIImage()
            result = dci_image_node.create_dci_image(
                image=test_tensor,
                icon_size=64,
                icon_state='normal',
                tone_type=tone,
                scale=scale,
                image_format='webp'
            )
            test_images.append(result[0])

    # Hover state image
    hover_img = create_test_image(color='green', text='Hover')
    hover_tensor = pil_to_tensor(hover_img)
    dci_image_node = DCIImage()
    result = dci_image_node.create_dci_image(
        image=hover_tensor,
        icon_size=64,
        icon_state='hover',
        tone_type='dark',
        scale=1,
        image_format='webp'
    )
    test_images.append(result[0])

    # Create DCIFileNode
    dci_file_node = DCIFileNode()

    # Prepare kwargs for multiple images
    kwargs = {}
    for i, img_data in enumerate(test_images, 1):
        kwargs[f'dci_image_{i}'] = img_data

    # Test creating DCI file
    result = dci_file_node.create_dci_file(
        filename='test_icon',
        save_to_file=True,
        output_directory='',
        **kwargs
    )

    binary_data, file_path = result

    print(f"  Created DCI file:")
    print(f"    Binary data size: {len(binary_data)} bytes")
    print(f"    File path: {file_path}")
    print(f"    Number of images: {len(test_images)}")

    return binary_data


def test_dci_preview_from_binary():
    """Test DCIPreviewFromBinary node"""
    print("\nTesting DCIPreviewFromBinary node...")

    # First create a DCI file
    binary_data = test_dci_file_node()

    if not binary_data:
        print("  Error: No binary data to preview")
        return

    # Create DCIPreviewFromBinary node
    preview_node = DCIPreviewFromBinary()

    # Test previewing DCI binary data
    result = preview_node.preview_dci_binary(
        dci_binary_data=binary_data,
        grid_columns=3,
        show_metadata=True
    )

    preview_tensor, metadata_summary = result

    print(f"  Created preview:")
    print(f"    Preview tensor shape: {preview_tensor.shape}")
    print(f"    Metadata summary length: {len(metadata_summary)} characters")
    print(f"  Metadata summary:")
    print("    " + "\n    ".join(metadata_summary.split('\n')[:10]))  # First 10 lines

    return preview_tensor, metadata_summary


def main():
    """Run all tests"""
    print("Testing new DCI nodes...")
    print("=" * 50)

    try:
        # Test individual components
        dci_image_data = test_dci_image_node()
        binary_data = test_dci_file_node()
        preview_result = test_dci_preview_from_binary()

        print("\n" + "=" * 50)
        print("All tests completed successfully!")

        # Summary
        print(f"\nSummary:")
        print(f"  ✓ DCIImage node: Created image data with path '{dci_image_data['path']}'")
        print(f"  ✓ DCIFileNode: Created {len(binary_data)} bytes of DCI data")
        print(f"  ✓ DCIPreviewFromBinary: Generated preview with shape {preview_result[0].shape}")

    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
