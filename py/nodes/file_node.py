import struct
import os
import base64
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
    """ComfyUI node for combining multiple DCI images into a DCI file with composable design"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                t("dci_binary_data"): ("BINARY_DATA",),
                t("dci_image_1"): ("DCI_IMAGE_DATA",),
                t("dci_image_2"): ("DCI_IMAGE_DATA",),
                t("dci_image_3"): ("DCI_IMAGE_DATA",),
                t("dci_image_4"): ("DCI_IMAGE_DATA",),
            }
        }

    RETURN_TYPES = ("BINARY_DATA",)
    RETURN_NAMES = (t("dci_binary_data"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Export')}"

    def _execute(self, **kwargs):
        """Combine multiple DCI images into a DCI file with composable design"""
        # Extract existing DCI binary data if provided
        # Try both translated and original parameter names for compatibility
        existing_binary_data = kwargs.get(t("dci_binary_data")) if t("dci_binary_data") in kwargs else kwargs.get("dci_binary_data")

        # Collect all DCI image data from the 4 available slots
        dci_images = []
        for i in range(1, 5):  # Support 4 images per node
            # Try both translated and original parameter names for compatibility
            dci_image_key_translated = t(f"dci_image_{i}")
            dci_image_key_original = f"dci_image_{i}"
            dci_image = kwargs.get(dci_image_key_translated) if dci_image_key_translated in kwargs else kwargs.get(dci_image_key_original)
            if dci_image:
                dci_images.append(dci_image)

        # If no new images and no existing data, return empty
        if not dci_images and not existing_binary_data:
            print("No DCI images or existing binary data provided")
            return (b"",)

        # If no new images but have existing data, return existing data
        if not dci_images and existing_binary_data:
            print(f"No new images, returning existing DCI data: {len(existing_binary_data)} bytes")
            return (existing_binary_data,)

        # If we have new images, create a new DCI file and merge with existing data if present
        if dci_images:
            # Create DCI file structure
            dci_file = DCIFile()
            directory_structure = {}

            # First, parse existing DCI data if provided
            if existing_binary_data:
                existing_structure = self._parse_existing_dci_data(existing_binary_data)
                # Merge existing structure into our directory structure
                for size_dir, size_content in existing_structure.items():
                    if size_dir not in directory_structure:
                        directory_structure[size_dir] = {}
                    for state_tone_dir, state_tone_content in size_content.items():
                        if state_tone_dir not in directory_structure[size_dir]:
                            directory_structure[size_dir][state_tone_dir] = {}
                        for scale_dir, scale_content in state_tone_content.items():
                            if scale_dir not in directory_structure[size_dir][state_tone_dir]:
                                directory_structure[size_dir][state_tone_dir][scale_dir] = {}
                            # Merge files from existing data
                            for filename, file_content in scale_content.items():
                                directory_structure[size_dir][state_tone_dir][scale_dir][filename] = file_content

            # Then, add new DCI images (they will overwrite existing files with same path)
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

            if existing_binary_data:
                print(f"Merged DCI file: {len(dci_images)} new images + existing data = {len(binary_data)} bytes total")
            else:
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

    def _parse_existing_dci_data(self, binary_data):
        """Parse existing DCI binary data to extract directory structure"""
        try:
            # Import DCIReader here to avoid circular imports
            from ..dci_reader import DCIReader

            # Create DCIReader instance with binary data
            reader = DCIReader(binary_data=binary_data)

            # Read and parse the DCI file
            if not reader.read():
                print("Failed to read existing DCI data")
                return {}

            # Extract directory structure from the reader
            directory_structure = {}

            # Get all icon images from the existing DCI data
            existing_images = reader.get_icon_images()

            for image_info in existing_images:
                # Build path from image metadata
                size = image_info.get('size', 256)
                state = image_info.get('state', 'normal')
                tone = image_info.get('tone', 'light')
                scale = image_info.get('scale', 1.0)

                # Format path components
                size_dir = str(size)
                state_tone_dir = f"{state}.{tone}"
                scale_dir = str(scale) if scale == int(scale) else f"{scale:.2f}".rstrip('0').rstrip('.')

                # Get filename from metadata or use default
                filename = image_info.get('filename', '1.webp')

                # Build nested structure
                if size_dir not in directory_structure:
                    directory_structure[size_dir] = {}
                if state_tone_dir not in directory_structure[size_dir]:
                    directory_structure[size_dir][state_tone_dir] = {}
                if scale_dir not in directory_structure[size_dir][state_tone_dir]:
                    directory_structure[size_dir][state_tone_dir][scale_dir] = {}

                # Store file content
                directory_structure[size_dir][state_tone_dir][scale_dir][filename] = image_info.get('content', b'')

            return directory_structure

        except Exception as e:
            print(f"Error parsing existing DCI data: {str(e)}")
            return {}


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
        file_path = kwargs.get(t("file_path")) if t("file_path") in kwargs else kwargs.get("file_path", "")

        return self._execute_impl(file_path)

    def _execute_impl(self, file_path=""):
        """Load binary file from file system"""
        if not file_path:
            print("No file path provided")
            return (b"", "")

        binary_data = load_binary_data(file_path)
        if binary_data is not None:
            print(f"Loaded binary file: {file_path} ({len(binary_data)} bytes)")
            return (binary_data, file_path)
        else:
            print(f"Failed to load binary file: {file_path}")
            return (b"", file_path)


class BinaryFileSaver(BaseNode):
    """ComfyUI node for saving binary data to file system with prefix and suffix support"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("binary_data"): ("BINARY_DATA",),
                t("file_name"): ("STRING", {"default": "binary_file", "multiline": False}),
            },
            "optional": {
                t("output_directory"): ("STRING", {"default": "", "multiline": False}),
                t("filename_prefix"): ("STRING", {"default": "", "multiline": False}),
                t("filename_suffix"): ("STRING", {"default": "", "multiline": False}),
                t("remove_extension"): ("BOOLEAN", {"default": False}),
                t("allow_overwrite"): ("BOOLEAN", {"default": False}),
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
        binary_data = kwargs.get(t("binary_data")) if t("binary_data") in kwargs else kwargs.get("binary_data")
        file_name = kwargs.get(t("file_name")) if t("file_name") in kwargs else kwargs.get("file_name")
        output_directory = kwargs.get(t("output_directory")) if t("output_directory") in kwargs else kwargs.get("output_directory", "")
        filename_prefix = kwargs.get(t("filename_prefix")) if t("filename_prefix") in kwargs else kwargs.get("filename_prefix", "")
        filename_suffix = kwargs.get(t("filename_suffix")) if t("filename_suffix") in kwargs else kwargs.get("filename_suffix", "")
        remove_extension = kwargs.get(t("remove_extension")) if t("remove_extension") in kwargs else kwargs.get("remove_extension", False)
        allow_overwrite = kwargs.get(t("allow_overwrite")) if t("allow_overwrite") in kwargs else kwargs.get("allow_overwrite", False)

        return self._execute_impl(binary_data, file_name, output_directory, filename_prefix, filename_suffix, remove_extension, allow_overwrite)

    def _execute_impl(self, binary_data, file_name, output_directory="", filename_prefix="", filename_suffix="", remove_extension=False, allow_overwrite=False):
        """Save binary data to file system with prefix and suffix support"""
        # Check if binary_data is valid
        if binary_data is None:
            error_msg = "错误：未提供二进制数据 (None)"
            print(error_msg)
            return (error_msg,)

        if isinstance(binary_data, bytes) and len(binary_data) == 0:
            error_msg = "错误：提供的二进制数据为空"
            print(error_msg)
            return (error_msg,)

        if not isinstance(binary_data, bytes):
            error_msg = f"错误：无效的二进制数据类型: {type(binary_data)}"
            print(error_msg)
            return (error_msg,)

        print(f"Processing binary data: {len(binary_data)} bytes")

        # Parse and clean up file name
        try:
            parsed_filename = self._parse_filename(file_name)
        except Exception as e:
            error_msg = f"错误：文件名解析失败: {str(e)}"
            print(error_msg)
            return (error_msg,)

        # Apply prefix and suffix
        try:
            final_filename = self._apply_prefix_suffix(parsed_filename, filename_prefix, filename_suffix, remove_extension)
        except Exception as e:
            error_msg = f"错误：文件名前缀后缀处理失败: {str(e)}"
            print(error_msg)
            return (error_msg,)

        # Determine output directory
        try:
            if output_directory:
                # Use specified output directory, normalize and clean the path
                output_dir = os.path.normpath(output_directory.strip())
                print(f"Normalized output directory: {output_dir}")
                # Ensure the directory exists
                if not ensure_directory(output_dir):
                    error_msg = f"错误：无法创建输出目录: {output_dir}"
                    print(error_msg)
                    return (error_msg,)
            else:
                # Use ComfyUI default output directory
                output_dir = get_output_directory()
        except Exception as e:
            error_msg = f"错误：输出目录处理失败: {str(e)}"
            print(error_msg)
            return (error_msg,)

        # Create full path
        try:
            full_path = os.path.join(output_dir, final_filename)
            print(f"Target file path: {full_path}")
        except Exception as e:
            error_msg = f"错误：文件路径构建失败: {str(e)}"
            print(error_msg)
            return (error_msg,)

        # Check if file exists and overwrite is not allowed
        if os.path.exists(full_path) and not allow_overwrite:
            error_msg = f"错误：文件已存在且不允许覆盖: {full_path}"
            print(error_msg)
            return (error_msg,)

        # Ensure directory exists
        try:
            dir_path = os.path.dirname(full_path)
            if dir_path and not ensure_directory(dir_path):
                error_msg = f"错误：无法创建文件目录: {dir_path}"
                print(error_msg)
                return (error_msg,)
        except Exception as e:
            error_msg = f"错误：目录创建失败: {str(e)}"
            print(error_msg)
            return (error_msg,)

        # Write binary data
        try:
            bytes_written = save_binary_data(binary_data, full_path)
            if bytes_written > 0:
                print(f"File saved successfully: {final_filename} ({bytes_written} bytes)")
                print(f"Full path: {full_path}")
                return (full_path,)
            else:
                error_msg = f"错误：文件保存失败，写入0字节: {full_path}"
                print(error_msg)
                return (error_msg,)
        except Exception as e:
            error_msg = f"错误：文件写入失败: {str(e)} (路径: {full_path})"
            print(error_msg)
            return (error_msg,)

    def _parse_filename(self, input_filename):
        """Parse filename from input string, handling both filenames and full paths"""
        if not input_filename:
            return "binary_file"

        # Normalize path separators for cross-platform compatibility
        normalized_path = input_filename.replace('\\', '/')

        # Extract basename from path (handles both Windows and Linux separators)
        basename = os.path.basename(normalized_path)

        # If basename is empty (input was just a path separator), use default
        if not basename:
            return "binary_file"

        # Clean the filename (remove invalid characters)
        cleaned_filename = clean_file_name(basename)

        return cleaned_filename

    def _apply_prefix_suffix(self, filename, prefix, suffix, remove_extension=False):
        """Apply prefix and suffix to filename with optional extension removal"""

        # If remove_extension is True, remove the extension first
        if remove_extension:
            # Handle complex extensions like .tar.gz, .tar.bz2, etc.
            complex_extensions = ['.tar.gz', '.tar.bz2', '.tar.xz', '.tar.Z', '.tar.lz', '.tar.lzma']

            # Check for complex extensions first
            name_part = filename
            for ext in complex_extensions:
                if filename.lower().endswith(ext.lower()):
                    name_part = filename[:-len(ext)]
                    break
            else:
                # No complex extension found, use standard splitext
                name_part, ext = os.path.splitext(filename)
                # Special handling for hidden files (files starting with .)
                if filename.startswith('.') and '.' not in filename[1:]:
                    # This is a hidden file without extension, keep the whole name
                    name_part = filename

            final_name = name_part
        else:
            # Keep the entire filename as is
            final_name = filename

        # Apply prefix and suffix unconditionally
        if prefix:
            final_name = f"{prefix}{final_name}"
        if suffix:
            final_name = f"{final_name}{suffix}"

        return final_name


class Base64Decoder(BaseNode):
    """ComfyUI node for decoding binary data from base64 string"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("base64_data"): ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("BINARY_DATA",)
    RETURN_NAMES = (t("binary_data"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Files')}"

    def _execute(self, **kwargs):
        """Decode binary data from base64 string"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        base64_data = kwargs.get(t("base64_data")) if t("base64_data") in kwargs else kwargs.get("base64_data", "")

        return self._execute_impl(base64_data)

    def _execute_impl(self, base64_data=""):
        """Decode binary data from base64 string"""
        if not base64_data:
            print("No base64 data provided")
            return (b"",)

        try:
            # Remove whitespace and newlines
            cleaned_data = ''.join(base64_data.split())

            # Decode base64
            binary_data = base64.b64decode(cleaned_data)
            print(f"Decoded base64 data: {len(binary_data)} bytes")
            return (binary_data,)

        except Exception as e:
            print(f"Failed to decode base64 data: {str(e)}")
            return (b"",)


class Base64Encoder(BaseNode):
    """ComfyUI node for encoding binary data to base64 string"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("binary_data"): ("BINARY_DATA",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = (t("base64_data"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Files')}"

    def _execute(self, **kwargs):
        """Encode binary data to base64 string"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        binary_data = kwargs.get(t("binary_data")) if t("binary_data") in kwargs else kwargs.get("binary_data")

        return self._execute_impl(binary_data)

    def _execute_impl(self, binary_data):
        """Encode binary data to base64 string"""
        if binary_data is None or len(binary_data) == 0:
            print("No binary data provided for encoding")
            return ("",)

        try:
            # Encode to base64
            base64_data = base64.b64encode(binary_data).decode('utf-8')
            print(f"Encoded binary data to base64: {len(binary_data)} bytes -> {len(base64_data)} characters")
            return (base64_data,)

        except Exception as e:
            print(f"Failed to encode binary data to base64: {str(e)}")
            return ("",)
