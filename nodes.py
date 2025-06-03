import torch
import numpy as np
from PIL import Image
import os
import tempfile
from .dci_format import create_dci_icon, DCIIconBuilder


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
