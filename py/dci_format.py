import struct
import os
from typing import List, Dict, Optional, Union
from io import BytesIO
from PIL import Image
import tempfile
import re


class DCIFile:
    """DCI (DSG Combined Icons) file format implementation"""

    MAGIC = b'DCI\x00'  # Magic header
    VERSION = 1

    # File types
    FILE_TYPE_RESERVED = 0
    FILE_TYPE_FILE = 1
    FILE_TYPE_DIRECTORY = 2
    FILE_TYPE_LINK = 3

    def __init__(self):
        self.files = []

    def add_file(self, name: str, content: bytes, file_type: int = FILE_TYPE_FILE):
        """Add a file to the DCI archive"""
        if len(name.encode('utf-8')) > 62:  # 63 bytes - 1 for null terminator
            raise ValueError(f"File name too long: {name}")

        if '/' in name:
            raise ValueError(f"File name cannot contain '/': {name}")

        self.files.append({
            'name': name,
            'content': content,
            'type': file_type
        })

    def add_directory(self, name: str, files: List[Dict]):
        """Add a directory with files to the DCI archive"""
        # Create directory content by packing all files in it
        dir_content = BytesIO()

        # Sort files by name (natural sort)
        sorted_files = sorted(files, key=lambda x: self._natural_sort_key(x['name']))

        for file_info in sorted_files:
            # Write file metadata
            file_name_bytes = file_info['name'].encode('utf-8')
            if len(file_name_bytes) > 62:
                raise ValueError(f"File name too long: {file_info['name']}")

            # File type (1 byte)
            dir_content.write(struct.pack('<B', file_info.get('type', self.FILE_TYPE_FILE)))

            # File name (63 bytes, null-terminated)
            name_padded = file_name_bytes + b'\x00' * (63 - len(file_name_bytes))
            dir_content.write(name_padded)

            # Content size (8 bytes)
            content = file_info['content']
            dir_content.write(struct.pack('<Q', len(content)))

            # Content
            dir_content.write(content)

        self.add_file(name, dir_content.getvalue(), self.FILE_TYPE_DIRECTORY)

    def _natural_sort_key(self, text: str):
        """Natural sorting key for filenames"""
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        return [convert(c) for c in re.split('([0-9]+)', text)]

    def write(self, output_path: str):
        """Write DCI file to disk"""
        binary_data = self.to_binary()
        with open(output_path, 'wb') as f:
            f.write(binary_data)

    def to_binary(self) -> bytes:
        """Generate DCI file as binary data"""
        output = BytesIO()

        # Write header
        output.write(self.MAGIC)
        output.write(struct.pack('<B', self.VERSION))

        # Sort files by name
        sorted_files = sorted(self.files, key=lambda x: self._natural_sort_key(x['name']))

        # Write file count (3 bytes)
        file_count = len(sorted_files)
        output.write(struct.pack('<I', file_count)[:3])  # Take only first 3 bytes

        # Write file metadata and content
        for file_info in sorted_files:
            # File type (1 byte)
            output.write(struct.pack('<B', file_info['type']))

            # File name (63 bytes, null-terminated)
            file_name_bytes = file_info['name'].encode('utf-8')
            name_padded = file_name_bytes + b'\x00' * (63 - len(file_name_bytes))
            output.write(name_padded)

            # Content size (8 bytes)
            content = file_info['content']
            output.write(struct.pack('<Q', len(content)))

            # Content
            output.write(content)

        return output.getvalue()


class DCIIconBuilder:
    """Builder for DCI icon files following the icon specification"""

    ICON_STATES = ['normal', 'disabled', 'hover', 'pressed']
    TONE_TYPES = ['universal', 'light', 'dark']
    SUPPORTED_FORMATS = ['png', 'jpg', 'webp']

    def __init__(self):
        self.dci = DCIFile()
        self.directory_structure = {}  # Track directory structure

    def add_icon_image(self, image: Image.Image, size: int, state: str = 'normal',
                      tone: str = 'universal', scale: float = 1.0, format: str = 'webp', quality: int = 90,
                      webp_lossless: bool = False, webp_alpha_quality: int = 100, png_compress_level: int = 6):
        """Add an icon image for specific state, tone, and scale"""

        if state not in self.ICON_STATES:
            raise ValueError(f"Invalid state: {state}. Must be one of {self.ICON_STATES}")

        if tone not in self.TONE_TYPES:
            raise ValueError(f"Invalid tone: {tone}. Must be one of {self.TONE_TYPES}")

        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Invalid format: {format}. Must be one of {self.SUPPORTED_FORMATS}")

        # Calculate actual size with scale
        actual_size = int(size * scale)

        # Resize image to target size
        resized_image = image.resize((actual_size, actual_size), Image.Resampling.LANCZOS)

        # Convert to bytes
        img_bytes = BytesIO()
        if format == 'webp':
            # WebP advanced settings
            if webp_lossless:
                # Lossless WebP
                resized_image.save(img_bytes, format='WEBP', lossless=True)
            else:
                # Standard lossy WebP with alpha quality control
                if resized_image.mode == 'RGBA':
                    resized_image.save(img_bytes, format='WEBP', quality=quality, alpha_quality=webp_alpha_quality)
                else:
                    resized_image.save(img_bytes, format='WEBP', quality=quality)
        elif format == 'png':
            # PNG with compression level control
            resized_image.save(img_bytes, format='PNG', compress_level=png_compress_level)
        elif format == 'jpg':
            # Convert to RGB if necessary for JPEG
            if resized_image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', resized_image.size, (255, 255, 255))
                if resized_image.mode == 'P':
                    resized_image = resized_image.convert('RGBA')
                rgb_image.paste(resized_image, mask=resized_image.split()[-1] if resized_image.mode in ('RGBA', 'LA') else None)
                resized_image = rgb_image
            resized_image.save(img_bytes, format='JPEG', quality=quality)

        img_content = img_bytes.getvalue()

        # Handle universal tone type
        if tone == 'universal':
            # Store image in light directory
            self._add_icon_image_internal(image, img_content, size, state, 'light', scale, format)
            # Create symlink in dark directory
            self._add_icon_symlink(size, state, 'light', 'dark', scale, format)
        else:
            # Normal processing for light/dark tones
            self._add_icon_image_internal(image, img_content, size, state, tone, scale, format)

    def _add_icon_image_internal(self, image: Image.Image, img_content: bytes, size: int, state: str,
                                tone: str, scale: float, format: str):
        """Internal method to add icon image to structure"""
        # Create directory structure: size/state.tone/scale/1.0p.-1.0_0_0_0_0_0_0.format
        size_dir = str(size)
        state_tone_dir = f"{state}.{tone}"
        # Format scale to remove unnecessary decimal places
        scale_dir = f"{scale:g}"

        # Layer file: priority.padding.palette.hue.saturation.brightness.red.green.blue.alpha.format
        layer_filename = f"1.0p.-1.0_0_0_0_0_0_0.{format}"

        # Build nested directory structure
        self._add_to_structure(size_dir, state_tone_dir, scale_dir, layer_filename, img_content)

    def _add_icon_symlink(self, size: int, state: str, source_tone: str, target_tone: str, scale: float, format: str):
        """Add a symlink from target_tone directory to source_tone directory"""
        size_dir = str(size)
        source_state_tone_dir = f"{state}.{source_tone}"
        target_state_tone_dir = f"{state}.{target_tone}"
        scale_dir = f"{scale:g}"
        layer_filename = f"1.0p.-1.0_0_0_0_0_0_0.{format}"

        # Create symlink path: ../../state.source_tone/scale/filename
        # Need to go up two levels: from scale_dir to state_tone_dir, then to size_dir
        symlink_target = f"../../{source_state_tone_dir}/{scale_dir}/{layer_filename}"

        # Add symlink to target directory structure
        self._add_symlink_to_structure(size_dir, target_state_tone_dir, scale_dir, layer_filename, symlink_target)

    def _add_to_structure(self, size_dir: str, state_tone_dir: str,
                         scale_dir: str, filename: str, content: bytes):
        """Add file to the directory structure"""

        # Initialize structure if needed
        if size_dir not in self.directory_structure:
            self.directory_structure[size_dir] = {}

        if state_tone_dir not in self.directory_structure[size_dir]:
            self.directory_structure[size_dir][state_tone_dir] = {}

        if scale_dir not in self.directory_structure[size_dir][state_tone_dir]:
            self.directory_structure[size_dir][state_tone_dir][scale_dir] = {}

        # Add the file
        self.directory_structure[size_dir][state_tone_dir][scale_dir][filename] = {
            'type': 'file',
            'content': content
        }

    def _add_symlink_to_structure(self, size_dir: str, state_tone_dir: str,
                                 scale_dir: str, filename: str, target_path: str):
        """Add symlink to the directory structure"""

        # Initialize structure if needed
        if size_dir not in self.directory_structure:
            self.directory_structure[size_dir] = {}

        if state_tone_dir not in self.directory_structure[size_dir]:
            self.directory_structure[size_dir][state_tone_dir] = {}

        if scale_dir not in self.directory_structure[size_dir][state_tone_dir]:
            self.directory_structure[size_dir][state_tone_dir][scale_dir] = {}

        # Add the symlink
        self.directory_structure[size_dir][state_tone_dir][scale_dir][filename] = {
            'type': 'symlink',
            'target': target_path
        }

    def build(self, output_path: str):
        """Build and write the DCI file"""
        binary_data = self.to_binary()
        with open(output_path, 'wb') as f:
            f.write(binary_data)

    def to_binary(self) -> bytes:
        """Build and return the DCI file as binary data"""
        # Convert directory structure to DCI format
        for size_dir, size_content in self.directory_structure.items():
            state_tone_dirs = []

            for state_tone_dir, state_tone_content in size_content.items():
                scale_dirs = []

                for scale_dir, scale_content in state_tone_content.items():
                    # Create files for this scale directory
                    scale_files = []
                    for filename, file_info in scale_content.items():
                        if isinstance(file_info, dict):
                            if file_info['type'] == 'file':
                                scale_files.append({
                                    'name': filename,
                                    'content': file_info['content'],
                                    'type': DCIFile.FILE_TYPE_FILE
                                })
                            elif file_info['type'] == 'symlink':
                                # Create symlink content (target path as UTF-8 bytes)
                                symlink_content = file_info['target'].encode('utf-8')
                                scale_files.append({
                                    'name': filename,
                                    'content': symlink_content,
                                    'type': DCIFile.FILE_TYPE_LINK
                                })
                        else:
                            # Backward compatibility: treat as file content
                            scale_files.append({
                                'name': filename,
                                'content': file_info,
                                'type': DCIFile.FILE_TYPE_FILE
                            })

                    # Create scale directory
                    scale_dir_content = self._create_directory_content(scale_files)
                    scale_dirs.append({
                        'name': scale_dir,
                        'content': scale_dir_content,
                        'type': DCIFile.FILE_TYPE_DIRECTORY
                    })

                # Create state.tone directory
                state_tone_dir_content = self._create_directory_content(scale_dirs)
                state_tone_dirs.append({
                    'name': state_tone_dir,
                    'content': state_tone_dir_content,
                    'type': DCIFile.FILE_TYPE_DIRECTORY
                })

            # Add size directory to DCI
            self.dci.add_directory(size_dir, state_tone_dirs)

        # Return the DCI file as binary data
        return self.dci.to_binary()

    def _create_directory_content(self, files: List[Dict]) -> bytes:
        """Create directory content from file list"""
        dir_content = BytesIO()

        # Sort files by name
        sorted_files = sorted(files, key=lambda x: self.dci._natural_sort_key(x['name']))

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


def create_dci_icon(image: Image.Image, output_path: str, size: int = 256,
                   states: List[str] = None, tones: List[str] = None,
                   scales: List[float] = None, format: str = 'webp', quality: int = 90,
                   webp_lossless: bool = False, webp_alpha_quality: int = 100, png_compress_level: int = 6):
    """Create a DCI icon file from an image"""

    if states is None:
        states = ['normal']
    if tones is None:
        tones = ['universal']
    if scales is None:
        scales = [1.0, 1.25, 1.5, 2.0]

    builder = DCIIconBuilder()

    # Add images for all combinations of states, tones, and scales
    for state in states:
        for tone in tones:
            for scale in scales:
                builder.add_icon_image(image, size, state, tone, scale, format, quality,
                                     webp_lossless, webp_alpha_quality, png_compress_level)

    builder.build(output_path)
