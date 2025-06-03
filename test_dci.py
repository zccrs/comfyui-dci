#!/usr/bin/env python3
"""
Test script for DCI format implementation
"""

import os
import sys
from PIL import Image, ImageDraw
from dci_format import create_dci_icon, DCIIconBuilder


def create_test_image(size=256, color=(255, 0, 0, 255)):
    """Create a test image with specified size and color"""
    image = Image.new('RGBA', (size, size), color)
    draw = ImageDraw.Draw(image)

    # Draw a simple pattern
    draw.rectangle([size//4, size//4, 3*size//4, 3*size//4],
                  fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    draw.text((size//2-20, size//2-10), "TEST", fill=(0, 0, 0, 255))

    return image


def test_basic_dci():
    """Test basic DCI creation"""
    print("Testing basic DCI creation...")

    # Create test image
    test_img = create_test_image()

    # Create DCI file
    output_path = "test_basic.dci"
    create_dci_icon(
        image=test_img,
        output_path=output_path,
        size=256,
        states=['normal'],
        tones=['dark'],
        scales=[1, 2, 3],
        format='webp'
    )

    if os.path.exists(output_path):
        print(f"✓ Basic DCI file created: {output_path}")
        print(f"  File size: {os.path.getsize(output_path)} bytes")
    else:
        print("✗ Failed to create basic DCI file")


def test_advanced_dci():
    """Test advanced DCI creation with multiple states"""
    print("\nTesting advanced DCI creation...")

    # Create different images for different states
    normal_img = create_test_image(color=(0, 255, 0, 255))  # Green
    hover_img = create_test_image(color=(255, 255, 0, 255))  # Yellow
    pressed_img = create_test_image(color=(255, 0, 0, 255))  # Red

    builder = DCIIconBuilder()

    # Add images for different states and tones
    states_images = {
        'normal': normal_img,
        'hover': hover_img,
        'pressed': pressed_img
    }

    tones = ['light', 'dark']
    scales = [1, 2, 3]

    for state, img in states_images.items():
        for tone in tones:
            for scale in scales:
                builder.add_icon_image(
                    image=img,
                    size=256,
                    state=state,
                    tone=tone,
                    scale=scale,
                    format='webp'
                )

    output_path = "test_advanced.dci"
    builder.build(output_path)

    if os.path.exists(output_path):
        print(f"✓ Advanced DCI file created: {output_path}")
        print(f"  File size: {os.path.getsize(output_path)} bytes")
    else:
        print("✗ Failed to create advanced DCI file")


def test_different_formats():
    """Test different image formats"""
    print("\nTesting different image formats...")

    test_img = create_test_image()
    formats = ['webp', 'png', 'jpg']

    for fmt in formats:
        output_path = f"test_{fmt}.dci"
        try:
            create_dci_icon(
                image=test_img,
                output_path=output_path,
                size=128,
                format=fmt
            )

            if os.path.exists(output_path):
                print(f"✓ {fmt.upper()} format DCI created: {output_path}")
                print(f"  File size: {os.path.getsize(output_path)} bytes")
            else:
                print(f"✗ Failed to create {fmt.upper()} format DCI")

        except Exception as e:
            print(f"✗ Error creating {fmt.upper()} format DCI: {e}")


def inspect_dci_file(filepath):
    """Inspect DCI file structure"""
    print(f"\nInspecting DCI file: {filepath}")

    if not os.path.exists(filepath):
        print("File does not exist")
        return

    with open(filepath, 'rb') as f:
        # Read header
        magic = f.read(4)
        version = f.read(1)[0]
        file_count_bytes = f.read(3)
        file_count = int.from_bytes(file_count_bytes + b'\x00', 'little')

        print(f"Magic: {magic}")
        print(f"Version: {version}")
        print(f"File count: {file_count}")

        # Read file entries
        for i in range(file_count):
            file_type = f.read(1)[0]
            file_name = f.read(63).rstrip(b'\x00').decode('utf-8')
            content_size = int.from_bytes(f.read(8), 'little')

            print(f"  File {i+1}:")
            print(f"    Type: {file_type} ({'Directory' if file_type == 2 else 'File'})")
            print(f"    Name: {file_name}")
            print(f"    Size: {content_size} bytes")

            # Skip content
            f.seek(content_size, 1)


if __name__ == "__main__":
    print("DCI Format Test Suite")
    print("=" * 50)

    try:
        # Run tests
        test_basic_dci()
        test_advanced_dci()
        test_different_formats()

        # Inspect created files
        for filename in ["test_basic.dci", "test_advanced.dci", "test_webp.dci"]:
            if os.path.exists(filename):
                inspect_dci_file(filename)

        print("\n" + "=" * 50)
        print("Test suite completed!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
