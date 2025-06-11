try:
    from PIL import Image, ImageFilter, ImageDraw
    import numpy as np
    import torch
    from ..utils.image_utils import tensor_to_pil, pil_to_tensor
    _image_support = True
except ImportError as e:
    print(f"Warning: Image support not available in drop_shadow_node: {e}")
    _image_support = False

from ..utils.i18n import t
from .base_node import BaseNode

class DropShadowNode(BaseNode):
    """ComfyUI node for applying drop shadow effect to images, similar to CSS drop-shadow"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("image"): ("IMAGE",),
            },
            "optional": {
                # Drop shadow parameters (similar to CSS drop-shadow)
                t("offset_x"): ("INT", {"default": 4, "min": -100, "max": 100, "step": 1}),
                t("offset_y"): ("INT", {"default": 4, "min": -100, "max": 100, "step": 1}),
                t("blur_radius"): ("INT", {"default": 8, "min": 0, "max": 100, "step": 1}),
                t("spread_radius"): ("INT", {"default": 0, "min": -50, "max": 50, "step": 1}),

                # Shadow color (RGBA)
                t("shadow_color_r"): ("INT", {"default": 0, "min": 0, "max": 255, "step": 1}),
                t("shadow_color_g"): ("INT", {"default": 0, "min": 0, "max": 255, "step": 1}),
                t("shadow_color_b"): ("INT", {"default": 0, "min": 0, "max": 255, "step": 1}),
                t("shadow_opacity"): ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),

                # Canvas expansion options
                t("auto_expand_canvas"): ("BOOLEAN", {"default": True}),
                t("canvas_padding"): ("INT", {"default": 20, "min": 0, "max": 200, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = (t("image"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Effects')}"

    def _execute(self, **kwargs):
        """Apply drop shadow effect to image"""
        if not _image_support:
            print("错误：图像支持不可用，缺少PIL/torch依赖库")
            return (None,)

        # Extract parameters with translation support
        image = kwargs.get(t("image")) if t("image") in kwargs else kwargs.get("image")
        if image is None:
            print("错误：未提供输入图像")
            return (None,)

        offset_x = kwargs.get(t("offset_x")) if t("offset_x") in kwargs else kwargs.get("offset_x", 4)
        offset_y = kwargs.get(t("offset_y")) if t("offset_y") in kwargs else kwargs.get("offset_y", 4)
        blur_radius = kwargs.get(t("blur_radius")) if t("blur_radius") in kwargs else kwargs.get("blur_radius", 8)
        spread_radius = kwargs.get(t("spread_radius")) if t("spread_radius") in kwargs else kwargs.get("spread_radius", 0)

        shadow_color_r = kwargs.get(t("shadow_color_r")) if t("shadow_color_r") in kwargs else kwargs.get("shadow_color_r", 0)
        shadow_color_g = kwargs.get(t("shadow_color_g")) if t("shadow_color_g") in kwargs else kwargs.get("shadow_color_g", 0)
        shadow_color_b = kwargs.get(t("shadow_color_b")) if t("shadow_color_b") in kwargs else kwargs.get("shadow_color_b", 0)
        shadow_opacity = kwargs.get(t("shadow_opacity")) if t("shadow_opacity") in kwargs else kwargs.get("shadow_opacity", 0.5)

        auto_expand_canvas = kwargs.get(t("auto_expand_canvas")) if t("auto_expand_canvas") in kwargs else kwargs.get("auto_expand_canvas", True)
        canvas_padding = kwargs.get(t("canvas_padding")) if t("canvas_padding") in kwargs else kwargs.get("canvas_padding", 20)

        return self._execute_impl(image, offset_x, offset_y, blur_radius, spread_radius,
                                 shadow_color_r, shadow_color_g, shadow_color_b, shadow_opacity,
                                 auto_expand_canvas, canvas_padding)

    def _execute_impl(self, image, offset_x=4, offset_y=4, blur_radius=8, spread_radius=0,
                     shadow_color_r=0, shadow_color_g=0, shadow_color_b=0, shadow_opacity=0.5,
                     auto_expand_canvas=True, canvas_padding=20):
        """Apply drop shadow effect to image"""

        try:
            # Convert ComfyUI tensor to PIL Image
            pil_image = tensor_to_pil(image)
            original_size = pil_image.size

            print(f"应用阴影效果: offset=({offset_x}, {offset_y}), blur={blur_radius}, spread={spread_radius}")
            print(f"阴影颜色: RGB({shadow_color_r}, {shadow_color_g}, {shadow_color_b}), 透明度={shadow_opacity}")

            # Ensure image has alpha channel for transparency support
            if pil_image.mode != 'RGBA':
                pil_image = pil_image.convert('RGBA')

            # Calculate canvas size if auto-expand is enabled
            if auto_expand_canvas:
                # Calculate required canvas expansion based on shadow parameters
                max_blur_spread = blur_radius + max(0, spread_radius)
                required_padding_x = max(canvas_padding, abs(offset_x) + max_blur_spread)
                required_padding_y = max(canvas_padding, abs(offset_y) + max_blur_spread)

                new_width = original_size[0] + 2 * required_padding_x
                new_height = original_size[1] + 2 * required_padding_y

                # Position of original image in expanded canvas
                image_x = required_padding_x
                image_y = required_padding_y
            else:
                # Use original size
                new_width, new_height = original_size
                image_x = 0
                image_y = 0

            # Create expanded canvas
            canvas = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))

            # Create shadow
            shadow = self._create_shadow(pil_image, spread_radius, blur_radius,
                                       shadow_color_r, shadow_color_g, shadow_color_b, shadow_opacity)

            # Calculate shadow position
            shadow_x = image_x + offset_x
            shadow_y = image_y + offset_y

            # Paste shadow onto canvas
            if shadow.size[0] > 0 and shadow.size[1] > 0:
                # Ensure shadow position is within canvas bounds
                shadow_x = max(0, min(shadow_x, new_width - shadow.size[0]))
                shadow_y = max(0, min(shadow_y, new_height - shadow.size[1]))

                canvas.paste(shadow, (shadow_x, shadow_y), shadow)

            # Paste original image on top of shadow
            if auto_expand_canvas:
                canvas.paste(pil_image, (image_x, image_y), pil_image)
            else:
                # For non-expanded canvas, just composite the shadow behind the original
                canvas = Image.alpha_composite(canvas.convert('RGBA'), pil_image.convert('RGBA'))

            # Convert back to ComfyUI tensor format
            result_tensor = pil_to_tensor(canvas)

            print(f"阴影效果应用完成: {original_size} -> {canvas.size}")
            return (result_tensor,)

        except Exception as e:
            print(f"错误：应用阴影效果失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return (image,)  # Return original image on error

    def _create_shadow(self, image, spread_radius, blur_radius, color_r, color_g, color_b, opacity):
        """Create shadow from image alpha channel"""

        # Extract alpha channel to create shadow mask
        if image.mode == 'RGBA':
            alpha = image.split()[-1]
        else:
            # If no alpha channel, use the entire image as mask
            alpha = Image.new('L', image.size, 255)

        # Apply spread radius (dilate/erode the alpha mask)
        if spread_radius != 0:
            alpha = self._apply_spread(alpha, spread_radius)

        # Create colored shadow from alpha mask
        shadow_color = (color_r, color_g, color_b, int(255 * opacity))
        shadow = Image.new('RGBA', alpha.size, (0, 0, 0, 0))

        # Apply color to alpha mask
        shadow_pixels = []
        alpha_pixels = list(alpha.getdata())

        for alpha_val in alpha_pixels:
            if alpha_val > 0:
                # Scale alpha by shadow opacity
                final_alpha = int((alpha_val / 255.0) * shadow_color[3])
                shadow_pixels.append((color_r, color_g, color_b, final_alpha))
            else:
                shadow_pixels.append((0, 0, 0, 0))

        shadow.putdata(shadow_pixels)

        # Apply blur
        if blur_radius > 0:
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        return shadow

    def _apply_spread(self, alpha_mask, spread_radius):
        """Apply spread effect (dilate/erode) to alpha mask"""
        if spread_radius == 0:
            return alpha_mask

        try:
            # Try scipy implementation first
            from scipy import ndimage
            alpha_array = np.array(alpha_mask)

            if spread_radius > 0:
                # Positive spread: dilate (expand the shadow)
                binary_mask = alpha_array > 0
                dilated = ndimage.binary_dilation(binary_mask, iterations=spread_radius)
                result = (dilated * 255).astype(np.uint8)
            else:
                # Negative spread: erode (shrink the shadow)
                binary_mask = alpha_array > 0
                eroded = ndimage.binary_erosion(binary_mask, iterations=abs(spread_radius))
                result = (eroded * 255).astype(np.uint8)

            return Image.fromarray(result, 'L')
        except ImportError:
            # Fallback to PIL-only implementation
            return self._apply_spread_fallback(alpha_mask, spread_radius)

    def _apply_spread_fallback(self, alpha_mask, spread_radius):
        """Fallback spread implementation without scipy"""
        if spread_radius == 0:
            return alpha_mask

        # Simple implementation using PIL filters
        if spread_radius > 0:
            # Positive spread: use MaxFilter to expand
            for _ in range(abs(spread_radius)):
                alpha_mask = alpha_mask.filter(ImageFilter.MaxFilter(3))
        else:
            # Negative spread: use MinFilter to shrink
            for _ in range(abs(spread_radius)):
                alpha_mask = alpha_mask.filter(ImageFilter.MinFilter(3))

        return alpha_mask
