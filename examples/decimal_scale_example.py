#!/usr/bin/env python3
"""
DCI Image Decimal Scale Example

This example demonstrates how to use decimal scale factors in DCI images,
such as 1.25x for high-DPI displays.
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Add the py directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from dci_format import create_dci_icon


def create_sample_icon(size=(256, 256), text="DCI", color='blue'):
    """Create a sample icon with text"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a colored circle
    margin = size[0] // 8
    circle_bbox = [margin, margin, size[0] - margin, size[1] - margin]

    if color == 'blue':
        fill_color = (70, 130, 180, 255)
    elif color == 'green':
        fill_color = (60, 179, 113, 255)
    elif color == 'red':
        fill_color = (220, 20, 60, 255)
    else:
        fill_color = (128, 128, 128, 255)

    draw.ellipse(circle_bbox, fill=fill_color)

    # Add text
    try:
        font_size = size[0] // 6
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill='white', font=font)

    return img


def main():
    """Create DCI icons with decimal scale factors"""
    print("Creating DCI icons with decimal scale factors...")
    print("=" * 60)

    # Create sample icon
    base_icon = create_sample_icon(text="1.25x", color='blue')

    # Example 1: Standard scales (integer)
    print("1. Creating DCI with standard integer scales...")
    create_dci_icon(
        image=base_icon,
        output_path='example_standard_scales.dci',
        size=64,
        states=['normal', 'hover'],
        tones=['dark', 'light'],
        scales=[1, 2, 3],  # Integer scales
        format='webp'
    )
    print("   ✓ Created: example_standard_scales.dci")

    # Example 2: Decimal scales for high-DPI displays
    print("\n2. Creating DCI with decimal scales for high-DPI...")
    create_dci_icon(
        image=base_icon,
        output_path='example_decimal_scales.dci',
        size=64,
        states=['normal', 'hover', 'pressed'],
        tones=['dark'],
        scales=[1.0, 1.25, 1.5, 2.0, 2.5],  # Decimal scales
        format='webp'
    )
    print("   ✓ Created: example_decimal_scales.dci")

    # Example 3: Mixed scales for comprehensive support
    print("\n3. Creating DCI with mixed scales...")
    create_dci_icon(
        image=base_icon,
        output_path='example_mixed_scales.dci',
        size=128,
        states=['normal', 'disabled'],
        tones=['dark', 'light'],
        scales=[1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0],  # Comprehensive scales
        format='png'
    )
    print("   ✓ Created: example_mixed_scales.dci")

    # Show file sizes
    print("\n" + "=" * 60)
    print("Generated files:")

    files = [
        'example_standard_scales.dci',
        'example_decimal_scales.dci',
        'example_mixed_scales.dci'
    ]

    for filename in files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  {filename}: {size:,} bytes")
        else:
            print(f"  {filename}: Not found")

    print("\n" + "=" * 60)
    print("Decimal scale benefits:")
    print("  • 1.25x: Perfect for 125% display scaling")
    print("  • 1.5x:  Ideal for 150% display scaling")
    print("  • 1.75x: Good for 175% display scaling")
    print("  • 2.5x:  Excellent for ultra-high DPI displays")
    print("\nThese decimal scales provide smoother scaling transitions")
    print("and better visual quality on high-DPI displays.")


if __name__ == "__main__":
    main()
