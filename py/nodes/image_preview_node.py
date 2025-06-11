try:
    from PIL import Image
    from ..utils.image_utils import apply_background, create_checkerboard_background, pil_to_comfyui_format, pil_to_tensor
    _image_support = True
except ImportError as e:
    print(f"Warning: Image support not available in image_preview_node: {e}")
    _image_support = False

from io import BytesIO
from .base_node import BaseNode
from ..utils.i18n import t
from ..utils.enums import (
    BackgroundColor, translate_ui_to_enum, get_enum_ui_options, get_enum_default_ui_value
)

class DCIImagePreview(BaseNode):
    """ComfyUI node for previewing DCI Image data"""

    @classmethod
    def INPUT_TYPES(cls):
        # Filter BackgroundColor enum to only include preview-relevant options
        preview_backgrounds = [BackgroundColor.TRANSPARENT, BackgroundColor.WHITE, BackgroundColor.BLACK, BackgroundColor.CHECKERBOARD]
        return {
            "required": {
                t("dci_image_data"): ("DCI_IMAGE_DATA,DCI_IMAGE_DATA_LIST",),
            },
            "optional": {
                t("preview_background"): ([t(bg.value) for bg in preview_backgrounds], {"default": t(BackgroundColor.CHECKERBOARD.value)}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = (t("preview_images"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Preview')}"
    OUTPUT_NODE = True

    def _execute(self, **kwargs):
        """Preview DCI Image data with IMAGE output"""
        # Extract parameters with translation support and convert to enums
        # Try both translated and original parameter names for compatibility
        dci_image_data = kwargs.get(t("dci_image_data")) if t("dci_image_data") in kwargs else kwargs.get("dci_image_data")

        # Convert UI value to enum for type safety
        preview_bg_ui = kwargs.get(t("preview_background")) if t("preview_background") in kwargs else kwargs.get("preview_background")
        preview_background = translate_ui_to_enum(preview_bg_ui, BackgroundColor, t) if preview_bg_ui else BackgroundColor.CHECKERBOARD

        return self._execute_impl(dci_image_data, preview_background)

    def _execute_impl(self, dci_image_data, preview_background: BackgroundColor = BackgroundColor.CHECKERBOARD):
        """Preview DCI image data with IMAGE output"""
        if not _image_support:
            return {"ui": {"text": ["Image support not available - missing PIL/torch dependencies"]}, "result": (None,)}

        # Handle both single DCI image data and list of DCI image data
        image_data_list = []
        if isinstance(dci_image_data, list):
            # Multiple DCI image data
            image_data_list = dci_image_data
            print(f"处理 {len(image_data_list)} 个DCI图像数据")
        else:
            # Single DCI image data
            image_data_list = [dci_image_data]
            print(f"处理单个DCI图像数据")

        # Process each DCI image data and generate previews
        preview_images = []
        ui_images = []
        ui_texts = []

        for i, image_data in enumerate(image_data_list):
            print(f"正在处理第 {i+1}/{len(image_data_list)} 个DCI图像...")

            # Validate individual image data
            if not image_data or not isinstance(image_data, dict):
                error_msg = f"❌ 错误：第{i+1}个DCI图像数据无效"
                ui_texts.append(error_msg)

                # Create error preview image
                error_preview = self._create_error_preview_image(error_msg)
                preview_images.append(error_preview)
                ui_images.append(pil_to_comfyui_format(error_preview, f"dci_image_error_{i}"))
                continue

            # Process individual DCI image
            result = self._process_single_dci_image(image_data, preview_background, i)

            if result['preview_image']:
                preview_images.append(result['preview_image'])
                ui_images.append(result['ui_image'])
                ui_texts.append(result['info_text'])
            else:
                # Error case
                error_preview = self._create_error_preview_image(result['error_msg'])
                preview_images.append(error_preview)
                ui_images.append(pil_to_comfyui_format(error_preview, f"dci_image_error_{i}"))
                ui_texts.append(result['error_msg'])

        # Convert PIL images to ComfyUI tensor format for IMAGE output
        if preview_images:
            # Convert all preview images to tensors and stack them
            image_tensors = []
            for pil_img in preview_images:
                tensor = pil_to_tensor(pil_img)
                image_tensors.append(tensor)

            # Stack tensors into batch
            import torch
            if len(image_tensors) == 1:
                output_tensor = image_tensors[0]
            else:
                output_tensor = torch.cat(image_tensors, dim=0)

            print(f"生成了 {len(preview_images)} 个DCI图像预览，输出张量形状: {output_tensor.shape}")
        else:
            output_tensor = None

        # Create UI output
        ui_output = {
            "ui": {
                "images": ui_images,
                "text": ui_texts
            }
        }

        return {**ui_output, "result": (output_tensor,)}

    def _process_single_dci_image(self, image_data, preview_background, index):
        """Process a single DCI image data and return preview result"""
        try:
            # Get the PIL image from DCI data
            pil_image = image_data.get('pil_image')
            if pil_image is None:
                # Try to reconstruct from binary content
                content = image_data.get('content')
                if content:
                    pil_image = Image.open(BytesIO(content))
                else:
                    error_msg = f"第{index+1}个DCI图像中未找到图像数据"
                    return {
                        'preview_image': None,
                        'ui_image': None,
                        'info_text': error_msg,
                        'error_msg': error_msg
                    }

            # Create preview image with background using enum string value
            preview_image = apply_background(pil_image, str(preview_background))

            # Convert to ComfyUI format for UI display
            preview_base64 = pil_to_comfyui_format(preview_image, f"dci_image_preview_{index}")

            # Create info text
            path = image_data.get('path', 'unknown')
            info_text = f"DCI图像预览 {index+1}: {path} - {pil_image.size} - {pil_image.mode}"

            return {
                'preview_image': preview_image,
                'ui_image': preview_base64,
                'info_text': info_text,
                'error_msg': None
            }

        except Exception as e:
            error_msg = f"❌ 处理第{index+1}个DCI图像时发生异常: {str(e)}"
            return {
                'preview_image': None,
                'ui_image': None,
                'info_text': error_msg,
                'error_msg': error_msg
            }

    def _create_error_preview_image(self, error_msg):
        """Create a simple error preview image"""
        try:
            # Create a simple red error image
            error_image = Image.new('RGB', (400, 200), color='red')
            return error_image
        except:
            # Fallback: return None if image creation fails
            return None
