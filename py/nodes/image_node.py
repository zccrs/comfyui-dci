try:
    from PIL import Image
    from ..utils.image_utils import tensor_to_pil, apply_background
    _image_support = True
except ImportError as e:
    print(f"Warning: Image support not available in image_node: {e}")
    _image_support = False

from io import BytesIO
from ..utils.ui_utils import format_dci_path
from .base_node import BaseNode

class DCIImage(BaseNode):
    """ComfyUI node for creating DCI image metadata and data with layer support"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "icon_size": ("INT", {"default": 256, "min": 16, "max": 1024, "step": 1}),
                "icon_state": (["normal", "disabled", "hover", "pressed"], {"default": "normal"}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "tone_type": (["light", "dark"], {"default": "light"}),
            },
            "optional": {
                # Basic format setting
                "image_format": (["webp", "png", "jpg"], {"default": "webp"}),

                # Advanced settings - Background color
                "adv_background_color": (["transparent", "white", "black", "custom"], {"default": "transparent"}),
                "adv_custom_bg_r": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),
                "adv_custom_bg_g": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),
                "adv_custom_bg_b": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),

                # Advanced settings - Layer properties
                "adv_layer_priority": ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),
                "adv_layer_padding": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                "adv_palette_type": (["none", "foreground", "background", "highlight_foreground", "highlight"], {"default": "none"}),

                # Advanced settings - Color adjustments
                "adv_hue_adjustment": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                "adv_saturation_adjustment": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                "adv_brightness_adjustment": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                "adv_red_adjustment": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                "adv_green_adjustment": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                "adv_blue_adjustment": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                "adv_alpha_adjustment": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
            }
        }

    RETURN_TYPES = ("DCI_IMAGE_DATA",)
    RETURN_NAMES = ("dci_image_data",)
    FUNCTION = "execute"
    CATEGORY = "DCI/Export"

    def _execute(self, image, icon_size, icon_state, scale, tone_type="light",
                 image_format="webp",
                 adv_background_color="transparent", adv_custom_bg_r=255, adv_custom_bg_g=255, adv_custom_bg_b=255,
                 adv_layer_priority=1, adv_layer_padding=0, adv_palette_type="none",
                 adv_hue_adjustment=0, adv_saturation_adjustment=0, adv_brightness_adjustment=0,
                 adv_red_adjustment=0, adv_green_adjustment=0, adv_blue_adjustment=0, adv_alpha_adjustment=0):
        """Create DCI image metadata and data with layer support"""
        if not _image_support:
            return ({},)

        # Convert ComfyUI image tensor to PIL Image
        pil_image = tensor_to_pil(image)

        # Handle background color for images with transparency
        if adv_background_color != "transparent" and pil_image.mode in ('RGBA', 'LA'):
            bg_color = (adv_custom_bg_r, adv_custom_bg_g, adv_custom_bg_b) if adv_background_color == "custom" else None
            pil_image = apply_background(pil_image, adv_background_color, bg_color)

        # Calculate actual size with scale
        actual_size = int(icon_size * scale)

        # Resize image to target size
        resized_image = pil_image.resize((actual_size, actual_size), Image.Resampling.LANCZOS)

        # Convert palette type to numeric value according to DCI specification
        palette_map = {
            "none": -1,
            "foreground": 0,
            "background": 1,
            "highlight_foreground": 2,
            "highlight": 3
        }
        palette_value = palette_map.get(adv_palette_type, -1)

        # Convert to bytes
        img_bytes = BytesIO()
        if image_format == 'webp':
            # For WebP, preserve transparency if available
            if resized_image.mode == 'RGBA' and adv_background_color == "transparent":
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

        # Create DCI path with layer parameters
        dci_path = format_dci_path(
            icon_size, icon_state, tone_type, scale, image_format,
            priority=adv_layer_priority, padding=adv_layer_padding, palette=palette_value,
            hue=adv_hue_adjustment, saturation=adv_saturation_adjustment, brightness=adv_brightness_adjustment,
            red=adv_red_adjustment, green=adv_green_adjustment, blue=adv_blue_adjustment, alpha=adv_alpha_adjustment
        )

        # Create metadata dictionary with layer information
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
            'background_color': adv_background_color,
            'pil_image': resized_image,  # Store PIL image for debug purposes

            # Layer metadata
            'layer_priority': adv_layer_priority,
            'layer_padding': adv_layer_padding,
            'palette_type': adv_palette_type,
            'palette_value': palette_value,
            'hue_adjustment': adv_hue_adjustment,
            'saturation_adjustment': adv_saturation_adjustment,
            'brightness_adjustment': adv_brightness_adjustment,
            'red_adjustment': adv_red_adjustment,
            'green_adjustment': adv_green_adjustment,
            'blue_adjustment': adv_blue_adjustment,
            'alpha_adjustment': adv_alpha_adjustment,
        }

        print(f"Created DCI image with layers: {dci_path} ({len(img_content)} bytes)")
        print(f"  Layer priority: {adv_layer_priority}, padding: {adv_layer_padding}, palette: {adv_palette_type}")
        print(f"  Color adjustments - H:{adv_hue_adjustment} S:{adv_saturation_adjustment} B:{adv_brightness_adjustment}")
        print(f"  RGBA adjustments - R:{adv_red_adjustment} G:{adv_green_adjustment} B:{adv_blue_adjustment} A:{adv_alpha_adjustment}")

        return (dci_image_data,)
