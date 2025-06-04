#!/usr/bin/env python3
"""
Test script for DCI preview functionality
"""

import os
import sys
from PIL import Image, ImageDraw
from dci_format import create_dci_icon, DCIIconBuilder
from dci_reader import DCIReader, DCIPreviewGenerator


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
    """Create a comprehensive test DCI file"""
    print("Creating test DCI file...")

    builder = DCIIconBuilder()

    # Create different images for different states
    state_images = {
        'normal': create_test_image(color=(0, 255, 0, 255), text="NORMAL"),
        'hover': create_test_image(color=(255, 255, 0, 255), text="HOVER"),
        'pressed': create_test_image(color=(255, 0, 0, 255), text="PRESS"),
        'disabled': create_test_image(color=(128, 128, 128, 255), text="DISABLED")
    }

    # Add images for multiple combinations
    sizes = [128, 256]
    tones = ['light', 'dark']
    scales = [1, 2, 3]
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

    output_path = "test_comprehensive.dci"
    builder.build(output_path)

    if os.path.exists(output_path):
        print(f"✓ Comprehensive test DCI file created: {output_path}")
        print(f"  File size: {os.path.getsize(output_path)} bytes")
        return output_path
    else:
        print("✗ Failed to create comprehensive test DCI file")
        return None


def test_dci_reader(dci_file_path):
    """Test DCI file reading"""
    print(f"\nTesting DCI reader with: {dci_file_path}")

    reader = DCIReader(dci_file_path)
    if not reader.read():
        print("✗ Failed to read DCI file")
        return None

    print(f"✓ DCI file read successfully")
    print(f"  Found {len(reader.files)} top-level entries")
    print(f"  Directory structure has {len(reader.directory_structure)} directories")

    # Extract images
    images = reader.get_icon_images()
    print(f"  Extracted {len(images)} images")

    if images:
        # Show some sample metadata
        sample = images[0]
        print(f"  Sample image metadata:")
        print(f"    Size: {sample['size']}px")
        print(f"    State: {sample['state']}")
        print(f"    Tone: {sample['tone']}")
        print(f"    Scale: {sample['scale']}x")
        print(f"    Format: {sample['format']}")
        print(f"    Path: {sample['path']}")
        print(f"    File size: {sample['file_size']} bytes")
        print(f"    Image dimensions: {sample['image'].size}")

    return images


def test_preview_generator(images):
    """Test preview generation"""
    print(f"\nTesting preview generator with {len(images)} images...")

    generator = DCIPreviewGenerator()

    # Test different grid sizes
    grid_sizes = [2, 4, 6]

    for grid_cols in grid_sizes:
        print(f"  Generating {grid_cols}-column preview...")

        preview_image = generator.create_preview_grid(images, grid_cols)
        output_path = f"preview_grid_{grid_cols}col.png"

        preview_image.save(output_path)
        print(f"    ✓ Saved preview: {output_path} ({preview_image.size[0]}x{preview_image.size[1]})")

    # Test metadata summary
    summary = generator.create_metadata_summary(images)
    print(f"\n  Metadata Summary:")
    print(f"    Total images: {summary['total_images']}")
    print(f"    Sizes: {summary['sizes']}")
    print(f"    States: {summary['states']}")
    print(f"    Tones: {summary['tones']}")
    print(f"    Scales: {summary['scales']}")
    print(f"    Formats: {summary['formats']}")
    print(f"    Total file size: {summary['total_file_size']} bytes")


def test_directory_structure_parsing(dci_file_path):
    """Test directory structure parsing"""
    print(f"\nTesting directory structure parsing...")

    reader = DCIReader(dci_file_path)
    reader.read()

    print("Directory structure:")
    for dir_path, files in reader.directory_structure.items():
        print(f"  {dir_path}/")
        for filename, file_info in files.items():
            print(f"    {filename} ({file_info['size']} bytes)")


def test_filtering():
    """Test image filtering functionality"""
    print(f"\nTesting filtering functionality...")

    # This would be used by the DCIMetadataExtractor node
    # For now, just demonstrate the concept

    dci_file_path = "test_comprehensive.dci"
    if not os.path.exists(dci_file_path):
        print("No test DCI file found for filtering test")
        return

    reader = DCIReader(dci_file_path)
    reader.read()
    images = reader.get_icon_images()

    # Test state filtering
    normal_images = [img for img in images if img['state'] == 'normal']
    print(f"  Normal state images: {len(normal_images)}")

    # Test tone filtering
    dark_images = [img for img in images if img['tone'] == 'dark']
    print(f"  Dark tone images: {len(dark_images)}")

    # Test scale filtering
    scale_1x_images = [img for img in images if img['scale'] == 1]
    print(f"  1x scale images: {len(scale_1x_images)}")

    # Test format filtering
    webp_images = [img for img in images if img['format'] == 'webp']
    print(f"  WebP format images: {len(webp_images)}")


def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        "test_comprehensive.dci",
        "preview_grid_2col.png",
        "preview_grid_4col.png",
        "preview_grid_6col.png"
    ]

    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Cleaned up: {file}")


if __name__ == "__main__":
    print("DCI Preview Functionality Test Suite")
    print("=" * 60)

    try:
        # Create test DCI file
        dci_file_path = create_test_dci_file()
        if not dci_file_path:
            sys.exit(1)

        # Test reading
        images = test_dci_reader(dci_file_path)
        if not images:
            sys.exit(1)

        # Test preview generation
        test_preview_generator(images)

        # Test directory structure parsing
        test_directory_structure_parsing(dci_file_path)

        # Test filtering
        test_filtering()

        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("\nGenerated files:")
        print("- test_comprehensive.dci (test DCI file)")
        print("- preview_grid_*col.png (preview images)")

        # Ask if user wants to clean up
        response = input("\nClean up test files? (y/N): ").strip().lower()
        if response == 'y':
            cleanup_test_files()

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
