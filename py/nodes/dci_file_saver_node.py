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
                t("allow_overwrite"): ("BOOLEAN", {"default": False}),
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
        binary_data = kwargs.get(t("binary_data")) if t("binary_data") in kwargs else kwargs.get("binary_data")
        input_filename = kwargs.get(t("input_filename")) if t("input_filename") in kwargs else kwargs.get("input_filename")
        output_directory = kwargs.get(t("output_directory")) if t("output_directory") in kwargs else kwargs.get("output_directory", "")
        filename_prefix = kwargs.get(t("filename_prefix")) if t("filename_prefix") in kwargs else kwargs.get("filename_prefix", "")
        filename_suffix = kwargs.get(t("filename_suffix")) if t("filename_suffix") in kwargs else kwargs.get("filename_suffix", "")
        allow_overwrite = kwargs.get(t("allow_overwrite")) if t("allow_overwrite") in kwargs else kwargs.get("allow_overwrite", False)

        return self._execute_impl(binary_data, input_filename, output_directory, filename_prefix, filename_suffix, allow_overwrite)

    def _execute_impl(self, binary_data, input_filename, output_directory="", filename_prefix="", filename_suffix="", allow_overwrite=False):
        """Save DCI binary data to file system with intelligent filename parsing"""

        # Check if binary_data is valid
        if binary_data is None:
            error_msg = "错误：未提供二进制数据 (None)"
            print(error_msg)
            return ("", error_msg)

        if isinstance(binary_data, bytes) and len(binary_data) == 0:
            error_msg = "错误：提供的二进制数据为空"
            print(error_msg)
            return ("", error_msg)

        if not isinstance(binary_data, bytes):
            error_msg = f"错误：无效的二进制数据类型: {type(binary_data)}"
            print(error_msg)
            return ("", error_msg)

        print(f"Processing DCI binary data: {len(binary_data)} bytes")

        # Parse filename from input_filename
        try:
            parsed_filename = self._parse_filename(input_filename)
        except Exception as e:
            error_msg = f"错误：文件名解析失败: {str(e)}"
            print(error_msg)
            return ("", error_msg)

        # Apply prefix and suffix
        try:
            final_filename = self._apply_prefix_suffix(parsed_filename, filename_prefix, filename_suffix)
        except Exception as e:
            error_msg = f"错误：文件名前缀后缀处理失败: {str(e)}"
            print(error_msg)
            return ("", error_msg)

        # Determine output directory
        try:
            if output_directory:
                # Use specified output directory, create if it doesn't exist
                output_dir = output_directory
                # Ensure the directory exists
                if not ensure_directory(output_dir):
                    error_msg = f"错误：无法创建输出目录: {output_dir}"
                    print(error_msg)
                    return ("", error_msg)
            else:
                # Use ComfyUI default output directory
                output_dir = get_output_directory()
        except Exception as e:
            error_msg = f"错误：输出目录处理失败: {str(e)}"
            print(error_msg)
            return ("", error_msg)

        # Create full path
        try:
            full_path = os.path.join(output_dir, final_filename)
            print(f"Target DCI file path: {full_path}")
        except Exception as e:
            error_msg = f"错误：文件路径构建失败: {str(e)}"
            print(error_msg)
            return ("", error_msg)

        # Check if file exists and overwrite is not allowed
        if os.path.exists(full_path) and not allow_overwrite:
            error_msg = f"错误：文件已存在且不允许覆盖: {full_path}"
            print(error_msg)
            return ("", error_msg)

        # Ensure directory exists
        try:
            dir_path = os.path.dirname(full_path)
            if dir_path and not ensure_directory(dir_path):
                error_msg = f"错误：无法创建文件目录: {dir_path}"
                print(error_msg)
                return ("", error_msg)
        except Exception as e:
            error_msg = f"错误：目录创建失败: {str(e)}"
            print(error_msg)
            return ("", error_msg)

        # Write binary data
        try:
            bytes_written = save_binary_data(binary_data, full_path)
            if bytes_written > 0:
                print(f"DCI file saved successfully: {final_filename} ({bytes_written} bytes)")
                print(f"Full path: {full_path}")
                return (final_filename, full_path)
            else:
                error_msg = f"错误：文件保存失败，写入0字节: {full_path}"
                print(error_msg)
                return ("", error_msg)
        except Exception as e:
            error_msg = f"错误：文件写入失败: {str(e)} (路径: {full_path})"
            print(error_msg)
            return ("", error_msg)

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
