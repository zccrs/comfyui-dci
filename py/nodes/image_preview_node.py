from PIL import Image
from io import BytesIO
from ..utils.image_utils import apply_background, create_checkerboard_background, pil_to_comfyui_format
from .base_node import BaseNode

class DCIImagePreview(BaseNode):
    """ComfyUI node for previewing DCI Image data"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dci_image_data": ("DCI_IMAGE_DATA",),
            },
            "optional": {
                "preview_background": (["transparent", "white", "black", "checkerboard"], {"default": "checkerboard"}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "preview_dci_image"
    CATEGORY = "Preview"
    OUTPUT_NODE = True

    def _execute(self, dci_image_data, preview_background="checkerboard"):
        """Preview DCI image data"""
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
