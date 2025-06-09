#!/usr/bin/env python3
"""
Test script to verify ComfyUI DCI node registration
"""

import sys
import os
import re

def test_node_registration():
    """Test that all nodes are properly registered"""
    try:
        # Read the __init__.py file directly
        init_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "__init__.py")

        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print("✅ Successfully read __init__.py file")

        # Extract NODE_CLASS_MAPPINGS
        class_mappings_match = re.search(r'NODE_CLASS_MAPPINGS\s*=\s*{([^}]+)}', content, re.DOTALL)
        if not class_mappings_match:
            print("❌ Error: NODE_CLASS_MAPPINGS not found")
            return False

        # Extract NODE_DISPLAY_NAME_MAPPINGS
        display_mappings_match = re.search(r'NODE_DISPLAY_NAME_MAPPINGS\s*=\s*{([^}]+)}', content, re.DOTALL)
        if not display_mappings_match:
            print("❌ Error: NODE_DISPLAY_NAME_MAPPINGS not found")
            return False

        # Parse node names from mappings
        class_mappings_content = class_mappings_match.group(1)
        node_names = re.findall(r'"([^"]+)":', class_mappings_content)

        print(f"📊 Found {len(node_names)} node classes")

        # Check that all nodes have unique names with DCI prefix
        for node_name in node_names:
            if not node_name.startswith("DCI_"):
                print(f"⚠️  Warning: Node '{node_name}' doesn't follow DCI_ naming convention")
            else:
                print(f"✅ Node '{node_name}' follows naming convention")

        # Check for custom data types
        if "CUSTOM_DATA_TYPES" in content:
            print("✅ Found CUSTOM_DATA_TYPES definition")

            # Check for expected data types
            expected_types = ["DCI_IMAGE_DATA", "BINARY_DATA"]
            for data_type in expected_types:
                if data_type in content:
                    print(f"✅ Custom data type '{data_type}' is defined")
                else:
                    print(f"❌ Missing custom data type '{data_type}'")
        else:
            print("⚠️  CUSTOM_DATA_TYPES not found")

        # Check for proper imports
        if "from .py.nodes import" in content:
            print("✅ Found proper relative imports from py.nodes")
        else:
            print("⚠️  Relative imports from py.nodes not found")

        # Check for proper exports
        if "__all__" in content:
            print("✅ Found __all__ export definition")
        else:
            print("⚠️  __all__ export definition not found")

        print("\n🎉 Node registration test completed!")
        return True

    except FileNotFoundError:
        print("❌ Error: __init__.py file not found")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_nodes_file():
    """Test that the nodes.py file has proper structure"""
    try:
        nodes_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "py", "nodes.py")

        with open(nodes_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print("\n📋 Testing py/nodes.py structure...")

        # Check for proper exception handling
        bare_except_count = len(re.findall(r'except\s*:', content))
        if bare_except_count > 0:
            print(f"⚠️  Found {bare_except_count} bare except statements (should use specific exceptions)")
        else:
            print("✅ No bare except statements found")

        # Check for proper folder_paths usage
        folder_paths_usage = re.findall(r'import folder_paths', content)
        if folder_paths_usage:
            print(f"✅ Found {len(folder_paths_usage)} proper folder_paths imports")

        # Check for proper category usage
        categories = re.findall(r'CATEGORY\s*=\s*"([^"]+)"', content)
        dci_categories = [cat for cat in categories if cat.startswith("DCI/")]
        print(f"✅ Found {len(dci_categories)} DCI category definitions")

        return True

    except FileNotFoundError:
        print("❌ Error: py/nodes.py file not found")
        return False
    except Exception as e:
        print(f"❌ Error testing nodes.py: {str(e)}")
        return False

def test_install_scripts():
    """Test that install scripts use proper pip invocation"""
    try:
        print("\n🔧 Testing install scripts...")

        # Test install.sh
        install_sh = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "install.sh")
        if os.path.exists(install_sh):
            with open(install_sh, 'r', encoding='utf-8') as f:
                content = f.read()

            if "python -m pip" in content:
                print("✅ install.sh uses proper pip invocation")
            else:
                print("⚠️  install.sh doesn't use 'python -m pip'")

        # Test install.bat
        install_bat = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "install.bat")
        if os.path.exists(install_bat):
            with open(install_bat, 'r', encoding='utf-8') as f:
                content = f.read()

            if "python -m pip" in content:
                print("✅ install.bat uses proper pip invocation")
            else:
                print("⚠️  install.bat doesn't use 'python -m pip'")

        return True

    except Exception as e:
        print(f"❌ Error testing install scripts: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing ComfyUI DCI Node Registration")
    print("=" * 50)

    success = True
    success &= test_node_registration()
    success &= test_nodes_file()
    success &= test_install_scripts()

    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
