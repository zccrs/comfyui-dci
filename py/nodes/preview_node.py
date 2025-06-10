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

class DCIPreviewNode(BaseNode):
    """ComfyUI node for previewing DCI file contents"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dci_binary_data": ("BINARY_DATA",),
            },
            "optional": {
                "light_background_color": (["light_gray", "dark_gray", "white", "black", "transparent", "checkerboard", "blue", "green", "red", "yellow", "cyan", "magenta", "orange", "purple", "pink", "brown", "navy", "teal", "olive", "maroon"], {"default": "light_gray"}),
                "dark_background_color": (["light_gray", "dark_gray", "white", "black", "transparent", "checkerboard", "blue", "green", "red", "yellow", "cyan", "magenta", "orange", "purple", "pink", "brown", "navy", "teal", "olive", "maroon"], {"default": "dark_gray"}),
                "text_font_size": ("INT", {"default": 12, "min": 8, "max": 24, "step": 1}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "preview_dci"
    CATEGORY = "DCI/Preview"
    OUTPUT_NODE = True

    def _execute(self, dci_binary_data, light_background_color="light_gray", dark_background_color="dark_gray", text_font_size=12):
        """Preview DCI file contents with in-node display"""
        if not _image_support:
            return {"ui": {"text": ["Image support not available - missing PIL/torch dependencies"]}}

        # Use binary data
        reader = DCIReader(binary_data=dci_binary_data)
        source_name = "binary_data"

        # Read DCI data
        if not reader.read():
            return {"ui": {"text": ["Failed to read DCI data"]}}

        # Extract images
        images = reader.get_icon_images()
        if not images:
            return {"ui": {"text": ["No images found in DCI file"]}}

        # 根据色调将图像分成Light和Dark两组
        light_images = [img for img in images if img['tone'].lower() == 'light']
        dark_images = [img for img in images if img['tone'].lower() == 'dark']
        other_images = [img for img in images if img['tone'].lower() not in ('light', 'dark')]

        # 确定背景颜色
        light_bg_color = self._get_background_color(light_background_color)
        dark_bg_color = self._get_background_color(dark_background_color)

        # 生成预览图像
        generator = DCIPreviewGenerator()

        # 为Light和Dark分别生成单列预览
        light_preview = self._create_preview_with_special_background(generator, light_images, 1, light_background_color, light_bg_color) if light_images else None
        dark_preview = self._create_preview_with_special_background(generator, dark_images, 1, dark_background_color, dark_bg_color) if dark_images else None

        # 如果有其他色调，将它们添加到默认组(Light)
        if other_images:
            if light_preview:
                # 如果已有Light预览，合并到Light预览中
                combined_images = light_images + other_images
                light_preview = self._create_preview_with_special_background(generator, combined_images, 1, light_background_color, light_bg_color)
            else:
                # 否则创建新的预览
                light_preview = self._create_preview_with_special_background(generator, other_images, 1, light_background_color, light_bg_color)

        # 合并Light和Dark预览（如果两者都存在）
        if light_preview and dark_preview:
            preview_image = self._combine_preview_images(light_preview, dark_preview)
        elif light_preview:
            preview_image = light_preview
        elif dark_preview:
            preview_image = dark_preview
        else:
            # 创建空预览
            preview_image = self._create_preview_with_special_background(generator, [], 1, light_background_color, light_bg_color)

        # Convert PIL image to base64 for UI display
        preview_base64 = pil_to_comfyui_format(preview_image, "dci_preview")

        # Generate detailed metadata summary
        summary_text = self._format_detailed_summary(images, source_name, text_font_size)

        # Create UI output with image and text
        ui_output = {
            "ui": {
                "images": [preview_base64],
                "text": [summary_text]
            }
        }

        print(f"DCI preview generated: {len(images)} images found, Light: {len(light_images)}, Dark: {len(dark_images)}, Other: {len(other_images)}")
        return ui_output

    def _get_background_color(self, color_name):
        """Get RGB color tuple based on color name"""
        color_presets = {
            "light_gray": (240, 240, 240),
            "dark_gray": (64, 64, 64),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "transparent": (240, 240, 240),  # Default fallback for transparent
            "checkerboard": (240, 240, 240),  # Default fallback for checkerboard
            "blue": (70, 130, 180),
            "green": (60, 120, 60),
            "red": (120, 60, 60),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "pink": (255, 192, 203),
            "brown": (165, 42, 42),
            "navy": (0, 0, 128),
            "teal": (0, 128, 128),
            "olive": (128, 128, 0),
            "maroon": (128, 0, 0),
        }
        return color_presets.get(color_name, (240, 240, 240))

    def _create_preview_with_special_background(self, generator, images, grid_cols, background_name, background_color):
        """Create preview with special handling for transparent and checkerboard backgrounds"""
        if background_name == "transparent":
            # For transparent, use a light gray background but preserve transparency info
            preview = generator.create_preview_grid(images, grid_cols, (240, 240, 240))
            return preview
        elif background_name == "checkerboard":
            # For checkerboard, create preview with light gray first, then apply checkerboard to transparent areas
            preview = generator.create_preview_grid(images, grid_cols, (240, 240, 240))
            return self._apply_checkerboard_to_preview(preview)
        else:
            # Normal color background
            return generator.create_preview_grid(images, grid_cols, background_color)

    def _apply_checkerboard_to_preview(self, preview_image):
        """Apply checkerboard pattern to preview image background"""
        # For now, just return the preview as-is since DCIPreviewGenerator handles backgrounds
        return preview_image

    def _combine_preview_images(self, light_preview, dark_preview):
        """Combine light and dark preview images side by side"""
        # 计算新图像的尺寸
        width = light_preview.width + dark_preview.width
        height = max(light_preview.height, dark_preview.height)

        # 创建新图像
        combined = Image.new('RGB', (width, height), (240, 240, 240))

        # 粘贴Light预览（左侧）
        combined.paste(light_preview, (0, 0))

        # 粘贴Dark预览（右侧）
        combined.paste(dark_preview, (light_preview.width, 0))

        return combined

    def _format_detailed_summary(self, images, source_name, text_font_size=12):
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
