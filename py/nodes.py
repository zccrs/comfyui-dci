import torch
import numpy as np
from PIL import Image
import os
import tempfile
import struct
from io import BytesIO
from .dci_format import create_dci_icon, DCIIconBuilder, DCIFile
from .dci_reader import DCIReader, DCIPreviewGenerator


class DCIImageExporter:
    """ComfyUI node for exporting images to DCI format"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "filename": ("STRING", {"default": "icon", "multiline": False}),
                "icon_size": ("INT", {"default": 256, "min": 16, "max": 1024, "step": 1}),
                "icon_state": (["normal", "disabled", "hover", "pressed"], {"default": "normal"}),
                "tone_type": (["light", "dark"], {"default": "dark"}),
                "image_format": (["webp", "png", "jpg"], {"default": "webp"}),
            },
            "optional": {
                "scale_factors": ("STRING", {"default": "1,2,3", "multiline": False}),
                "output_directory": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_path",)
    FUNCTION = "export_dci"
    CATEGORY = "DCI/Export"
    OUTPUT_NODE = True

    def export_dci(self, image, filename, icon_size, icon_state, tone_type,
                   image_format, scale_factors="1,2,3", output_directory=""):
        """Export image to DCI format"""

        try:
            # Convert ComfyUI image tensor to PIL Image
            # ComfyUI images are in format [batch, height, width, channels] with values 0-1
            if len(image.shape) == 4:
                # Take first image from batch
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
                # Convert grayscale to RGB
                pil_image = Image.fromarray(img_array[:, :, 0], 'L').convert('RGB')

            # Parse scale factors
            try:
                scales = [int(s.strip()) for s in scale_factors.split(',') if s.strip()]
                if not scales:
                    scales = [1, 2, 3]
            except ValueError:
                print(f"Invalid scale factors: {scale_factors}, using default [1,2,3]")
                scales = [1, 2, 3]

            # Determine output path
            if output_directory and os.path.exists(output_directory):
                output_path = os.path.join(output_directory, f"{filename}.dci")
            else:
                # Use ComfyUI's output directory or temp directory
                try:
                    import folder_paths
                    output_dir = folder_paths.get_output_directory()
                except ImportError:
                    # Fallback if ComfyUI folder_paths is not available
                    output_dir = tempfile.gettempdir()
                except Exception:
                    # Fallback for any other folder_paths related errors
                    output_dir = tempfile.gettempdir()
                output_path = os.path.join(output_dir, f"{filename}.dci")

            # Create DCI file
            builder = DCIIconBuilder()

            # Add images for all scale factors
            for scale in scales:
                builder.add_icon_image(
                    image=pil_image,
                    size=icon_size,
                    state=icon_state,
                    tone=tone_type,
                    scale=scale,
                    format=image_format
                )

            # Build and save DCI file
            builder.build(output_path)

            print(f"DCI file exported successfully: {output_path}")
            return (output_path,)

        except Exception as e:
            print(f"Error exporting DCI file: {str(e)}")
            import traceback
            traceback.print_exc()
            return ("",)


class DCIImageExporterAdvanced:
    """Advanced ComfyUI node for exporting images to DCI format with multiple states"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "filename": ("STRING", {"default": "icon", "multiline": False}),
                "icon_size": ("INT", {"default": 256, "min": 16, "max": 1024, "step": 1}),
                "image_format": (["webp", "png", "jpg"], {"default": "webp"}),
            },
            "optional": {
                "normal_image": ("IMAGE",),
                "disabled_image": ("IMAGE",),
                "hover_image": ("IMAGE",),
                "pressed_image": ("IMAGE",),
                "include_light_tone": ("BOOLEAN", {"default": False}),
                "include_dark_tone": ("BOOLEAN", {"default": True}),
                "scale_factors": ("STRING", {"default": "1,2,3", "multiline": False}),
                "output_directory": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_path",)
    FUNCTION = "export_dci_advanced"
    CATEGORY = "DCI/Export"
    OUTPUT_NODE = True

    def export_dci_advanced(self, image, filename, icon_size, image_format,
                           normal_image=None, disabled_image=None, hover_image=None, pressed_image=None,
                           include_light_tone=False, include_dark_tone=True,
                           scale_factors="1,2,3", output_directory=""):
        """Export images to DCI format with multiple states and tones"""

        try:
            # Parse scale factors
            try:
                scales = [int(s.strip()) for s in scale_factors.split(',') if s.strip()]
                if not scales:
                    scales = [1, 2, 3]
            except ValueError:
                print(f"Invalid scale factors: {scale_factors}, using default [1,2,3]")
                scales = [1, 2, 3]

            # Determine output path
            if output_directory and os.path.exists(output_directory):
                output_path = os.path.join(output_directory, f"{filename}.dci")
            else:
                try:
                    import folder_paths
                    output_dir = folder_paths.get_output_directory()
                except ImportError:
                    # Fallback if ComfyUI folder_paths is not available
                    output_dir = tempfile.gettempdir()
                except Exception:
                    # Fallback for any other folder_paths related errors
                    output_dir = tempfile.gettempdir()
                output_path = os.path.join(output_dir, f"{filename}.dci")

            # Create DCI builder
            builder = DCIIconBuilder()

            # Prepare state images
            state_images = {
                'normal': normal_image if normal_image is not None else image,
                'disabled': disabled_image,
                'hover': hover_image,
                'pressed': pressed_image
            }

            # Determine tones to include
            tones = []
            if include_dark_tone:
                tones.append('dark')
            if include_light_tone:
                tones.append('light')
            if not tones:
                tones = ['dark']  # Default to dark if none selected

            # Process each state and tone combination
            for state, state_image in state_images.items():
                if state_image is None:
                    continue

                # Convert tensor to PIL Image
                pil_image = self._tensor_to_pil(state_image)

                for tone in tones:
                    for scale in scales:
                        builder.add_icon_image(
                            image=pil_image,
                            size=icon_size,
                            state=state,
                            tone=tone,
                            scale=scale,
                            format=image_format
                        )

            # Build and save DCI file
            builder.build(output_path)

            print(f"Advanced DCI file exported successfully: {output_path}")
            return (output_path,)

        except Exception as e:
            print(f"Error exporting advanced DCI file: {str(e)}")
            import traceback
            traceback.print_exc()
            return ("",)

    def _tensor_to_pil(self, tensor):
        """Convert ComfyUI tensor to PIL Image"""
        if len(tensor.shape) == 4:
            img_array = tensor[0].cpu().numpy()
        else:
            img_array = tensor.cpu().numpy()

        img_array = (img_array * 255).astype(np.uint8)

        if img_array.shape[2] == 3:
            return Image.fromarray(img_array, 'RGB')
        elif img_array.shape[2] == 4:
            return Image.fromarray(img_array, 'RGBA')
        else:
            return Image.fromarray(img_array[:, :, 0], 'L').convert('RGB')


class DCIPreviewNode:
    """ComfyUI node for previewing DCI file contents"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "dci_file_path": ("STRING", {"default": "", "multiline": False}),
                "dci_binary_data": ("BINARY_DATA",),
                "grid_columns": ("INT", {"default": 4, "min": 1, "max": 10, "step": 1}),
                "show_metadata": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("preview_image", "metadata_summary")
    FUNCTION = "preview_dci"
    CATEGORY = "DCI/Preview"
    OUTPUT_NODE = True

    def preview_dci(self, grid_columns=4, show_metadata=True, dci_file_path="", dci_binary_data=None):
        """Preview DCI file contents"""

        try:
            # Determine input source
            if dci_binary_data is not None:
                # Use binary data
                reader = DCIReader(binary_data=dci_binary_data)
                source_name = "binary_data"
            elif dci_file_path and os.path.exists(dci_file_path):
                # Use file path
                reader = DCIReader(dci_file_path)
                source_name = os.path.basename(dci_file_path)
            else:
                return self._create_error_output("No DCI file path or binary data provided")

            # Read DCI data
            if not reader.read():
                return self._create_error_output("Failed to read DCI data")

            # Extract images
            images = reader.get_icon_images()
            if not images:
                return self._create_error_output("No images found in DCI file")

            # Generate preview
            generator = DCIPreviewGenerator()
            preview_image = generator.create_preview_grid(images, grid_columns)

            # Convert PIL image to ComfyUI tensor
            preview_tensor = self._pil_to_tensor(preview_image)

            # Generate metadata summary
            summary = generator.create_metadata_summary(images)
            summary_text = self._format_summary(summary, source_name)

            print(f"DCI preview generated: {len(images)} images found")
            return (preview_tensor, summary_text)

        except Exception as e:
            print(f"Error previewing DCI file: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_error_output(f"Error: {str(e)}")

    def _pil_to_tensor(self, pil_image):
        """Convert PIL image to ComfyUI tensor"""
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Convert to numpy array
        img_array = np.array(pil_image).astype(np.float32) / 255.0

        # Convert to tensor with batch dimension
        tensor = torch.from_numpy(img_array).unsqueeze(0)

        return tensor

    def _create_error_output(self, error_message):
        """Create error output"""
        # Create error image
        error_image = Image.new('RGB', (400, 200), (200, 200, 200))
        from PIL import ImageDraw, ImageFont

        draw = ImageDraw.Draw(error_image)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except (OSError, IOError):
            # Font file not found, use default font
            font = ImageFont.load_default()

        # Draw error message
        bbox = draw.textbbox((0, 0), error_message, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (error_image.width - text_width) // 2
        y = (error_image.height - text_height) // 2

        draw.text((x, y), error_message, fill=(100, 100, 100), font=font)

        # Convert to tensor
        error_tensor = self._pil_to_tensor(error_image)

        return (error_tensor, error_message)

    def _format_summary(self, summary, source_name):
        """Format metadata summary as text"""
        if not summary:
            return "No metadata available"

        lines = [
            f"DCI Source: {source_name}",
            f"Total Images: {summary['total_images']}",
            f"Total File Size: {summary['total_file_size']} bytes",
            "",
            f"Icon Sizes: {', '.join(map(str, summary['sizes']))}",
            f"States: {', '.join(summary['states'])}",
            f"Tones: {', '.join(summary['tones'])}",
            f"Scale Factors: {', '.join(map(str, summary['scales']))}",
            f"Formats: {', '.join(summary['formats'])}",
        ]

        return "\n".join(lines)



class DCIMetadataExtractor:
    """ComfyUI node for extracting detailed metadata from DCI files"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "dci_file_path": ("STRING", {"default": "", "multiline": False}),
                "dci_binary_data": ("BINARY_DATA",),
                "filter_by_state": (["all", "normal", "disabled", "hover", "pressed"], {"default": "all"}),
                "filter_by_tone": (["all", "light", "dark"], {"default": "all"}),
                "filter_by_scale": ("STRING", {"default": "all", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("detailed_metadata", "directory_structure", "file_list")
    FUNCTION = "extract_metadata"
    CATEGORY = "DCI/Analysis"
    OUTPUT_NODE = True

    def extract_metadata(self, filter_by_state="all", filter_by_tone="all", filter_by_scale="all", dci_file_path="", dci_binary_data=None):
        """Extract detailed metadata from DCI file"""

        try:
            # Determine input source
            if dci_binary_data is not None:
                # Use binary data
                reader = DCIReader(binary_data=dci_binary_data)
            elif dci_file_path and os.path.exists(dci_file_path):
                # Use file path
                reader = DCIReader(dci_file_path)
            else:
                return ("No DCI file path or binary data provided", "", "")

            # Read DCI data
            if not reader.read():
                return ("Failed to read DCI data", "", "")

            # Extract images
            images = reader.get_icon_images()

            # Apply filters
            filtered_images = self._apply_filters(images, filter_by_state, filter_by_tone, filter_by_scale)

            # Generate detailed metadata
            detailed_metadata = self._generate_detailed_metadata(filtered_images)
            directory_structure = self._generate_directory_structure(reader.directory_structure)
            file_list = self._generate_file_list(filtered_images)

            return (detailed_metadata, directory_structure, file_list)

        except Exception as e:
            error_msg = f"Error extracting metadata: {str(e)}"
            print(error_msg)
            return (error_msg, "", "")

    def _apply_filters(self, images, state_filter, tone_filter, scale_filter):
        """Apply filters to image list"""
        filtered = images

        if state_filter != "all":
            filtered = [img for img in filtered if img['state'] == state_filter]

        if tone_filter != "all":
            filtered = [img for img in filtered if img['tone'] == tone_filter]

        if scale_filter != "all":
            try:
                scale_values = [int(s.strip()) for s in scale_filter.split(',') if s.strip().isdigit()]
                if scale_values:
                    filtered = [img for img in filtered if img['scale'] in scale_values]
            except (ValueError, AttributeError):
                # Invalid scale filter format, ignore filter
                pass

        return filtered

    def _generate_detailed_metadata(self, images):
        """Generate detailed metadata text"""
        if not images:
            return "No images match the filter criteria"

        lines = [f"Detailed Metadata ({len(images)} images):", "=" * 50]

        for i, img in enumerate(images, 1):
            lines.extend([
                f"\nImage {i}:",
                f"  Path: {img['path']}",
                f"  Filename: {img['filename']}",
                f"  Size: {img['size']}px",
                f"  State: {img['state']}",
                f"  Tone: {img['tone']}",
                f"  Scale: {img['scale']}x",
                f"  Format: {img['format']}",
                f"  Priority: {img['priority']}",
                f"  File Size: {img['file_size']} bytes",
                f"  Image Dimensions: {img['image'].size[0]}x{img['image'].size[1]}",
                f"  Image Mode: {img['image'].mode}"
            ])

        return "\n".join(lines)

    def _generate_directory_structure(self, directory_structure):
        """Generate directory structure text"""
        lines = ["Directory Structure:", "=" * 30]

        def add_directory(path, indent=0):
            prefix = "  " * indent
            lines.append(f"{prefix}{os.path.basename(path)}/")

            if path in directory_structure:
                for name, info in directory_structure[path].items():
                    if info['type'] == 1:  # File
                        lines.append(f"{prefix}  {name} ({info['size']} bytes)")

        for dir_path in sorted(directory_structure.keys()):
            add_directory(dir_path)

        return "\n".join(lines)

    def _generate_file_list(self, images):
        """Generate file list text"""
        if not images:
            return "No files match the filter criteria"

        lines = [f"File List ({len(images)} files):", "=" * 30]

        for img in images:
            lines.append(f"{img['path']}/{img['filename']} - {img['file_size']} bytes")

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
                "scale": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
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
            actual_size = icon_size * scale

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
            dci_path = f"{icon_size}/{icon_state}.{tone_type}/{scale}/1.0.0.0.0.0.0.0.0.0.{image_format}"

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
                "filename": ("STRING", {"default": "icon", "multiline": False}),
                "save_to_file": ("BOOLEAN", {"default": False}),
                "output_directory": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("DCI_BINARY_DATA", "STRING")
    RETURN_NAMES = ("dci_binary_data", "file_path")
    FUNCTION = "create_dci_file"
    CATEGORY = "DCI/Export"
    OUTPUT_NODE = True

    def create_dci_file(self, filename="icon", save_to_file=False, output_directory="", **kwargs):
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
                return (b"", "")

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

            # Optionally save to file
            file_path = ""
            if save_to_file:
                if output_directory and os.path.exists(output_directory):
                    file_path = os.path.join(output_directory, f"{filename}.dci")
                else:
                    try:
                        import folder_paths
                        output_dir = folder_paths.get_output_directory()
                    except ImportError:
                        # ComfyUI folder_paths not available
                        output_dir = tempfile.gettempdir()
                    except Exception:
                        # Any other folder_paths related errors
                        output_dir = tempfile.gettempdir()
                    file_path = os.path.join(output_dir, f"{filename}.dci")

                with open(file_path, 'wb') as f:
                    f.write(binary_data)
                print(f"DCI file saved: {file_path}")

            print(f"Created DCI file with {len(dci_images)} images ({len(binary_data)} bytes)")
            return (binary_data, file_path)

        except Exception as e:
            print(f"Error creating DCI file: {str(e)}")
            import traceback
            traceback.print_exc()
            return (b"", "")

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


class DCIPreviewFromBinary:
    """ComfyUI node for previewing DCI file contents from binary data"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dci_binary_data": ("DCI_BINARY_DATA",),
            },
            "optional": {
                "grid_columns": ("INT", {"default": 4, "min": 1, "max": 10, "step": 1}),
                "show_metadata": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("preview_image", "metadata_summary")
    FUNCTION = "preview_dci_binary"
    CATEGORY = "DCI/Preview"
    OUTPUT_NODE = True

    def preview_dci_binary(self, dci_binary_data, grid_columns=4, show_metadata=True):
        """Preview DCI file contents from binary data"""

        try:
            if not dci_binary_data:
                return self._create_error_output("No DCI binary data provided")

            # Read DCI from binary data
            reader = DCIReader(binary_data=dci_binary_data)
            if not reader.read():
                return self._create_error_output("Failed to read DCI binary data")

            # Extract images
            images = reader.get_icon_images()
            if not images:
                return self._create_error_output("No images found in DCI data")

            # Create preview
            preview_generator = DCIPreviewGenerator()
            preview_image = preview_generator.create_preview_grid(
                images,
                grid_cols=grid_columns
            )

            # Convert PIL to tensor
            preview_tensor = self._pil_to_tensor(preview_image)

            # Create metadata summary
            summary = preview_generator.create_metadata_summary(images)
            summary_text = self._format_summary(summary, "binary_data")

            return (preview_tensor, summary_text)

        except Exception as e:
            error_msg = f"Error previewing DCI binary data: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return self._create_error_output(error_msg)

    def _pil_to_tensor(self, pil_image):
        """Convert PIL Image to ComfyUI tensor format"""
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Convert to numpy array
        img_array = np.array(pil_image)

        # Convert to 0-1 range and add batch dimension
        img_tensor = torch.from_numpy(img_array.astype(np.float32) / 255.0).unsqueeze(0)

        return img_tensor

    def _create_error_output(self, error_message):
        """Create error output with placeholder image"""
        # Create a simple error image
        error_img = Image.new('RGB', (400, 200), color='red')
        error_tensor = self._pil_to_tensor(error_img)
        return (error_tensor, error_message)

    def _format_summary(self, summary, source):
        """Format metadata summary as text"""
        if not summary:
            return "No metadata available"

        lines = [
            f"DCI Source: {source}",
            f"Total Images: {summary['total_images']}",
            f"Total File Size: {summary['total_file_size']} bytes",
            "",
            f"Icon Sizes: {', '.join(map(str, summary['sizes']))}",
            f"States: {', '.join(summary['states'])}",
            f"Tones: {', '.join(summary['tones'])}",
            f"Scale Factors: {', '.join(map(str, summary['scales']))}",
            f"Formats: {', '.join(summary['formats'])}",
        ]

        return "\n".join(lines)


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
                "file_path": ("STRING", {"default": "", "multiline": False}),
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

    def save_binary_file(self, binary_data, file_path, output_directory=""):
        """Save binary data to file system"""

        try:
            if not binary_data:
                print("No binary data provided")
                return ("",)

            # Determine output path
            if output_directory and os.path.exists(output_directory):
                if not file_path:
                    # Use default filename
                    filename = 'binary_file'
                    full_path = os.path.join(output_directory, filename)
                else:
                    full_path = os.path.join(output_directory, os.path.basename(file_path))
            else:
                if not file_path:
                    # Use ComfyUI output directory or temp directory
                    try:
                        import folder_paths
                        output_dir = folder_paths.get_output_directory()
                    except ImportError:
                        # ComfyUI folder_paths not available
                        output_dir = tempfile.gettempdir()
                    except Exception:
                        # Any other folder_paths related errors
                        output_dir = tempfile.gettempdir()

                    filename = 'binary_file'
                    full_path = os.path.join(output_dir, filename)
                else:
                    full_path = file_path

            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Write binary data directly
            with open(full_path, 'wb') as f:
                f.write(binary_data)

            file_size = len(binary_data)
            print(f"Saved binary file: {full_path} ({file_size} bytes)")
            return (full_path,)

        except Exception as e:
            print(f"Error saving binary file: {str(e)}")
            import traceback
            traceback.print_exc()
            return ("",)
