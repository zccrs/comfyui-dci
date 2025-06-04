#!/usr/bin/env python3
"""
Test script to verify that DCI nodes can be loaded correctly.
This script simulates how ComfyUI would load the nodes.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_node_loading():
    """Test if nodes can be loaded without errors"""
    try:
        # Test importing the nodes module directly
        print("Testing nodes.py import...")
        import nodes as dci_nodes

        print(f"✓ Successfully imported nodes.py")
        print(f"✓ Found {len(dci_nodes.NODE_CLASS_MAPPINGS)} node classes")
        print(f"✓ Found {len(dci_nodes.NODE_DISPLAY_NAME_MAPPINGS)} display names")

        # Test that all mappings are consistent
        class_keys = set(dci_nodes.NODE_CLASS_MAPPINGS.keys())
        display_keys = set(dci_nodes.NODE_DISPLAY_NAME_MAPPINGS.keys())

        if class_keys == display_keys:
            print("✓ Node class mappings and display name mappings are consistent")
        else:
            print("✗ Mismatch between class mappings and display name mappings")
            print(f"  Class keys: {class_keys}")
            print(f"  Display keys: {display_keys}")
            return False

        # Test that all node classes have required attributes
        print("\nTesting node class attributes...")
        for node_name, node_class in dci_nodes.NODE_CLASS_MAPPINGS.items():
            print(f"  Testing {node_name}...")

            # Check required class methods
            if not hasattr(node_class, 'INPUT_TYPES'):
                print(f"    ✗ Missing INPUT_TYPES method")
                return False

            if not hasattr(node_class, 'RETURN_TYPES'):
                print(f"    ✗ Missing RETURN_TYPES attribute")
                return False

            if not hasattr(node_class, 'FUNCTION'):
                print(f"    ✗ Missing FUNCTION attribute")
                return False

            if not hasattr(node_class, 'CATEGORY'):
                print(f"    ✗ Missing CATEGORY attribute")
                return False

            # Check that CATEGORY starts with "DCI/"
            if not node_class.CATEGORY.startswith("DCI/"):
                print(f"    ✗ Wrong category: {node_class.CATEGORY}, expected to start with 'DCI/'")
                return False

            print(f"    ✓ {node_name} has all required attributes")

        print("\n✓ All nodes passed validation!")
        print("\nNode categories:")
        categories = {}
        for node_name, node_class in dci_nodes.NODE_CLASS_MAPPINGS.items():
            category = node_class.CATEGORY
            if category not in categories:
                categories[category] = []
            categories[category].append(node_name)

        for category, nodes in sorted(categories.items()):
            print(f"  {category}:")
            for node in nodes:
                print(f"    - {node}")

        return True

    except Exception as e:
        print(f"✗ Error loading nodes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("DCI Node Loading Test")
    print("=" * 50)

    success = test_node_loading()

    if success:
        print("\n🎉 All tests passed! Nodes should be visible in ComfyUI under the 'DCI' category with subcategories.")
    else:
        print("\n❌ Tests failed! There are issues that need to be fixed.")

    sys.exit(0 if success else 1)
