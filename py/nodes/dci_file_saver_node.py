import os
from ..utils.file_utils import get_output_directory, ensure_directory, save_binary_data
from ..utils.i18n import t
from .base_node import BaseNode

class DCIFileSaver(BaseNode):
    """ComfyUI node for saving DCI binary data to file system with advanced filename handling"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("binary_data"): ("BINARY_DATA",),
                t("input_filename"): ("STRING", {"default": "icon.png", "multiline": False}),
            },
            "optional": {
                t("output_directory"): ("STRING", {"default": "", "multiline": False}),
                t("filename_prefix"): ("STRING", {"default": "", "multiline": False}),
                t("filename_suffix"): ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = (t("saved_filename"), t("saved_full_path"))
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Files')}"
    OUTPUT_NODE = True

    def _execute(self, **kwargs):
        """Save DCI binary data to file system with advanced filename handling"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        binary_data = kwargs.get(t("binary_data")) or kwargs.get("binary_data")
        input_filename = kwargs.get(t("input_filename")) or kwargs.get("input_filename")
        output_directory = kwargs.get(t("output_directory")) or kwargs.get("output_directory", "")
        filename_prefix = kwargs.get(t("filename_prefix")) or kwargs.get("filename_prefix", "")
        filename_suffix = kwargs.get(t("filename_suffix")) or kwargs.get("filename_suffix", "")

        return self._execute_impl(binary_data, input_filename, output_directory, filename_prefix, filename_suffix)

    def _execute_impl(self, binary_data, input_filename, output_directory="", filename_prefix="", filename_suffix=""):
        """Save DCI binary data to file system with intelligent filename parsing"""

        # Check if binary_data is valid
        if binary_data is None:
            print("No binary data provided (None)")
            return ("", "")

        if isinstance(binary_data, bytes) and len(binary_data) == 0:
            print("Empty binary data provided")
            return ("", "")

        if not isinstance(binary_data, bytes):
            print(f"Invalid binary data type: {type(binary_data)}")
            return ("", "")

        print(f"Processing DCI binary data: {len(binary_data)} bytes")

        # Parse filename from input_filename
        parsed_filename = self._parse_filename(input_filename)

        # Apply prefix and suffix
        final_filename = self._apply_prefix_suffix(parsed_filename, filename_prefix, filename_suffix)

        # Determine output directory
        if output_directory and os.path.exists(output_directory):
            output_dir = output_directory
        else:
            output_dir = get_output_directory()

        # Create full path
        full_path = os.path.join(output_dir, final_filename)
        print(f"Target DCI file path: {full_path}")

        # Ensure directory exists
        dir_path = os.path.dirname(full_path)
        if dir_path:
            ensure_directory(dir_path)

        # Write binary data
        bytes_written = save_binary_data(binary_data, full_path)
        if bytes_written > 0:
            print(f"DCI file saved successfully: {final_filename} ({bytes_written} bytes)")
            print(f"Full path: {full_path}")
            return (final_filename, full_path)
        else:
            print(f"Failed to save DCI file: {full_path}")
            return ("", "")

    def _parse_filename(self, input_filename):
        """Parse filename from input string, handling both filenames and full paths"""
        if not input_filename:
            return "icon.dci"

        # Normalize path separators for cross-platform compatibility
        normalized_path = input_filename.replace('\\', '/')

        # Extract basename from path (handles both Windows and Linux separators)
        basename = os.path.basename(normalized_path)

        # If basename is empty (input was just a path separator), use default
        if not basename:
            return "icon.dci"

        # Remove common image extensions and replace with .dci
        name_without_ext = self._remove_image_extension(basename)

        # Add .dci extension
        return f"{name_without_ext}.dci"

    def _remove_image_extension(self, filename):
        """Remove common image extensions from filename"""
        # List of image extensions to remove (case insensitive)
        image_extensions = ['.webp', '.png', '.jpg', '.jpeg', '.apng', '.gif', '.bmp', '.tiff', '.tif']

        # Convert to lowercase for comparison
        filename_lower = filename.lower()

        # Check each extension
        for ext in image_extensions:
            if filename_lower.endswith(ext):
                # Remove the extension (case preserving for the base name)
                return filename[:-len(ext)]

        # If no image extension found, return as is
        return filename

    def _apply_prefix_suffix(self, filename, prefix, suffix):
        """Apply prefix and suffix to filename while preserving the .dci extension"""
        if not filename.endswith('.dci'):
            filename = f"{filename}.dci"

        # Split filename and extension
        name_part = filename[:-4]  # Remove .dci
        extension = '.dci'

        # Apply prefix and suffix
        if prefix:
            name_part = f"{prefix}{name_part}"
        if suffix:
            name_part = f"{name_part}{suffix}"

        return f"{name_part}{extension}"
