import struct
import os
from io import BytesIO
from ..utils.file_utils import load_binary_data, save_binary_data, get_output_directory, clean_file_name, ensure_directory
from .base_node import BaseNode
from ..utils.i18n import t

try:
    from ..dci_format import DCIFile
except ImportError:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(current_dir))
    from dci_format import DCIFile

class DCIFileNode(BaseNode):
    """ComfyUI node for combining multiple DCI images into a DCI file"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                t("dci_image_1"): ("DCI_IMAGE_DATA",),
                t("dci_image_2"): ("DCI_IMAGE_DATA",),
                t("dci_image_3"): ("DCI_IMAGE_DATA",),
                t("dci_image_4"): ("DCI_IMAGE_DATA",),
                t("dci_image_5"): ("DCI_IMAGE_DATA",),
                t("dci_image_6"): ("DCI_IMAGE_DATA",),
                t("dci_image_7"): ("DCI_IMAGE_DATA",),
                t("dci_image_8"): ("DCI_IMAGE_DATA",),
                t("dci_image_9"): ("DCI_IMAGE_DATA",),
                t("dci_image_10"): ("DCI_IMAGE_DATA",),
                t("dci_image_11"): ("DCI_IMAGE_DATA",),
                t("dci_image_12"): ("DCI_IMAGE_DATA",),
            }
        }

    RETURN_TYPES = ("BINARY_DATA",)
    RETURN_NAMES = (t("dci_binary_data"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Export')}"

    def _execute(self, **kwargs):
        """Combine multiple DCI images into a DCI file"""
        # Collect all DCI image data
        dci_images = []
        for i in range(1, 13):  # Support up to 12 images
            # Try both translated and original parameter names for compatibility
            dci_image_key_translated = t(f"dci_image_{i}")
            dci_image_key_original = f"dci_image_{i}"
            dci_image = kwargs.get(dci_image_key_translated) or kwargs.get(dci_image_key_original)
            if dci_image:
                dci_images.append(dci_image)

        if not dci_images:
            print("No DCI images provided")
            return (b"",)

        # Create DCI file structure
        dci_file = DCIFile()
        directory_structure = {}

        # Process each DCI image
        for dci_image in dci_images:
            path = dci_image['path']
            content = dci_image['content']

            # Parse path: size/state.tone/scale/filename
            path_parts = path.split('/')
            if len(path_parts) != 4:
                print(f"Invalid DCI path format: {path}")
                continue

            size_dir, state_tone_dir, scale_dir, filename_part = path_parts

            # Build nested directory structure
            if size_dir not in directory_structure:
                directory_structure[size_dir] = {}
            if state_tone_dir not in directory_structure[size_dir]:
                directory_structure[size_dir][state_tone_dir] = {}
            if scale_dir not in directory_structure[size_dir][state_tone_dir]:
                directory_structure[size_dir][state_tone_dir][scale_dir] = {}

            directory_structure[size_dir][state_tone_dir][scale_dir][filename_part] = content

        # Convert directory structure to DCI format
        for size_dir, size_content in directory_structure.items():
            state_tone_dirs = []

            for state_tone_dir, state_tone_content in size_content.items():
                scale_dirs = []

                for scale_dir, scale_content in state_tone_content.items():
                    # Create files for this scale directory
                    scale_files = []
                    for filename_part, file_content in scale_content.items():
                        scale_files.append({
                            'name': filename_part,
                            'content': file_content,
                            'type': DCIFile.FILE_TYPE_FILE
                        })

                    # Create scale directory
                    scale_dir_content = self._create_directory_content(scale_files, dci_file)
                    scale_dirs.append({
                        'name': scale_dir,
                        'content': scale_dir_content,
                        'type': DCIFile.FILE_TYPE_DIRECTORY
                    })

                # Create state.tone directory
                state_tone_dir_content = self._create_directory_content(scale_dirs, dci_file)
                state_tone_dirs.append({
                    'name': state_tone_dir,
                    'content': state_tone_dir_content,
                    'type': DCIFile.FILE_TYPE_DIRECTORY
                })

            # Add size directory to DCI
            dci_file.add_directory(size_dir, state_tone_dirs)

        # Generate binary data
        binary_data = dci_file.to_binary()

        print(f"Created DCI file with {len(dci_images)} images ({len(binary_data)} bytes)")
        return (binary_data,)

    def _create_directory_content(self, files, dci_file):
        """Create directory content from file list"""
        dir_content = BytesIO()

        # Sort files by name
        sorted_files = sorted(files, key=lambda x: dci_file._natural_sort_key(x['name']))

        for file_info in sorted_files:
            # File type (1 byte)
            dir_content.write(struct.pack('<B', file_info.get('type', DCIFile.FILE_TYPE_FILE)))

            # File name (63 bytes, null-terminated)
            file_name_bytes = file_info['name'].encode('utf-8')
            name_padded = file_name_bytes + b'\x00' * (63 - len(file_name_bytes))
            dir_content.write(name_padded)

            # Content size (8 bytes)
            content = file_info['content']
            dir_content.write(struct.pack('<Q', len(content)))

            # Content
            dir_content.write(content)

        return dir_content.getvalue()


class BinaryFileLoader(BaseNode):
    """ComfyUI node for loading binary files from file system"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                t("file_path"): ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("BINARY_DATA", "STRING")
    RETURN_NAMES = (t("binary_data"), t("file_path"))
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Files')}"

    def _execute(self, **kwargs):
        """Load binary file from file system"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        file_path = kwargs.get(t("file_path")) or kwargs.get("file_path", "")

        return self._execute_impl(file_path)

    def _execute_impl(self, file_path=""):
        """Load binary file from file system"""
        if not file_path:
            print("No file path provided")
            return (None, "")

        content = load_binary_data(file_path)
        if content is None:
            return (None, "")

        print(f"Loaded binary file: {os.path.basename(file_path)} ({len(content)} bytes)")
        return (content, file_path)


class BinaryFileSaver(BaseNode):
    """ComfyUI node for saving binary data to file system"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("binary_data"): ("BINARY_DATA",),
                t("file_name"): ("STRING", {"default": "binary_file", "multiline": False}),
            },
            "optional": {
                t("output_directory"): ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = (t("saved_path"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Files')}"
    OUTPUT_NODE = True

    def _execute(self, **kwargs):
        """Save binary data to file system"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        binary_data = kwargs.get(t("binary_data")) or kwargs.get("binary_data")
        file_name = kwargs.get(t("file_name")) or kwargs.get("file_name")
        output_directory = kwargs.get(t("output_directory")) or kwargs.get("output_directory", "")

        return self._execute_impl(binary_data, file_name, output_directory)

    def _execute_impl(self, binary_data, file_name, output_directory=""):
        """Save binary data to file system"""
        # Check if binary_data is valid
        if binary_data is None:
            print("No binary data provided (None)")
            return ("",)

        if isinstance(binary_data, bytes) and len(binary_data) == 0:
            print("Empty binary data provided")
            return ("",)

        if not isinstance(binary_data, bytes):
            print(f"Invalid binary data type: {type(binary_data)}")
            return ("",)

        print(f"Processing binary data: {len(binary_data)} bytes")

        # Clean up file name
        cleaned_file_name = clean_file_name(file_name)

        # Determine output directory
        if output_directory and os.path.exists(output_directory):
            output_dir = output_directory
        else:
            output_dir = get_output_directory()

        # Create full path
        full_path = os.path.join(output_dir, cleaned_file_name)
        print(f"Target file path: {full_path}")

        # Ensure directory exists
        dir_path = os.path.dirname(full_path)
        if dir_path:
            ensure_directory(dir_path)

        # Write binary data
        bytes_written = save_binary_data(binary_data, full_path)
        if bytes_written > 0:
            print(f"File saved successfully: {full_path} ({bytes_written} bytes)")
            return (full_path,)
        else:
            print(f"Failed to save file: {full_path}")
            return ("",)
