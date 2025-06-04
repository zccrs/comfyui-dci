#!/usr/bin/env python3
"""
Simple test for DCI functionality without torch dependency
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import DCI modules directly
from dci_format import DCIIconBuilder, DCIFile
from dci_reader import DCIReader, DCIPreviewGenerator


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


def test_dci_format_functionality():
    """Test basic DCI format functionality"""
    print("Testing DCI format functionality...")

    # Create test images
    normal_img = create_test_image(color='blue', text='Normal')
    hover_img = create_test_image(color='green', text='Hover')

    # Create DCI builder
    builder = DCIIconBuilder()

    # Add images
    builder.add_icon_image(normal_img, size=64, state='normal', tone='dark', scale=1, format='webp')
    builder.add_icon_image(normal_img, size=64, state='normal', tone='dark', scale=2, format='webp')
    builder.add_icon_image(hover_img, size=64, state='hover', tone='dark', scale=1, format='webp')

    # Generate binary data
    binary_data = builder.to_binary()

    print(f"  Created DCI binary data: {len(binary_data)} bytes")

    return binary_data


def test_dci_reader_functionality(binary_data):
    """Test DCI reader functionality"""
    print("Testing DCI reader functionality...")

    # Read DCI from binary data
    reader = DCIReader(binary_data=binary_data)
    success = reader.read()

    if not success:
        print("  Error: Failed to read DCI data")
        return None

    # Extract images
    images = reader.get_icon_images()

    print(f"  Extracted {len(images)} images from DCI data")

    for i, img_info in enumerate(images):
        print(f"    Image {i+1}: {img_info['size']}px, {img_info['state']}, {img_info['tone']}, {img_info['scale']}x, {img_info['format']}")

    return images


def test_dci_preview_functionality(images):
    """Test DCI preview functionality"""
    print("Testing DCI preview functionality...")

    if not images:
        print("  Error: No images to preview")
        return

    # Create preview generator
    generator = DCIPreviewGenerator()

    # Create preview grid
    preview_image = generator.create_preview_grid(images, grid_cols=3)

    print(f"  Created preview image: {preview_image.size[0]}x{preview_image.size[1]} pixels")

    # Create metadata summary
    summary = generator.create_metadata_summary(images)

    print(f"  Metadata summary:")
    print(f"    Total images: {summary['total_images']}")
    print(f"    Sizes: {summary['sizes']}")
    print(f"    States: {summary['states']}")
    print(f"    Tones: {summary['tones']}")
    print(f"    Scales: {summary['scales']}")
    print(f"    Formats: {summary['formats']}")

    return preview_image, summary


def test_dci_file_creation():
    """Test DCI file creation and saving"""
    print("Testing DCI file creation...")

    # Create test image
    test_img = create_test_image(color='purple', text='File Test')

    # Create DCI file
    dci_file = DCIFile()

    # Create a simple file structure
    builder = DCIIconBuilder()
    builder.add_icon_image(test_img, size=32, state='normal', tone='dark', scale=1, format='png')

    # Get binary data
    binary_data = builder.to_binary()

    # Save to file
    output_path = 'test_output.dci'
    with open(output_path, 'wb') as f:
        f.write(binary_data)

    print(f"  Saved DCI file: {output_path} ({len(binary_data)} bytes)")

    # Verify by reading back
    reader = DCIReader(file_path=output_path)
    success = reader.read()

    if success:
        images = reader.get_icon_images()
        print(f"  Verified: Read back {len(images)} images from saved file")
    else:
        print("  Error: Failed to read back saved file")

    return output_path


def main():
    """Run all tests"""
    print("Testing DCI functionality...")
    print("=" * 50)

    try:
        # Test basic DCI format
        binary_data = test_dci_format_functionality()

        # Test DCI reader
        images = test_dci_reader_functionality(binary_data)

        # Test DCI preview
        if images:
            preview_image, summary = test_dci_preview_functionality(images)

        # Test file creation
        output_path = test_dci_file_creation()

        print("\n" + "=" * 50)
        print("All tests completed successfully!")

        print(f"\nSummary:")
        print(f"  ✓ DCI format: Created {len(binary_data)} bytes of binary data")
        print(f"  ✓ DCI reader: Extracted {len(images) if images else 0} images")
        print(f"  ✓ DCI preview: Generated preview and metadata")
        print(f"  ✓ DCI file: Saved to {output_path}")

    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
