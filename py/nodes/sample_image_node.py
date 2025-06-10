try:
    from PIL import Image
    from ..utils.image_utils import tensor_to_pil, apply_background
    _image_support = True
except ImportError as e:
    print(f"Warning: Image support not available in sample_image_node: {e}")
    _image_support = False

from io import BytesIO
from ..utils.ui_utils import format_dci_path
from .base_node import BaseNode
from ..utils.i18n import t

class DCISampleImage(BaseNode):
    """ComfyUI node for creating simple DCI image data with basic settings only"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("image"): ("IMAGE",),
                t("icon_size"): ("INT", {"default": 256, "min": 16, "max": 1024, "step": 1}),
                t("icon_state"): ([t("normal"), t("disabled"), t("hover"), t("pressed")], {"default": t("normal")}),
                t("scale"): ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                t("tone_type"): ([t("light"), t("dark")], {"default": t("light")}),
                t("image_format"): ([t("webp"), t("png"), t("jpg")], {"default": t("webp")}),
            }
        }

    RETURN_TYPES = ("DCI_IMAGE_DATA",)
    RETURN_NAMES = (t("dci_image_data"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Export')}"

    def _execute(self, **kwargs):
        """Create simple DCI image data with basic settings only"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        image = kwargs.get(t("image")) if t("image") in kwargs else kwargs.get("image")
        icon_size = kwargs.get(t("icon_size")) if t("icon_size") in kwargs else kwargs.get("icon_size")
        icon_state = kwargs.get(t("icon_state")) if t("icon_state") in kwargs else kwargs.get("icon_state")
        scale = kwargs.get(t("scale")) if t("scale") in kwargs else kwargs.get("scale")
        tone_type = kwargs.get(t("tone_type")) if t("tone_type") in kwargs else kwargs.get("tone_type", "light")
        image_format = kwargs.get(t("image_format")) if t("image_format") in kwargs else kwargs.get("image_format", "webp")

        return self._execute_impl(image, icon_size, icon_state, scale, tone_type, image_format)

    def _execute_impl(self, image, icon_size, icon_state, scale, tone_type="light", image_format="webp"):
        """Create simple DCI image data with basic settings only"""
        if not _image_support:
            return ({},)

        # Convert ComfyUI image tensor to PIL Image
        pil_image = tensor_to_pil(image)

        # Calculate actual size with scale
        actual_size = int(icon_size * scale)

        # Resize image to target size
        resized_image = pil_image.resize((actual_size, actual_size), Image.Resampling.LANCZOS)

        # Convert to bytes
        img_bytes = BytesIO()
        if image_format == 'webp':
            # For WebP, preserve transparency if available
            if resized_image.mode == 'RGBA':
                resized_image.save(img_bytes, format='WEBP', quality=90, lossless=True)
            else:
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

        # Create simple DCI path with default layer parameters
        dci_path = format_dci_path(
            icon_size, icon_state, tone_type, scale, image_format,
            priority=1, padding=0, palette=-1,  # Use defaults
            hue=0, saturation=0, brightness=0,
            red=0, green=0, blue=0, alpha=0
        )

        # Create metadata dictionary with basic information
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
            'background_color': "transparent",
            'pil_image': resized_image,  # Store PIL image for debug purposes

            # Default layer metadata
            'layer_priority': 1,
            'layer_padding': 0,
            'palette_type': "none",
            'palette_value': -1,
            'hue_adjustment': 0,
            'saturation_adjustment': 0,
            'brightness_adjustment': 0,
            'red_adjustment': 0,
            'green_adjustment': 0,
            'blue_adjustment': 0,
            'alpha_adjustment': 0,
        }

        print(f"Created simple DCI image: {dci_path} ({len(img_content)} bytes)")

        return (dci_image_data,)
