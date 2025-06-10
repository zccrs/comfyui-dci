try:
    from PIL import Image
    from ..utils.image_utils import tensor_to_pil, apply_background
    _image_support = True
except ImportError as e:
    print(f"Warning: Image support not available in image_node: {e}")
    _image_support = False

from io import BytesIO
from ..utils.ui_utils import format_dci_path
from ..utils.i18n import t
from .base_node import BaseNode

class DCIImage(BaseNode):
    """ComfyUI node for creating DCI image metadata and data with layer support"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("image"): ("IMAGE",),
                t("icon_size"): ("INT", {"default": 256, "min": 16, "max": 1024, "step": 1}),
                t("icon_state"): ([t("normal"), t("disabled"), t("hover"), t("pressed")], {"default": t("normal")}),
                t("scale"): ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                t("tone_type"): ([t("light"), t("dark")], {"default": t("light")}),
            },
            "optional": {
                # Basic format setting
                t("image_format"): ([t("webp"), t("png"), t("jpg")], {"default": t("webp")}),

                # Background color settings
                t("background_color"): ([t("transparent"), t("white"), t("black"), t("custom")], {"default": t("transparent")}),
                t("custom_bg_r"): ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),
                t("custom_bg_g"): ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),
                t("custom_bg_b"): ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),

                # Layer properties
                t("layer_priority"): ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),
                t("layer_padding"): ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                t("palette_type"): ([t("none"), t("foreground"), t("background"), t("highlight_foreground"), t("highlight")], {"default": t("none")}),

                # Color adjustments
                t("hue_adjustment"): ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                t("saturation_adjustment"): ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                t("brightness_adjustment"): ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                t("red_adjustment"): ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                t("green_adjustment"): ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                t("blue_adjustment"): ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                t("alpha_adjustment"): ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
            }
        }

    RETURN_TYPES = ("DCI_IMAGE_DATA",)
    RETURN_NAMES = (t("dci_image_data"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Export')}"

    def _execute(self, **kwargs):
        """Create DCI image metadata and data with layer support"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        image = kwargs.get(t("image")) if t("image") in kwargs else kwargs.get("image")
        icon_size = kwargs.get(t("icon_size")) if t("icon_size") in kwargs else kwargs.get("icon_size")
        icon_state = kwargs.get(t("icon_state")) if t("icon_state") in kwargs else kwargs.get("icon_state")
        scale = kwargs.get(t("scale")) if t("scale") in kwargs else kwargs.get("scale")
        tone_type = kwargs.get(t("tone_type")) if t("tone_type") in kwargs else kwargs.get("tone_type", "light")
        image_format = kwargs.get(t("image_format")) if t("image_format") in kwargs else kwargs.get("image_format", "webp")
        background_color = kwargs.get(t("background_color")) if t("background_color") in kwargs else kwargs.get("background_color", "transparent")
        custom_bg_r = kwargs.get(t("custom_bg_r")) if t("custom_bg_r") in kwargs else kwargs.get("custom_bg_r", 255)
        custom_bg_g = kwargs.get(t("custom_bg_g")) if t("custom_bg_g") in kwargs else kwargs.get("custom_bg_g", 255)
        custom_bg_b = kwargs.get(t("custom_bg_b")) if t("custom_bg_b") in kwargs else kwargs.get("custom_bg_b", 255)
        layer_priority = kwargs.get(t("layer_priority")) if t("layer_priority") in kwargs else kwargs.get("layer_priority", 1)
        layer_padding = kwargs.get(t("layer_padding")) if t("layer_padding") in kwargs else kwargs.get("layer_padding", 0)
        palette_type = kwargs.get(t("palette_type")) if t("palette_type") in kwargs else kwargs.get("palette_type", "none")
        hue_adjustment = kwargs.get(t("hue_adjustment")) if t("hue_adjustment") in kwargs else kwargs.get("hue_adjustment", 0)
        saturation_adjustment = kwargs.get(t("saturation_adjustment")) if t("saturation_adjustment") in kwargs else kwargs.get("saturation_adjustment", 0)
        brightness_adjustment = kwargs.get(t("brightness_adjustment")) if t("brightness_adjustment") in kwargs else kwargs.get("brightness_adjustment", 0)
        red_adjustment = kwargs.get(t("red_adjustment")) if t("red_adjustment") in kwargs else kwargs.get("red_adjustment", 0)
        green_adjustment = kwargs.get(t("green_adjustment")) if t("green_adjustment") in kwargs else kwargs.get("green_adjustment", 0)
        blue_adjustment = kwargs.get(t("blue_adjustment")) if t("blue_adjustment") in kwargs else kwargs.get("blue_adjustment", 0)
        alpha_adjustment = kwargs.get(t("alpha_adjustment")) if t("alpha_adjustment") in kwargs else kwargs.get("alpha_adjustment", 0)

        return self._execute_impl(image, icon_size, icon_state, scale, tone_type,
                                 image_format, background_color, custom_bg_r, custom_bg_g, custom_bg_b,
                                 layer_priority, layer_padding, palette_type,
                                 hue_adjustment, saturation_adjustment, brightness_adjustment,
                                 red_adjustment, green_adjustment, blue_adjustment, alpha_adjustment)

    def _execute_impl(self, image, icon_size, icon_state, scale, tone_type="light",
                     image_format="webp",
                     background_color="transparent", custom_bg_r=255, custom_bg_g=255, custom_bg_b=255,
                     layer_priority=1, layer_padding=0, palette_type="none",
                     hue_adjustment=0, saturation_adjustment=0, brightness_adjustment=0,
                     red_adjustment=0, green_adjustment=0, blue_adjustment=0, alpha_adjustment=0):
        """Create DCI image metadata and data with layer support"""
        if not _image_support:
            return ({},)

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

        # Convert palette type to numeric value according to DCI specification
        palette_map = {
            "none": -1,
            "foreground": 0,
            "background": 1,
            "highlight_foreground": 2,
            "highlight": 3
        }
        palette_value = palette_map.get(palette_type, -1)

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

        # Create DCI path with layer parameters
        dci_path = format_dci_path(
            icon_size, icon_state, tone_type, scale, image_format,
            priority=layer_priority, padding=layer_padding, palette=palette_value,
            hue=hue_adjustment, saturation=saturation_adjustment, brightness=brightness_adjustment,
            red=red_adjustment, green=green_adjustment, blue=blue_adjustment, alpha=alpha_adjustment
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
            'background_color': background_color,
            'pil_image': resized_image,  # Store PIL image for debug purposes

            # Layer metadata
            'layer_priority': layer_priority,
            'layer_padding': layer_padding,
            'palette_type': palette_type,
            'palette_value': palette_value,
            'hue_adjustment': hue_adjustment,
            'saturation_adjustment': saturation_adjustment,
            'brightness_adjustment': brightness_adjustment,
            'red_adjustment': red_adjustment,
            'green_adjustment': green_adjustment,
            'blue_adjustment': blue_adjustment,
            'alpha_adjustment': alpha_adjustment,
        }

        print(f"{t('Created DCI image with layers')}: {dci_path} ({len(img_content)} {t('bytes')})")
        print(f"  {t('Layer priority')}: {layer_priority}, {t('padding')}: {layer_padding}, {t('palette')}: {palette_type}")
        print(f"  {t('Color adjustments')} - H:{hue_adjustment} S:{saturation_adjustment} B:{brightness_adjustment}")
        print(f"  {t('RGBA adjustments')} - R:{red_adjustment} G:{green_adjustment} B:{blue_adjustment} A:{alpha_adjustment}")

        return (dci_image_data,)
