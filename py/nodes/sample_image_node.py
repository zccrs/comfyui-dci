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
from ..utils.enums import (
    ImageFormat, IconState, ToneType, BackgroundColor, PaletteType,
    translate_ui_to_enum, get_enum_ui_options, get_enum_default_ui_value
)

class DCISampleImage(BaseNode):
    """ComfyUI node for creating simple DCI image data with basic settings only"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("image"): ("IMAGE",),
                t("icon_size"): ("INT", {"default": 256, "min": 16, "max": 1024, "step": 1}),
                t("icon_state"): (get_enum_ui_options(IconState, t), {"default": get_enum_default_ui_value(IconState.NORMAL, t)}),
                t("scale"): ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                t("tone_type"): (get_enum_ui_options(ToneType, t), {"default": get_enum_default_ui_value(ToneType.LIGHT, t)}),
                t("image_format"): ([fmt.value for fmt in ImageFormat], {"default": ImageFormat.WEBP.value}),
                t("image_quality"): ("INT", {"default": 90, "min": 1, "max": 100, "step": 1}),

                # WebP advanced settings
                t("webp_lossless"): ("BOOLEAN", {"default": False}),
                t("webp_near_lossless"): ("INT", {"default": 100, "min": 60, "max": 100, "step": 1}),
                t("webp_alpha_quality"): ("INT", {"default": 100, "min": 0, "max": 100, "step": 1}),

                # PNG advanced settings
                t("png_compress_level"): ("INT", {"default": 6, "min": 0, "max": 9, "step": 1}),
            }
        }

    RETURN_TYPES = ("DCI_IMAGE_DATA",)
    RETURN_NAMES = (t("dci_image_data"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Export')}"

    def _execute(self, **kwargs):
        """Create simple DCI image data with basic settings only"""
        # Extract parameters with translation support and convert to enums
        # Try both translated and original parameter names for compatibility
        image = kwargs.get(t("image")) if t("image") in kwargs else kwargs.get("image")
        icon_size = kwargs.get(t("icon_size")) if t("icon_size") in kwargs else kwargs.get("icon_size")

        # Convert UI values to enums for type safety
        icon_state_ui = kwargs.get(t("icon_state")) if t("icon_state") in kwargs else kwargs.get("icon_state")
        icon_state = translate_ui_to_enum(icon_state_ui, IconState, t) if icon_state_ui else IconState.NORMAL

        scale = kwargs.get(t("scale")) if t("scale") in kwargs else kwargs.get("scale")

        tone_type_ui = kwargs.get(t("tone_type")) if t("tone_type") in kwargs else kwargs.get("tone_type")
        tone_type = translate_ui_to_enum(tone_type_ui, ToneType, t) if tone_type_ui else ToneType.LIGHT

        image_format_ui = kwargs.get(t("image_format")) if t("image_format") in kwargs else kwargs.get("image_format", ImageFormat.WEBP.value)
        image_format = ImageFormat(image_format_ui) if image_format_ui else ImageFormat.WEBP

        image_quality = kwargs.get(t("image_quality")) if t("image_quality") in kwargs else kwargs.get("image_quality", 90)

        # WebP advanced settings
        webp_lossless = kwargs.get(t("webp_lossless")) if t("webp_lossless") in kwargs else kwargs.get("webp_lossless", False)
        webp_near_lossless = kwargs.get(t("webp_near_lossless")) if t("webp_near_lossless") in kwargs else kwargs.get("webp_near_lossless", 100)
        webp_alpha_quality = kwargs.get(t("webp_alpha_quality")) if t("webp_alpha_quality") in kwargs else kwargs.get("webp_alpha_quality", 100)

        # PNG advanced settings
        png_compress_level = kwargs.get(t("png_compress_level")) if t("png_compress_level") in kwargs else kwargs.get("png_compress_level", 6)

        return self._execute_impl(image, icon_size, icon_state, scale, tone_type, image_format, image_quality,
                                 webp_lossless, webp_near_lossless, webp_alpha_quality, png_compress_level)

    def _execute_impl(self, image, icon_size, icon_state: IconState, scale, tone_type: ToneType = ToneType.LIGHT, image_format: ImageFormat = ImageFormat.WEBP, image_quality: int = 90,
                     webp_lossless: bool = False, webp_near_lossless: int = 100, webp_alpha_quality: int = 100, png_compress_level: int = 6):
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
        if image_format == ImageFormat.WEBP:
            # WebP advanced settings
            if webp_lossless:
                # Lossless WebP
                resized_image.save(img_bytes, format='WEBP', lossless=True)
            elif webp_near_lossless < 100:
                # Near-lossless WebP
                resized_image.save(img_bytes, format='WEBP', quality=image_quality, method=6, near_lossless=webp_near_lossless)
            else:
                # Standard lossy WebP with alpha quality control
                if resized_image.mode == 'RGBA':
                    resized_image.save(img_bytes, format='WEBP', quality=image_quality, alpha_quality=webp_alpha_quality)
                else:
                    resized_image.save(img_bytes, format='WEBP', quality=image_quality)
        elif image_format == ImageFormat.PNG:
            # PNG with compression level control
            resized_image.save(img_bytes, format='PNG', compress_level=png_compress_level)
        elif image_format == ImageFormat.JPG:
            # Convert to RGB if necessary for JPEG (JPEG doesn't support transparency)
            if resized_image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', resized_image.size, (255, 255, 255))
                if resized_image.mode == 'P':
                    resized_image = resized_image.convert('RGBA')
                rgb_image.paste(resized_image, mask=resized_image.split()[-1] if resized_image.mode in ('RGBA', 'LA') else None)
                resized_image = rgb_image
            resized_image.save(img_bytes, format='JPEG', quality=image_quality)

        img_content = img_bytes.getvalue()

        # Create simple DCI path with default layer parameters using enum string values
        dci_path = format_dci_path(
            icon_size, str(icon_state), str(tone_type), scale, str(image_format),
            priority=1, padding=0, palette=-1,  # Use defaults
            hue=0, saturation=0, brightness=0,
            red=0, green=0, blue=0, alpha=0
        )

        # Create metadata dictionary with basic information
        # Store enum values for internal use, but also store UI-friendly translated strings
        dci_image_data = {
            'path': dci_path,
            'content': img_content,
            'size': icon_size,
            'state': icon_state,  # Store enum for internal use
            'state_ui': t(str(icon_state)),  # Store translated string for UI display
            'tone': tone_type,  # Store enum for internal use
            'tone_ui': t(str(tone_type)),  # Store translated string for UI display
            'scale': scale,
            'format': image_format,  # Store enum for internal use
            'format_ui': str(image_format),  # Store string for UI display
            'actual_size': actual_size,
            'file_size': len(img_content),
            'background_color': BackgroundColor.TRANSPARENT,  # Store enum for internal use
            'background_color_ui': t(str(BackgroundColor.TRANSPARENT)),  # Store translated string for UI display
            'pil_image': resized_image,  # Store PIL image for debug purposes

            # Default layer metadata
            'layer_priority': 1,
            'layer_padding': 0,
            'palette_type': PaletteType.NONE,  # Store enum for internal use
            'palette_type_ui': t(str(PaletteType.NONE)),  # Store translated string for UI display
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
