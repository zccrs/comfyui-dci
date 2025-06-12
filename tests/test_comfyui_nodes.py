#!/usr/bin/env python3
"""
Unit tests for ComfyUI nodes
"""

import unittest
import os
import sys
import tempfile
import shutil
from PIL import Image
import numpy as np

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

try:
    from nodes.dci_preview_node import DCIPreviewNode
    from nodes.dci_file_saver_node import DCIFileSaverNode
    from nodes.binary_file_loader_node import BinaryFileLoaderNode
    from nodes.binary_file_saver_node import BinaryFileSaverNode
    from nodes.base64_encoder_node import Base64EncoderNode
    from nodes.base64_decoder_node import Base64DecoderNode
    from nodes.deb_packager_node import DebPackager
    from nodes.deb_loader_node import DebLoader
except ImportError as e:
    print(f"Warning: Could not import ComfyUI nodes: {e}")
    DCIPreviewNode = None
    DCIFileSaverNode = None
    BinaryFileLoaderNode = None
    BinaryFileSaverNode = None
    Base64EncoderNode = None
    Base64DecoderNode = None
    DebPackager = None
    DebLoader = None


class TestDCINodes(unittest.TestCase):
    """Test DCI-related ComfyUI nodes"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def create_test_image_tensor(self, width=256, height=256, channels=3):
        """Create a test image tensor"""
        # Create a simple gradient image
        image_array = np.zeros((height, width, channels), dtype=np.float32)

        for y in range(height):
            for x in range(width):
                image_array[y, x, 0] = x / width  # Red gradient
                image_array[y, x, 1] = y / height  # Green gradient
                if channels > 2:
                    image_array[y, x, 2] = 0.5  # Blue constant
                if channels > 3:
                    image_array[y, x, 3] = 1.0  # Alpha constant

        # Add batch dimension
        return np.expand_dims(image_array, axis=0)

    @unittest.skipIf(DCIPreviewNode is None, "DCI preview node not available")
    def test_dci_preview_node_initialization(self):
        """Test DCI preview node initialization"""
        node = DCIPreviewNode()
        self.assertIsNotNone(node)

        # Test class methods
        input_types = DCIPreviewNode.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("binary_data", input_types["required"])

        return_types = DCIPreviewNode.RETURN_TYPES
        self.assertIn("IMAGE", return_types)

    @unittest.skipIf(DCIFileSaverNode is None, "DCI file saver node not available")
    def test_dci_file_saver_node_initialization(self):
        """Test DCI file saver node initialization"""
        node = DCIFileSaverNode()
        self.assertIsNotNone(node)

        # Test class methods
        input_types = DCIFileSaverNode.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("image", input_types["required"])

        return_types = DCIFileSaverNode.RETURN_TYPES
        self.assertIn("STRING", return_types)

    @unittest.skipIf(DCIFileSaverNode is None, "DCI file saver node not available")
    def test_dci_file_saver_execution(self):
        """Test DCI file saver execution"""
        node = DCIFileSaverNode()

        # Create test image tensor
        image_tensor = self.create_test_image_tensor()

        # Test parameters
        output_path = os.path.join(self.test_dir, "test_output.dci")

        try:
            result = node.save_dci_file(
                image=image_tensor,
                output_path=output_path,
                size=256,
                states="normal",
                tones="dark",
                scales="1,2",
                format="webp",
                quality=80
            )

            # Check if result is returned (should be a tuple with file path)
            self.assertIsInstance(result, tuple)
            self.assertTrue(len(result) > 0)

        except Exception as e:
            # If the node implementation has issues, we should at least test that it doesn't crash
            self.fail(f"DCI file saver execution failed: {e}")


class TestBinaryFileNodes(unittest.TestCase):
    """Test binary file handling nodes"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    @unittest.skipIf(BinaryFileLoaderNode is None, "Binary file loader node not available")
    def test_binary_file_loader_initialization(self):
        """Test binary file loader initialization"""
        node = BinaryFileLoaderNode()
        self.assertIsNotNone(node)

        # Test class methods
        input_types = BinaryFileLoaderNode.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("file_path", input_types["required"])

        return_types = BinaryFileLoaderNode.RETURN_TYPES
        self.assertIn("BINARY_DATA", return_types)

    @unittest.skipIf(BinaryFileLoaderNode is None, "Binary file loader node not available")
    def test_binary_file_loader_execution(self):
        """Test binary file loader execution"""
        node = BinaryFileLoaderNode()

        # Create test file
        test_content = b"Test binary content for loader"
        test_file = os.path.join(self.test_dir, "test.bin")
        with open(test_file, 'wb') as f:
            f.write(test_content)

        try:
            result = node.load_binary_file(file_path=test_file)

            # Check result format
            self.assertIsInstance(result, tuple)
            self.assertTrue(len(result) >= 1)

            # The first element should be the binary data
            loaded_data = result[0]
            self.assertEqual(loaded_data, test_content)

        except Exception as e:
            self.fail(f"Binary file loader execution failed: {e}")

    @unittest.skipIf(BinaryFileSaverNode is None, "Binary file saver node not available")
    def test_binary_file_saver_initialization(self):
        """Test binary file saver initialization"""
        node = BinaryFileSaverNode()
        self.assertIsNotNone(node)

        # Test class methods
        input_types = BinaryFileSaverNode.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("binary_data", input_types["required"])

        return_types = BinaryFileSaverNode.RETURN_TYPES
        self.assertIn("STRING", return_types)

    @unittest.skipIf(BinaryFileSaverNode is None, "Binary file saver node not available")
    def test_binary_file_saver_execution(self):
        """Test binary file saver execution"""
        node = BinaryFileSaverNode()

        # Test data
        test_content = b"Test binary content for saver"
        output_file = os.path.join(self.test_dir, "output.bin")

        try:
            result = node.save_binary_file(
                binary_data=test_content,
                file_path=output_file
            )

            # Check result
            self.assertIsInstance(result, tuple)
            self.assertTrue(len(result) >= 1)

            # Verify file was created
            self.assertTrue(os.path.exists(output_file))

            # Verify file content
            with open(output_file, 'rb') as f:
                saved_content = f.read()
                self.assertEqual(saved_content, test_content)

        except Exception as e:
            self.fail(f"Binary file saver execution failed: {e}")


class TestBase64Nodes(unittest.TestCase):
    """Test Base64 encoding/decoding nodes"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    @unittest.skipIf(Base64EncoderNode is None, "Base64 encoder node not available")
    def test_base64_encoder_initialization(self):
        """Test Base64 encoder initialization"""
        node = Base64EncoderNode()
        self.assertIsNotNone(node)

        # Test class methods
        input_types = Base64EncoderNode.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("binary_data", input_types["required"])

        return_types = Base64EncoderNode.RETURN_TYPES
        self.assertIn("STRING", return_types)

    @unittest.skipIf(Base64EncoderNode is None, "Base64 encoder node not available")
    def test_base64_encoder_execution(self):
        """Test Base64 encoder execution"""
        node = Base64EncoderNode()

        # Test data
        test_content = b"Test binary content for Base64 encoding"

        try:
            result = node.encode_base64(binary_data=test_content)

            # Check result
            self.assertIsInstance(result, tuple)
            self.assertTrue(len(result) >= 1)

            # The result should be a Base64 string
            encoded_data = result[0]
            self.assertIsInstance(encoded_data, str)

            # Verify it's valid Base64
            import base64
            decoded_back = base64.b64decode(encoded_data)
            self.assertEqual(decoded_back, test_content)

        except Exception as e:
            self.fail(f"Base64 encoder execution failed: {e}")

    @unittest.skipIf(Base64DecoderNode is None, "Base64 decoder node not available")
    def test_base64_decoder_initialization(self):
        """Test Base64 decoder initialization"""
        node = Base64DecoderNode()
        self.assertIsNotNone(node)

        # Test class methods
        input_types = Base64DecoderNode.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("base64_string", input_types["required"])

        return_types = Base64DecoderNode.RETURN_TYPES
        self.assertIn("BINARY_DATA", return_types)

    @unittest.skipIf(Base64DecoderNode is None, "Base64 decoder node not available")
    def test_base64_decoder_execution(self):
        """Test Base64 decoder execution"""
        node = Base64DecoderNode()

        # Test data
        test_content = b"Test binary content for Base64 decoding"
        import base64
        encoded_content = base64.b64encode(test_content).decode('utf-8')

        try:
            result = node.decode_base64(base64_string=encoded_content)

            # Check result
            self.assertIsInstance(result, tuple)
            self.assertTrue(len(result) >= 1)

            # The result should be the original binary data
            decoded_data = result[0]
            self.assertEqual(decoded_data, test_content)

        except Exception as e:
            self.fail(f"Base64 decoder execution failed: {e}")

    @unittest.skipIf(Base64EncoderNode is None or Base64DecoderNode is None, "Base64 nodes not available")
    def test_base64_round_trip(self):
        """Test Base64 encoding and decoding round trip"""
        encoder = Base64EncoderNode()
        decoder = Base64DecoderNode()

        # Test data
        test_content = b"Test binary content for round trip encoding/decoding"

        try:
            # Encode
            encode_result = encoder.encode_base64(binary_data=test_content)
            encoded_data = encode_result[0]

            # Decode
            decode_result = decoder.decode_base64(base64_string=encoded_data)
            decoded_data = decode_result[0]

            # Verify round trip
            self.assertEqual(decoded_data, test_content)

        except Exception as e:
            self.fail(f"Base64 round trip failed: {e}")


class TestDebNodes(unittest.TestCase):
    """Test DEB package nodes"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    @unittest.skipIf(DebPackager is None, "DEB packager node not available")
    def test_deb_packager_initialization(self):
        """Test DEB packager initialization"""
        node = DebPackager()
        self.assertIsNotNone(node)

        # Test class methods
        input_types = DebPackager.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("local_directory", input_types["required"])

        return_types = DebPackager.RETURN_TYPES
        self.assertIn("STRING", return_types)

    @unittest.skipIf(DebLoader is None, "DEB loader node not available")
    def test_deb_loader_initialization(self):
        """Test DEB loader initialization"""
        node = DebLoader()
        self.assertIsNotNone(node)

        # Test class methods
        input_types = DebLoader.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("deb_file_path", input_types["required"])

        return_types = DebLoader.RETURN_TYPES
        self.assertIn("BINARY_DATA", return_types)

    def test_node_categories(self):
        """Test that nodes have proper categories"""
        nodes_to_test = [
            (DCIPreviewNode, "DCI"),
            (DCIFileSaverNode, "DCI"),
            (BinaryFileLoaderNode, "file"),
            (BinaryFileSaverNode, "file"),
            (Base64EncoderNode, "encoding"),
            (Base64DecoderNode, "encoding"),
            (DebPackager, "packaging"),
            (DebLoader, "packaging"),
        ]

        for node_class, expected_category in nodes_to_test:
            if node_class is not None:
                with self.subTest(node=node_class.__name__):
                    category = getattr(node_class, 'CATEGORY', None)
                    self.assertIsNotNone(category, f"{node_class.__name__} should have a CATEGORY")
                    self.assertIn(expected_category, category.lower(),
                                f"{node_class.__name__} category should contain '{expected_category}'")

    def test_node_functions(self):
        """Test that nodes have proper function names"""
        nodes_to_test = [
            (DCIPreviewNode, "preview_dci"),
            (DCIFileSaverNode, "save_dci_file"),
            (BinaryFileLoaderNode, "load_binary_file"),
            (BinaryFileSaverNode, "save_binary_file"),
            (Base64EncoderNode, "encode_base64"),
            (Base64DecoderNode, "decode_base64"),
            (DebPackager, "package_deb"),
            (DebLoader, "load_deb"),
        ]

        for node_class, expected_function in nodes_to_test:
            if node_class is not None:
                with self.subTest(node=node_class.__name__):
                    function_name = getattr(node_class, 'FUNCTION', None)
                    self.assertIsNotNone(function_name, f"{node_class.__name__} should have a FUNCTION")
                    self.assertEqual(function_name, expected_function,
                                   f"{node_class.__name__} function should be '{expected_function}'")


if __name__ == '__main__':
    unittest.main()
