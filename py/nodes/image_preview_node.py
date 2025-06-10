try:
    from PIL import Image
    from ..utils.image_utils import apply_background, create_checkerboard_background, pil_to_comfyui_format
    _image_support = True
except ImportError as e:
    print(f"Warning: Image support not available in image_preview_node: {e}")
    _image_support = False

from io import BytesIO
from .base_node import BaseNode
from ..utils.i18n import t

class DCIImagePreview(BaseNode):
    """ComfyUI node for previewing DCI Image data"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("dci_image_data"): ("DCI_IMAGE_DATA",),
            },
            "optional": {
                t("preview_background"): ([t("transparent"), t("white"), t("black"), t("checkerboard")], {"default": t("checkerboard")}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Preview')}"
    OUTPUT_NODE = True

    def _execute(self, **kwargs):
        """Preview DCI Image data"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        dci_image_data = kwargs.get(t("dci_image_data")) if t("dci_image_data") in kwargs else kwargs.get("dci_image_data")
        preview_background = kwargs.get(t("preview_background")) if t("preview_background") in kwargs else kwargs.get("preview_background", "checkerboard")

        return self._execute_impl(dci_image_data, preview_background)

    def _execute_impl(self, dci_image_data, preview_background="checkerboard"):
        """Preview DCI image data"""
        if not _image_support:
            return {"ui": {"text": ["Image support not available - missing PIL/torch dependencies"]}}

        if not dci_image_data or not isinstance(dci_image_data, dict):
            return {"ui": {"text": ["Invalid DCI image data"]}}

        # Get the PIL image from DCI data
        pil_image = dci_image_data.get('pil_image')
        if pil_image is None:
            # Try to reconstruct from binary content
            content = dci_image_data.get('content')
            if content:
                pil_image = Image.open(BytesIO(content))
            else:
                return {"ui": {"text": ["No image data found in DCI image"]}}

        # Create preview image with background
        preview_image = apply_background(pil_image, preview_background)

        # Convert to ComfyUI format
        preview_base64 = pil_to_comfyui_format(preview_image, "dci_preview")

        # Create UI output with only image preview
        ui_output = {
            "ui": {
                "images": [preview_base64]
            }
        }

        print(f"DCI Image Preview: {dci_image_data.get('path', 'unknown')} - {pil_image.size} - {pil_image.mode}")
        return ui_output
