from ..utils.image_utils import apply_background, create_checkerboard_background, pil_to_comfyui_format
from ..utils.ui_utils import format_image_info, format_binary_info
from .base_node import BaseNode

class DCIImageDebug(BaseNode):
    """ComfyUI node for debugging and previewing DCI Image data"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dci_image_data": ("DCI_IMAGE_DATA",),
            },
            "optional": {
                "show_metadata": ("BOOLEAN", {"default": True}),
                "show_binary_info": ("BOOLEAN", {"default": True}),
                "preview_background": (["transparent", "white", "black", "checkerboard"], {"default": "checkerboard"}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "debug_dci_image"
    CATEGORY = "DCI/Debug"
    OUTPUT_NODE = True

    def _execute(self, dci_image_data, show_metadata=True, show_binary_info=True, preview_background="checkerboard"):
        """Debug and preview DCI image data"""
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
        preview_base64 = pil_to_comfyui_format(preview_image, "dci_debug")

        # Generate debug information
        debug_lines = ["🔍 DCI Image Debug Information", "=" * 40, ""]

        if show_metadata:
            debug_lines.extend([
                "📋 基本信息:",
                format_image_info(dci_image_data),
                ""
            ])

        if show_binary_info and dci_image_data.get('content'):
            debug_lines.append(format_binary_info(dci_image_data['content']))

        # PIL Image information
        if pil_image:
            debug_lines.extend([
                "🖼️  PIL图像信息:",
                f"  📐 尺寸: {pil_image.size[0]}×{pil_image.size[1]}px",
                f"  🎨 颜色模式: {pil_image.mode}",
                f"  📊 格式: {getattr(pil_image, 'format', 'N/A')}",
                ""
            ])

        # Add validation status
        debug_lines.extend([
            "✅ 验证状态:",
            f"  📁 路径格式: {'✓' if dci_image_data.get('path') else '✗'}",
            f"  🔢 二进制数据: {'✓' if dci_image_data.get('content') else '✗'}",
            f"  🖼️  PIL图像: {'✓' if dci_image_data.get('pil_image') else '✗'}",
            f"  📊 元数据完整: {'✓' if all(k in dci_image_data for k in ['size', 'state', 'tone', 'scale', 'format']) else '✗'}",
        ])

        # Create UI output
        ui_output = {
            "ui": {
                "images": [preview_base64],
                "text": ["\n".join(debug_lines)]
            }
        }

        print(f"DCI Image Debug: {dci_image_data.get('path', 'unknown')} - {pil_image.size} - {pil_image.mode}")
        return ui_output
