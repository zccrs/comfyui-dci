import torch
import numpy as np
from PIL import Image
import os
import tempfile
from .dci_format import create_dci_icon, DCIIconBuilder
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
    CATEGORY = "image/export"
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
                except:
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
    CATEGORY = "image/export"
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
                except:
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
            "required": {
                "dci_file_path": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "grid_columns": ("INT", {"default": 4, "min": 1, "max": 10, "step": 1}),
                "show_metadata": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("preview_image", "metadata_summary")
    FUNCTION = "preview_dci"
    CATEGORY = "image/preview"
    OUTPUT_NODE = True

    def preview_dci(self, dci_file_path, grid_columns=4, show_metadata=True):
        """Preview DCI file contents"""

        try:
            if not dci_file_path or not os.path.exists(dci_file_path):
                return self._create_error_output("DCI file not found or path is empty")

            # Read DCI file
            reader = DCIReader(dci_file_path)
            if not reader.read():
                return self._create_error_output("Failed to read DCI file")

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
            summary_text = self._format_summary(summary, dci_file_path)

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
        except:
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

    def _format_summary(self, summary, file_path):
        """Format metadata summary as text"""
        if not summary:
            return "No metadata available"

        lines = [
            f"DCI File: {os.path.basename(file_path)}",
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


class DCIFileLoader:
    """ComfyUI node for loading DCI files from file system"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "file_path": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("dci_file_path",)
    FUNCTION = "load_dci_file"
    CATEGORY = "loaders"

    def load_dci_file(self, file_path=""):
        """Load DCI file path"""

        if not file_path:
            # Try to find DCI files in common directories
            search_dirs = []

            try:
                import folder_paths
                search_dirs.append(folder_paths.get_output_directory())
            except:
                pass

            search_dirs.extend([
                tempfile.gettempdir(),
                os.getcwd(),
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Desktop")
            ])

            for search_dir in search_dirs:
                if os.path.exists(search_dir):
                    dci_files = [f for f in os.listdir(search_dir) if f.endswith('.dci')]
                    if dci_files:
                        file_path = os.path.join(search_dir, dci_files[0])
                        print(f"Auto-found DCI file: {file_path}")
                        break

        if file_path and os.path.exists(file_path):
            return (file_path,)
        else:
            print(f"DCI file not found: {file_path}")
            return ("",)


class DCIMetadataExtractor:
    """ComfyUI node for extracting detailed metadata from DCI files"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dci_file_path": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "filter_by_state": (["all", "normal", "disabled", "hover", "pressed"], {"default": "all"}),
                "filter_by_tone": (["all", "light", "dark"], {"default": "all"}),
                "filter_by_scale": ("STRING", {"default": "all", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("detailed_metadata", "directory_structure", "file_list")
    FUNCTION = "extract_metadata"
    CATEGORY = "analysis"
    OUTPUT_NODE = True

    def extract_metadata(self, dci_file_path, filter_by_state="all", filter_by_tone="all", filter_by_scale="all"):
        """Extract detailed metadata from DCI file"""

        try:
            if not dci_file_path or not os.path.exists(dci_file_path):
                return ("DCI file not found", "", "")

            # Read DCI file
            reader = DCIReader(dci_file_path)
            if not reader.read():
                return ("Failed to read DCI file", "", "")

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
            except:
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
