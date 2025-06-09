import torch
import numpy as np
from PIL import Image
import os
import tempfile
import struct
from io import BytesIO

# Try relative imports first, fall back to absolute imports
try:
    from .dci_format import create_dci_icon, DCIIconBuilder, DCIFile
    from .dci_reader import DCIReader, DCIPreviewGenerator
except ImportError:
    # Fallback for when module is loaded directly
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from dci_format import create_dci_icon, DCIIconBuilder, DCIFile
    from dci_reader import DCIReader, DCIPreviewGenerator


class DCIPreviewNode:
    """ComfyUI node for previewing DCI file contents"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dci_binary_data": ("BINARY_DATA",),
            },
            "optional": {
                "grid_columns": ("INT", {"default": 4, "min": 1, "max": 10, "step": 1}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "preview_dci"
    CATEGORY = "DCI/Preview"
    OUTPUT_NODE = True

    def preview_dci(self, dci_binary_data, grid_columns=4):
        """Preview DCI file contents with in-node display"""

        try:
            # Use binary data
            reader = DCIReader(binary_data=dci_binary_data)
            source_name = "binary_data"

            # Read DCI data
            if not reader.read():
                return {"ui": {"text": ["Failed to read DCI data"]}}

            # Extract images
            images = reader.get_icon_images()
            if not images:
                return {"ui": {"text": ["No images found in DCI file"]}}

            # Generate preview
            generator = DCIPreviewGenerator()
            preview_image = generator.create_preview_grid(images, grid_columns)

            # Convert PIL image to base64 for UI display
            preview_base64 = self._pil_to_base64(preview_image)

            # Generate metadata summary (always show metadata)
            summary = generator.create_metadata_summary(images)
            summary_text = self._format_summary(summary, source_name)

            # Create UI output with image and text
            ui_output = {
                "ui": {
                    "images": [preview_base64],
                    "text": [summary_text]
                }
            }

            print(f"DCI preview generated: {len(images)} images found")
            return ui_output

        except Exception as e:
            print(f"Error previewing DCI file: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"ui": {"text": [f"Error: {str(e)}"]}}

    def _pil_to_base64(self, pil_image):
        """Convert PIL image to base64 string for UI display"""
        import base64
        import hashlib
        import time

        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Save to bytes buffer
        buffer = BytesIO()
        pil_image.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()

        # Generate unique filename
        timestamp = str(int(time.time()))
        hash_obj = hashlib.md5(img_bytes)
        filename = f"dci_preview_{timestamp}_{hash_obj.hexdigest()[:8]}.png"

        # Save to temp directory for ComfyUI
        try:
            import folder_paths
            temp_dir = folder_paths.get_temp_directory()
        except:
            temp_dir = tempfile.gettempdir()

        temp_path = os.path.join(temp_dir, filename)
        with open(temp_path, 'wb') as f:
            f.write(img_bytes)

        # Return in format expected by ComfyUI
        return {
            "filename": filename,
            "subfolder": "",
            "type": "temp"
        }

    def _format_summary(self, summary, source_name):
        """Format metadata summary as text"""
        if not summary:
            return "No metadata available"

        lines = [
            f"📁 DCI Source: {source_name}",
            f"🖼️  Total Images: {summary['total_images']}",
            f"📊 Total File Size: {summary['total_file_size']} bytes",
            "",
            f"📏 Icon Sizes: {', '.join(map(str, summary['sizes']))}",
            f"🎭 States: {', '.join(summary['states'])}",
            f"🎨 Tones: {', '.join(summary['tones'])}",
            f"🔍 Scale Factors: {', '.join(map(str, summary['scales']))}",
            f"🗂️  Formats: {', '.join(summary['formats'])}",
        ]

        return "\n".join(lines)


class DCIImage:
    """ComfyUI node for creating DCI image metadata and data"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "icon_size": ("INT", {"default": 256, "min": 16, "max": 1024, "step": 1}),
                "icon_state": (["normal", "disabled", "hover", "pressed"], {"default": "normal"}),
                "tone_type": (["light", "dark"], {"default": "dark"}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "image_format": (["webp", "png", "jpg"], {"default": "webp"}),
            }
        }

    RETURN_TYPES = ("DCI_IMAGE_DATA",)
    RETURN_NAMES = ("dci_image_data",)
    FUNCTION = "create_dci_image"
    CATEGORY = "DCI/Export"

    def create_dci_image(self, image, icon_size, icon_state, tone_type, scale, image_format):
        """Create DCI image metadata and data"""

        try:
            # Convert ComfyUI image tensor to PIL Image
            if len(image.shape) == 4:
                img_array = image[0].cpu().numpy()
            else:
                img_array = image.cpu().numpy()

            # Convert from 0-1 range to 0-255 range
            img_array = (img_array * 255).astype(np.uint8)

            # Convert to PIL Image
            if img_array.shape[2] == 3:
                pil_image = Image.fromarray(img_array, 'RGB')
            elif img_array.shape[2] == 4:
                pil_image = Image.fromarray(img_array, 'RGBA')
            else:
                pil_image = Image.fromarray(img_array[:, :, 0], 'L').convert('RGB')

            # Calculate actual size with scale
            actual_size = int(icon_size * scale)

            # Resize image to target size
            resized_image = pil_image.resize((actual_size, actual_size), Image.Resampling.LANCZOS)

            # Convert to bytes
            img_bytes = BytesIO()
            if image_format == 'webp':
                resized_image.save(img_bytes, format='WEBP', quality=90)
            elif image_format == 'png':
                resized_image.save(img_bytes, format='PNG')
            elif image_format == 'jpg':
                # Convert to RGB if necessary for JPEG
                if resized_image.mode in ('RGBA', 'LA', 'P'):
                    rgb_image = Image.new('RGB', resized_image.size, (255, 255, 255))
                    if resized_image.mode == 'P':
                        resized_image = resized_image.convert('RGBA')
                    rgb_image.paste(resized_image, mask=resized_image.split()[-1] if resized_image.mode in ('RGBA', 'LA') else None)
                    resized_image = rgb_image
                resized_image.save(img_bytes, format='JPEG', quality=90)

            img_content = img_bytes.getvalue()

            # Create DCI path: size/state.tone/scale/1.0.0.0.0.0.0.0.0.0.format
            # Format scale to remove unnecessary decimal places
            scale_str = f"{scale:g}"  # This removes trailing zeros
            dci_path = f"{icon_size}/{icon_state}.{tone_type}/{scale_str}/1.0.0.0.0.0.0.0.0.0.{image_format}"

            # Create metadata dictionary
            dci_image_data = {
                'path': dci_path,
                'content': img_content,
                'size': icon_size,
                'state': icon_state,
                'tone': tone_type,
                'scale': scale,
                'format': image_format,
                'actual_size': actual_size,
                'file_size': len(img_content)
            }

            print(f"Created DCI image: {dci_path} ({len(img_content)} bytes)")
            return (dci_image_data,)

        except Exception as e:
            print(f"Error creating DCI image: {str(e)}")
            import traceback
            traceback.print_exc()
            return ({},)


class DCIFileNode:
    """ComfyUI node for combining multiple DCI images into a DCI file"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "dci_image_1": ("DCI_IMAGE_DATA",),
                "dci_image_2": ("DCI_IMAGE_DATA",),
                "dci_image_3": ("DCI_IMAGE_DATA",),
                "dci_image_4": ("DCI_IMAGE_DATA",),
                "dci_image_5": ("DCI_IMAGE_DATA",),
                "dci_image_6": ("DCI_IMAGE_DATA",),
                "dci_image_7": ("DCI_IMAGE_DATA",),
                "dci_image_8": ("DCI_IMAGE_DATA",),
                "dci_image_9": ("DCI_IMAGE_DATA",),
                "dci_image_10": ("DCI_IMAGE_DATA",),
                "dci_image_11": ("DCI_IMAGE_DATA",),
                "dci_image_12": ("DCI_IMAGE_DATA",),
            }
        }

    RETURN_TYPES = ("BINARY_DATA",)
    RETURN_NAMES = ("dci_binary_data",)
    FUNCTION = "create_dci_file"
    CATEGORY = "DCI/Export"

    def create_dci_file(self, **kwargs):
        """Combine multiple DCI images into a DCI file"""

        try:
            # Collect all DCI image data
            dci_images = []
            for i in range(1, 13):  # Support up to 12 images
                dci_image_key = f"dci_image_{i}"
                if dci_image_key in kwargs and kwargs[dci_image_key]:
                    dci_images.append(kwargs[dci_image_key])

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

        except Exception as e:
            print(f"Error creating DCI file: {str(e)}")
            import traceback
            traceback.print_exc()
            return (b"",)

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


class BinaryFileLoader:
    """ComfyUI node for loading binary files from file system"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "file_path": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("BINARY_DATA", "STRING")
    RETURN_NAMES = ("binary_data", "file_path")
    FUNCTION = "load_binary_file"
    CATEGORY = "DCI/Files"

    def load_binary_file(self, file_path=""):
        """Load binary file from file system"""

        try:
            if not file_path or not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return (None, "")

            # Read binary file
            with open(file_path, 'rb') as f:
                content = f.read()

            # Get file info
            filename = os.path.basename(file_path)
            file_size = len(content)

            print(f"Loaded binary file: {filename} ({file_size} bytes)")
            # Return the binary content directly, not wrapped in a dictionary
            return (content, file_path)

        except Exception as e:
            print(f"Error loading binary file: {str(e)}")
            import traceback
            traceback.print_exc()
            return (None, "")


class BinaryFileSaver:
    """ComfyUI node for saving binary data to file system"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "binary_data": ("BINARY_DATA",),
                "file_name": ("STRING", {"default": "binary_file", "multiline": False}),
            },
            "optional": {
                "output_directory": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    FUNCTION = "save_binary_file"
    CATEGORY = "DCI/Files"
    OUTPUT_NODE = True

    def save_binary_file(self, binary_data, file_name, output_directory=""):
        """Save binary data to file system"""

        try:
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

            # Clean up file name (remove any path separators)
            clean_file_name = os.path.basename(file_name) if file_name else "binary_file"
            if not clean_file_name:
                clean_file_name = "binary_file"

            # Determine output directory
            if output_directory and os.path.exists(output_directory):
                output_dir = output_directory
            else:
                # Use ComfyUI output directory or temp directory
                try:
                    import folder_paths
                    output_dir = folder_paths.get_output_directory()
                    print(f"Using ComfyUI output directory: {output_dir}")
                except ImportError:
                    # ComfyUI folder_paths not available
                    output_dir = tempfile.gettempdir()
                    print(f"ComfyUI not available, using temp directory: {output_dir}")
                except Exception as e:
                    # Any other folder_paths related errors
                    output_dir = tempfile.gettempdir()
                    print(f"Error accessing ComfyUI output directory: {e}, using temp directory: {output_dir}")

            # Create full path
            full_path = os.path.join(output_dir, clean_file_name)
            print(f"Target file path: {full_path}")

            # Ensure directory exists
            dir_path = os.path.dirname(full_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
                print(f"Ensured directory exists: {dir_path}")

            # Write binary data
            with open(full_path, 'wb') as f:
                bytes_written = f.write(binary_data)
                print(f"Wrote {bytes_written} bytes to file")

            # Verify file was written correctly
            if os.path.exists(full_path):
                actual_size = os.path.getsize(full_path)
                print(f"File saved successfully: {full_path} ({actual_size} bytes)")
                return (full_path,)
            else:
                print(f"File was not created: {full_path}")
                return ("",)

        except Exception as e:
            print(f"Error saving binary file: {str(e)}")
            import traceback
            traceback.print_exc()
            return ("",)
