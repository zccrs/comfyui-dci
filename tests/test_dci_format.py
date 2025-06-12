#!/usr/bin/env python3
"""
Unit tests for DCI format implementation
"""

import unittest
import os
import sys
import tempfile
import shutil
from PIL import Image, ImageDraw

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

try:
    from dci_format import create_dci_icon, DCIIconBuilder
    from dci_reader import DCIReader, DCIPreviewGenerator
except ImportError as e:
    print(f"Warning: Could not import DCI modules: {e}")
    create_dci_icon = None
    DCIIconBuilder = None
    DCIReader = None
    DCIPreviewGenerator = None


class TestDCIFormat(unittest.TestCase):
    """Test DCI format creation and parsing"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def create_test_image(self, size=256, color=(255, 0, 0, 255)):
        """Create a test image with specified size and color"""
        image = Image.new('RGBA', (size, size), color)
        draw = ImageDraw.Draw(image)

        # Draw a simple pattern
        draw.rectangle([size//4, size//4, 3*size//4, 3*size//4],
                      fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
        draw.text((size//2-20, size//2-10), "TEST", fill=(0, 0, 0, 255))

        return image

    @unittest.skipIf(create_dci_icon is None, "DCI format module not available")
    def test_basic_dci_creation(self):
        """Test basic DCI file creation"""
        test_img = self.create_test_image()
        output_path = os.path.join(self.test_dir, "test_basic.dci")

        create_dci_icon(
            image=test_img,
            output_path=output_path,
            size=256,
            states=['normal'],
            tones=['dark'],
            scales=[1, 2, 3],
            format='webp'
        )

        self.assertTrue(os.path.exists(output_path), "DCI file should be created")
        self.assertGreater(os.path.getsize(output_path), 0, "DCI file should not be empty")

    @unittest.skipIf(DCIIconBuilder is None, "DCI format module not available")
    def test_advanced_dci_creation(self):
        """Test advanced DCI creation with multiple states"""
        # Create different images for different states
        normal_img = self.create_test_image(color=(0, 255, 0, 255))  # Green
        hover_img = self.create_test_image(color=(255, 255, 0, 255))  # Yellow
        pressed_img = self.create_test_image(color=(255, 0, 0, 255))  # Red

        builder = DCIIconBuilder()

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

        output_path = os.path.join(self.test_dir, "test_advanced.dci")
        builder.build(output_path)

        self.assertTrue(os.path.exists(output_path), "Advanced DCI file should be created")
        self.assertGreater(os.path.getsize(output_path), 0, "Advanced DCI file should not be empty")

    @unittest.skipIf(create_dci_icon is None, "DCI format module not available")
    def test_different_formats(self):
        """Test different image formats"""
        test_img = self.create_test_image()
        formats = ['webp', 'png']  # Skip jpg for now as it might have issues with transparency

        for fmt in formats:
            with self.subTest(format=fmt):
                output_path = os.path.join(self.test_dir, f"test_{fmt}.dci")

                create_dci_icon(
                    image=test_img,
                    output_path=output_path,
                    size=128,
                    format=fmt
                )

                self.assertTrue(os.path.exists(output_path), f"{fmt.upper()} format DCI should be created")
                self.assertGreater(os.path.getsize(output_path), 0, f"{fmt.upper()} format DCI should not be empty")

    def test_dci_file_structure(self):
        """Test DCI file structure inspection"""
        if create_dci_icon is None:
            self.skipTest("DCI format module not available")

        test_img = self.create_test_image()
        output_path = os.path.join(self.test_dir, "test_structure.dci")

        create_dci_icon(
            image=test_img,
            output_path=output_path,
            size=256,
            states=['normal'],
            tones=['dark'],
            scales=[1],
            format='webp'
        )

        # Inspect file structure
        with open(output_path, 'rb') as f:
            # Read header
            magic = f.read(4)
            version = f.read(1)[0]
            file_count_bytes = f.read(3)
            file_count = int.from_bytes(file_count_bytes + b'\x00', 'little')

            self.assertEqual(magic, b'DCI\x00', "Magic header should be correct")
            self.assertEqual(version, 1, "Version should be 1")
            self.assertGreater(file_count, 0, "File count should be greater than 0")


class TestDCIReader(unittest.TestCase):
    """Test DCI file reading and parsing"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    @unittest.skipIf(DCIReader is None, "DCI reader module not available")
    def test_dci_reader_initialization(self):
        """Test DCI reader initialization"""
        # Test with file path
        reader1 = DCIReader(file_path="test.dci")
        self.assertEqual(reader1.file_path, "test.dci")
        self.assertIsNone(reader1.binary_data)

        # Test with binary data
        test_data = b"test data"
        reader2 = DCIReader(binary_data=test_data)
        self.assertEqual(reader2.binary_data, test_data)
        self.assertIsNone(reader2.file_path)

    @unittest.skipIf(DCIReader is None, "DCI reader module not available")
    def test_dci_reader_invalid_input(self):
        """Test DCI reader with invalid input"""
        reader = DCIReader()

        # The read() method returns False on error, doesn't raise ValueError
        result = reader.read()
        self.assertFalse(result, "read() should return False for invalid input")

    @unittest.skipIf(DCIReader is None, "DCI reader module not available")
    def test_state_tone_parsing(self):
        """Test state and tone parsing"""
        reader = DCIReader()

        # Test normal cases
        state, tone = reader._parse_state_tone("normal.dark")
        self.assertEqual(state, "normal")
        self.assertEqual(tone, "dark")

        # Test edge cases
        state, tone = reader._parse_state_tone("hover")
        self.assertEqual(state, "hover")
        self.assertEqual(tone, "unknown")

        state, tone = reader._parse_state_tone("")
        self.assertEqual(state, "unknown")
        self.assertEqual(tone, "unknown")

    @unittest.skipIf(DCIReader is None, "DCI reader module not available")
    def test_layer_filename_parsing(self):
        """Test layer filename parsing"""
        reader = DCIReader()

        # Test simple format
        result = reader._parse_layer_filename("1.webp")
        self.assertEqual(result['priority'], 1)
        self.assertEqual(result['format'], 'webp')
        self.assertFalse(result['is_alpha8'])

        # Test with alpha8
        result = reader._parse_layer_filename("2.png.alpha8")
        self.assertEqual(result['priority'], 2)
        self.assertEqual(result['format'], 'png')
        self.assertTrue(result['is_alpha8'])

        # Test with padding
        result = reader._parse_layer_filename("1.10p.webp")
        self.assertEqual(result['priority'], 1)
        self.assertEqual(result['padding'], 10)
        self.assertEqual(result['format'], 'webp')

        # Test with palette and color adjustments
        result = reader._parse_layer_filename("1.3_0_0_-10_0_0_0_0.webp")
        self.assertEqual(result['priority'], 1)
        self.assertEqual(result['palette'], 3)
        self.assertEqual(result['brightness'], -10)
        self.assertEqual(result['format'], 'webp')


class TestDCIPreviewGenerator(unittest.TestCase):
    """Test DCI preview generation"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    @unittest.skipIf(DCIPreviewGenerator is None, "DCI preview generator module not available")
    def test_preview_generator_initialization(self):
        """Test preview generator initialization"""
        generator = DCIPreviewGenerator()
        self.assertEqual(generator.background_color, (240, 240, 240))
        self.assertEqual(generator.font_size, 12)

        # Test with custom parameters
        generator2 = DCIPreviewGenerator(background_color=(255, 255, 255), font_size=16)
        self.assertEqual(generator2.background_color, (255, 255, 255))
        self.assertEqual(generator2.font_size, 16)

    @unittest.skipIf(DCIPreviewGenerator is None, "DCI preview generator module not available")
    def test_contrasting_text_color(self):
        """Test contrasting text color calculation"""
        generator = DCIPreviewGenerator()

        # Test light background
        text_color = generator._get_contrasting_text_color((255, 255, 255))
        self.assertEqual(text_color, (0, 0, 0))  # Should be black

        # Test dark background
        text_color = generator._get_contrasting_text_color((0, 0, 0))
        self.assertEqual(text_color, (255, 255, 255))  # Should be white

    @unittest.skipIf(DCIPreviewGenerator is None, "DCI preview generator module not available")
    def test_empty_preview_creation(self):
        """Test empty preview creation"""
        generator = DCIPreviewGenerator()
        preview = generator._create_empty_preview()

        self.assertIsInstance(preview, Image.Image)
        self.assertEqual(preview.size, (400, 200))
        self.assertEqual(preview.mode, 'RGB')

    @unittest.skipIf(DCIPreviewGenerator is None, "DCI preview generator module not available")
    def test_text_wrapping(self):
        """Test text wrapping functionality"""
        generator = DCIPreviewGenerator()

        # Create a temporary image for text measurement
        temp_img = Image.new('RGB', (100, 100))
        draw = ImageDraw.Draw(temp_img)

        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
        except:
            font = None

        if font:
            # Test short text (should not wrap)
            lines = generator._wrap_text("Short", 200, font, draw)
            self.assertEqual(len(lines), 1)
            self.assertEqual(lines[0], "Short")

            # Test long text (should wrap)
            long_text = "This is a very long text that should be wrapped"
            lines = generator._wrap_text(long_text, 50, font, draw)
            self.assertGreater(len(lines), 1)


if __name__ == '__main__':
    unittest.main()
