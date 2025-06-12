#!/usr/bin/env python3
"""
Test script to verify node categories are properly translated
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_node_categories():
    """Test node categories"""
    try:
        from __init__ import NODE_CLASS_MAPPINGS

        print("Node categories:")
        categories = {}

        for node_name, node_class in NODE_CLASS_MAPPINGS.items():
            category = node_class.CATEGORY
            print(f"  {node_name}: {category}")

            # Group by category
            if category not in categories:
                categories[category] = []
            categories[category].append(node_name)

        print("\nGrouped by category:")
        for category, nodes in categories.items():
            print(f"  {category}:")
            for node in nodes:
                print(f"    - {node}")

        # Check for mixed language categories
        print("\nChecking for translation issues:")
        mixed_categories = []
        for category in categories.keys():
            if "DCI/" in category:
                subcategory = category.split("/", 1)[1]
                # Check if subcategory contains English words
                english_words = ["Export", "Preview", "Analysis", "Files"]
                if subcategory in english_words:
                    mixed_categories.append(category)

        if mixed_categories:
            print("❌ Found untranslated categories:")
            for cat in mixed_categories:
                print(f"    {cat}")
        else:
            print("✅ All categories are properly translated")

        return len(mixed_categories) == 0

    except Exception as e:
        print(f"Error testing node categories: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_node_categories()
    sys.exit(0 if success else 1)
