try:
    from PIL import Image
    from ..utils.image_utils import create_checkerboard_background, pil_to_comfyui_format
    _image_support = True
except ImportError as e:
    print(f"Warning: Image support not available in preview_node: {e}")
    _image_support = False

from ..utils.ui_utils import format_image_info
from .base_node import BaseNode

try:
    from ..dci_reader import DCIReader, DCIPreviewGenerator
except ImportError:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(current_dir))
    from dci_reader import DCIReader, DCIPreviewGenerator

class DCIAnalysisNode(BaseNode):
    """ComfyUI node for analyzing DCI file contents and outputting text summary"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dci_binary_data": ("BINARY_DATA",),
            },
            "optional": {
                "text_font_size": ("INT", {"default": 18, "min": 8, "max": 50, "step": 1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis_text",)
    FUNCTION = "execute"
    CATEGORY = "DCI/Analysis"

    def _execute(self, dci_binary_data, text_font_size=18):
        """Analyze DCI file contents and return detailed text summary"""
        # Use binary data
        reader = DCIReader(binary_data=dci_binary_data)
        source_name = "binary_data"

        # Read DCI data
        if not reader.read():
            return ("Failed to read DCI data",)

        # Extract images
        images = reader.get_icon_images()
        if not images:
            return ("No images found in DCI file",)

        # Generate detailed metadata summary
        summary_text = self._format_detailed_summary(images, source_name, text_font_size)

        print(f"DCI analysis completed: {len(images)} images analyzed")
        return (summary_text,)

    def _format_detailed_summary(self, images, source_name, text_font_size=18):
        """Format detailed metadata summary as text"""
        if not images:
            return "No images available"

        # 根据色调将图像分组
        light_images = [img for img in images if img['tone'].lower() == 'light']
        dark_images = [img for img in images if img['tone'].lower() == 'dark']
        other_images = [img for img in images if img['tone'].lower() not in ('light', 'dark')]

        # Calculate summary statistics
        total_images = len(images)
        total_file_size = sum(img['file_size'] for img in images)

        # Collect unique values across all images
        sizes = sorted(set(img['size'] for img in images))
        states = sorted(set(img['state'] for img in images))
        tones = sorted(set(img['tone'] for img in images))
        scales = sorted(set(img['scale'] for img in images))
        formats = sorted(set(img['format'] for img in images))

        # Adjust spacing based on font size
        spacing = "" if text_font_size <= 10 else "\n"
        indentation = "   " if text_font_size <= 14 else " "
        separator = "=" * max(20, 50 - text_font_size)

        # Build summary sections
        lines = [
            f"📁 DCI 数据源: {source_name} (字体大小: {text_font_size})",
            f"🖼️  图像总数: {total_images} (Light: {len(light_images)}, Dark: {len(dark_images)}, 其他: {len(other_images)})",
            f"🗂️  文件总大小: {total_file_size:,} 字节 ({total_file_size/1024:.1f} KB)",
            "",
            "📏 图标尺寸:",
            f"{indentation}{', '.join(f'{size}px' for size in sizes)}",
            "",
            "🎭 图标状态:",
            f"{indentation}{', '.join(states)}",
            "",
            "🎨 色调类型:",
            f"{indentation}{', '.join(tones)}",
            "",
            "🔍 缩放因子:",
            f"{indentation}{', '.join(f'{scale:g}x' for scale in scales)}",
            "",
            "🗂️  图像格式:",
            f"{indentation}{', '.join(formats)}",
            "",
        ]

        # Add image groups
        self._add_image_group(lines, light_images, "Light", indentation)
        self._add_image_group(lines, dark_images, "Dark", indentation)
        self._add_image_group(lines, other_images, "其他", indentation)

        return "\n".join(lines)

    def _add_image_group(self, lines, images, group_name, indentation):
        """Add a group of images to the summary"""
        if not images:
            return

        lines.extend([
            f"📂 {group_name} 文件路径列表:",
        ])

        # Sort images for consistent display
        sorted_images = sorted(images, key=lambda x: (x['size'], x['state'], x['scale']))
        for img in sorted_images:
            path = img.get('path', 'unknown_path')
            filename = img.get('filename', 'unknown_file')
            full_path = f"/{path}/{filename}"
            lines.append(f"{indentation}{full_path}")

        lines.append("")
        lines.extend([
            f"🌟 {group_name} 主题图像:",
            ""
        ])

        for i, img in enumerate(sorted_images, 1):
            lines.extend([format_image_info(img, i), ""])
