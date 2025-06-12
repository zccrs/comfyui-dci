#!/usr/bin/env python3
"""
Unit tests for pure Python AR implementation
"""

import unittest
import os
import sys
import tempfile
import shutil

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

try:
    from nodes.deb_packager_node import DebPackager
    from nodes.deb_loader_node import DebLoader
except ImportError as e:
    print(f"Warning: Could not import DEB nodes: {e}")
    DebPackager = None
    DebLoader = None


class TestPurePythonAR(unittest.TestCase):
    """Test pure Python AR implementation"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def create_ar_archive_python(self, archive_path, files, working_dir):
        """Create ar archive using pure Python implementation"""
        try:
            with open(archive_path, 'wb') as ar_file:
                # Write ar archive signature
                ar_file.write(b"!<arch>\n")

                for filename in files:
                    file_path = os.path.join(working_dir, filename)

                    if not os.path.exists(file_path):
                        continue

                    # Get file stats
                    stat = os.stat(file_path)
                    file_size = stat.st_size

                    # Read file content
                    with open(file_path, 'rb') as f:
                        file_content = f.read()

                    # Create ar header (60 bytes)
                    name_field = filename.ljust(16)[:16].encode('ascii')
                    date_field = str(int(stat.st_mtime)).ljust(12)[:12].encode('ascii')
                    uid_field = b"0     "  # 6 bytes
                    gid_field = b"0     "  # 6 bytes
                    mode_field = b"100644  "  # 8 bytes
                    size_field = str(file_size).ljust(10)[:10].encode('ascii')
                    end_field = b"`\n"  # 2 bytes

                    header = name_field + date_field + uid_field + gid_field + mode_field + size_field + end_field

                    # Write header and content
                    ar_file.write(header)
                    ar_file.write(file_content)

                    # Add padding if file size is odd
                    if file_size % 2 == 1:
                        ar_file.write(b"\n")

            return True

        except Exception as e:
            print(f"Error creating AR archive: {e}")
            return False

    def extract_ar_archive_python(self, deb_file_path, extract_dir):
        """Extract ar archive using pure Python implementation"""
        try:
            with open(deb_file_path, 'rb') as f:
                # Read ar header
                magic = f.read(8)
                if magic != b'!<arch>\n':
                    return False

                while True:
                    # Read file header (60 bytes)
                    header = f.read(60)
                    if len(header) < 60:
                        break

                    # Parse header
                    filename = header[0:16].decode('ascii').strip()
                    size_str = header[48:58].decode('ascii').strip()

                    if not size_str:
                        break

                    size = int(size_str)

                    # Read file content
                    content = f.read(size)

                    # Pad to even boundary
                    if size % 2 == 1:
                        f.read(1)

                    # Save file
                    if filename and not filename.startswith('/'):
                        output_path = os.path.join(extract_dir, filename)
                        with open(output_path, 'wb') as out_f:
                            out_f.write(content)

            return True

        except Exception as e:
            print(f"Error extracting AR archive: {e}")
            return False

    def test_ar_format_validation(self):
        """Test AR format validation"""
        # Create test files
        test_files = []
        for i in range(3):
            filename = f"test_{i}.txt"
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f"Test content {i}\nThis is file number {i}")
            test_files.append(filename)

        # Create AR archive
        ar_path = os.path.join(self.test_dir, "test.ar")
        success = self.create_ar_archive_python(ar_path, test_files, self.test_dir)

        self.assertTrue(success, "AR archive creation should succeed")
        self.assertTrue(os.path.exists(ar_path), "AR archive file should exist")
        self.assertGreater(os.path.getsize(ar_path), 0, "AR archive should not be empty")

        # Verify AR format
        with open(ar_path, 'rb') as f:
            magic = f.read(8)
            self.assertEqual(magic, b'!<arch>\n', "AR magic header should be correct")

    def test_ar_extraction(self):
        """Test AR archive extraction"""
        # Create test files
        test_files = []
        test_contents = {}
        for i in range(3):
            filename = f"test_{i}.txt"
            content = f"Test content {i}\nThis is file number {i}"
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            test_files.append(filename)
            test_contents[filename] = content

        # Create AR archive
        ar_path = os.path.join(self.test_dir, "test.ar")
        success = self.create_ar_archive_python(ar_path, test_files, self.test_dir)
        self.assertTrue(success, "AR archive creation should succeed")

        # Extract AR archive
        extract_dir = os.path.join(self.test_dir, "extract")
        os.makedirs(extract_dir)
        success = self.extract_ar_archive_python(ar_path, extract_dir)
        self.assertTrue(success, "AR archive extraction should succeed")

        # Verify extracted files
        for filename, expected_content in test_contents.items():
            extracted_file = os.path.join(extract_dir, filename)
            self.assertTrue(os.path.exists(extracted_file), f"Extracted file {filename} should exist")

            with open(extracted_file, 'r') as f:
                actual_content = f.read()
                self.assertEqual(actual_content, expected_content, f"Content of {filename} should match")

    def test_cross_platform_compatibility(self):
        """Test cross-platform compatibility"""
        # Test different file names and contents (AR format file name limit is 16 characters)
        test_cases = [
            ("simple.txt", "Simple content"),
            ("with-dash.txt", "Content with dash"),
            ("under_score.txt", "Content with underscore"),
            ("file123.txt", "Numeric content"),
        ]

        files = []
        for filename, content in test_cases:
            if len(filename) <= 16:  # AR format limitation
                filepath = os.path.join(self.test_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(content)
                files.append(filename)

        # Create and extract AR archive
        ar_path = os.path.join(self.test_dir, "cross_platform.ar")
        success = self.create_ar_archive_python(ar_path, files, self.test_dir)
        self.assertTrue(success, "Cross-platform AR creation should succeed")

        extract_dir = os.path.join(self.test_dir, "extract")
        os.makedirs(extract_dir)
        success = self.extract_ar_archive_python(ar_path, extract_dir)
        self.assertTrue(success, "Cross-platform AR extraction should succeed")

        # Verify all files
        for filename, expected_content in test_cases:
            if len(filename) <= 16:
                extracted_file = os.path.join(extract_dir, filename)
                self.assertTrue(os.path.exists(extracted_file), f"File {filename} should be extracted")

                with open(extracted_file, 'r') as f:
                    actual_content = f.read()
                    self.assertEqual(actual_content, expected_content, f"Content of {filename} should match")

    @unittest.skipIf(DebPackager is None or DebLoader is None, "DEB nodes not available")
    def test_pure_python_deb_workflow(self):
        """Test complete DEB package workflow using pure Python implementation"""
        # Create test DCI files
        test_files_dir = os.path.join(self.test_dir, "test_files")
        os.makedirs(test_files_dir)

        test_dci_content = b"DCI test content for pure Python implementation"
        for i in range(3):
            dci_file = os.path.join(test_files_dir, f"test_{i}.dci")
            with open(dci_file, 'wb') as f:
                f.write(test_dci_content + f" {i}".encode())

        # Create DEB package
        output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(output_dir)

        packager = DebPackager()
        result = packager._execute_impl(
            local_directory=test_files_dir,
            file_filter="*.dci",
            include_subdirectories=True,
            install_target_path="/usr/share/test/icons",
            output_directory=output_dir,
            package_name="test-dci-package",
            package_version="1.0.0",
            maintainer_name="Test User",
            maintainer_email="test@example.com",
            package_description="Test DCI package for pure Python implementation"
        )

        deb_path, file_list = result
        self.assertTrue(os.path.exists(deb_path), "DEB package should be created")
        self.assertNotIn("错误", deb_path, "DEB package creation should not have errors")
        self.assertEqual(len(file_list), 3, "Should package 3 files")

        # Load DEB package
        loader = DebLoader()
        load_result = loader._execute_impl(
            deb_file_path=deb_path,
            file_filter="*.dci"
        )

        binary_data_list, relative_paths, image_list, image_relative_paths = load_result

        self.assertEqual(len(binary_data_list), 3, "Should load 3 files")
        self.assertEqual(len(relative_paths), 3, "Should have 3 relative paths")

        # Verify file contents
        for i, (data, path) in enumerate(zip(binary_data_list, relative_paths)):
            expected_content = test_dci_content + f" {i}".encode()
            self.assertEqual(data, expected_content, f"File content should match for {path}")

    def test_ar_header_format(self):
        """Test AR header format compliance"""
        # Create a simple test file
        test_file = "test.txt"
        test_content = "Hello, World!"
        filepath = os.path.join(self.test_dir, test_file)
        with open(filepath, 'w') as f:
            f.write(test_content)

        # Create AR archive
        ar_path = os.path.join(self.test_dir, "test.ar")
        success = self.create_ar_archive_python(ar_path, [test_file], self.test_dir)
        self.assertTrue(success, "AR archive creation should succeed")

        # Verify header format
        with open(ar_path, 'rb') as f:
            # Skip magic
            magic = f.read(8)
            self.assertEqual(magic, b'!<arch>\n', "Magic should be correct")

            # Read header
            header = f.read(60)
            self.assertEqual(len(header), 60, "Header should be exactly 60 bytes")

            # Parse header fields
            name_field = header[0:16]
            date_field = header[16:28]
            uid_field = header[28:34]
            gid_field = header[34:40]
            mode_field = header[40:48]
            size_field = header[48:58]
            end_field = header[58:60]

            # Verify format
            self.assertTrue(name_field.startswith(b'test.txt'), "Name field should start with filename")
            self.assertTrue(date_field.decode('ascii').strip().isdigit(), "Date field should be numeric")
            self.assertEqual(uid_field, b"0     ", "UID field should be correct")
            self.assertEqual(gid_field, b"0     ", "GID field should be correct")
            self.assertEqual(mode_field, b"100644  ", "Mode field should be correct")
            self.assertEqual(size_field.decode('ascii').strip(), str(len(test_content)), "Size field should match content length")
            self.assertEqual(end_field, b"`\n", "End field should be correct")


if __name__ == '__main__':
    unittest.main()
