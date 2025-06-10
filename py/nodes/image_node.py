from PIL import Image
from io import BytesIO
from ..utils.image_utils import tensor_to_pil, apply_background
from ..utils.ui_utils import format_dci_path
from .base_node import BaseNode

class DCIImage(BaseNode):
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
            },
            "optional": {
                "background_color": (["transparent", "white", "black", "custom"], {"default": "transparent"}),
                "custom_bg_r": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),
                "custom_bg_g": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),
                "custom_bg_b": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),
            }
        }

    RETURN_TYPES = ("DCI_IMAGE_DATA",)
    RETURN_NAMES = ("dci_image_data",)
    FUNCTION = "create_dci_image"
    CATEGORY = "DCI/Export"

    def _execute(self, image, icon_size, icon_state, tone_type, scale, image_format,
                background_color="transparent", custom_bg_r=255, custom_bg_g=255, custom_bg_b=255):
        """Create DCI image metadata and data"""
        # Convert ComfyUI image tensor to PIL Image
        pil_image = tensor_to_pil(image)

        # Handle background color for images with transparency
        if background_color != "transparent" and pil_image.mode in ('RGBA', 'LA'):
            bg_color = (custom_bg_r, custom_bg_g, custom_bg_b) if background_color == "custom" else None
            pil_image = apply_background(pil_image, background_color, bg_color)

        # Calculate actual size with scale
        actual_size = int(icon_size * scale)

        # Resize image to target size
        resized_image = pil_image.resize((actual_size, actual_size), Image.Resampling.LANCZOS)

        # Convert to bytes
        img_bytes = BytesIO()
        if image_format == 'webp':
            # For WebP, preserve transparency if available
            if resized_image.mode == 'RGBA' and background_color == "transparent":
                resized_image.save(img_bytes, format='WEBP', quality=90, lossless=True)
            else:
                # Convert to RGB for lossy WebP
                if resized_image.mode == 'RGBA':
                    rgb_image = Image.new('RGB', resized_image.size, (255, 255, 255))
                    rgb_image.paste(resized_image, mask=resized_image.split()[-1] if resized_image.mode == 'RGBA' else None)
                    resized_image = rgb_image
                resized_image.save(img_bytes, format='WEBP', quality=90)
        elif image_format == 'png':
            # PNG supports transparency
            resized_image.save(img_bytes, format='PNG')
        elif image_format == 'jpg':
            # Convert to RGB if necessary for JPEG (JPEG doesn't support transparency)
            if resized_image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', resized_image.size, (255, 255, 255))
                if resized_image.mode == 'P':
                    resized_image = resized_image.convert('RGBA')
                rgb_image.paste(resized_image, mask=resized_image.split()[-1] if resized_image.mode in ('RGBA', 'LA') else None)
                resized_image = rgb_image
            resized_image.save(img_bytes, format='JPEG', quality=90)

        img_content = img_bytes.getvalue()

        # Create DCI path
        dci_path = format_dci_path(icon_size, icon_state, tone_type, scale, image_format)

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
            'file_size': len(img_content),
            'background_color': background_color,
            'pil_image': resized_image  # Store PIL image for debug purposes
        }

        print(f"Created DCI image: {dci_path} ({len(img_content)} bytes), background: {background_color}")
        return (dci_image_data,)
