#!/usr/bin/env python3
"""
Simple verification script for DCI Preview Node fixes
No torch dependency required
只移除show_file_paths参数，保留text_font_size参数
"""

import os
import sys
import re

# Path to nodes.py
nodes_file = os.path.join(os.path.dirname(__file__), '..', 'py', 'nodes.py')

def verify_parameters_updated():
    """Verify that show_file_paths is removed but text_font_size remains"""
    print("Verifying parameter updates...")

    # Simply read the first 40 lines which should contain the INPUT_TYPES method
    with open(nodes_file, 'r', encoding='utf-8') as f:
        first_lines = ''.join([f.readline() for _ in range(40)])

    # Check for text_font_size
    if 'text_font_size' not in first_lines:
        print("❌ text_font_size parameter not found in first 40 lines")
        return False

    # Check for show_file_paths - should not exist
    if 'show_file_paths' in first_lines:
        print("❌ show_file_paths parameter still exists in first 40 lines")
        return False

    print("✓ Parameters correctly updated (text_font_size kept, show_file_paths removed)")
    return True


def verify_format_method():
    """Verify that _format_detailed_summary method is updated"""
    print("\nVerifying _format_detailed_summary method...")

    with open(nodes_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check function signature
    if 'def _format_detailed_summary(self, images, source_name, text_font_size=' not in content:
        print("❌ _format_detailed_summary method signature incorrect")
        return False

    # Verify adaptive formatting based on font size
    if 'if text_font_size' in content or 'text_font_size <=' in content:
        print("✓ Adaptive formatting based on font size found")
    else:
        print("❌ No adaptive formatting based on font size")
        return False

    # Verify no HTML formatting
    if '<span' in content or '</span>' in content:
        print("❌ HTML formatting still present")
        return False

    # Verify file paths section always shown
    if 'if show_file_paths' in content:
        print("❌ Conditional file path display still present")
        return False

    print("✓ _format_detailed_summary method correctly updated")
    return True


def verify_file_paths_always_shown():
    """Verify that file paths are always shown"""
    print("\nVerifying file paths are always shown...")

    with open(nodes_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for file paths section
    if '📂 文件路径列表' not in content:
        print("❌ File paths section not found")
        return False

    # Check that the file paths section is not conditionally displayed
    if 'if show_file_paths' in content:
        print("❌ File paths still conditionally displayed")
        return False

    print("✓ File paths section is always included")
    return True


def main():
    """Main verification function"""
    print("DCI Preview Node Fix Verification (No Dependencies)")
    print("=" * 60)

    if not os.path.exists(nodes_file):
        print(f"❌ Could not find nodes.py at: {nodes_file}")
        return 1

    all_passed = True

    # Run verifications
    if not verify_parameters_updated():
        all_passed = False

    if not verify_format_method():
        all_passed = False

    if not verify_file_paths_always_shown():
        all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("✅ All verifications passed!")
        print("\nConfirmed fixes:")
        print("  ✓ show_file_paths parameter removed from INPUT_TYPES")
        print("  ✓ text_font_size parameter retained and properly used")
        print("  ✓ HTML formatting removed from text output")
        print("  ✓ Adaptive text formatting based on font size")
        print("  ✓ File paths always shown (no conditional display)")
        return 0
    else:
        print("❌ Some verifications failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
