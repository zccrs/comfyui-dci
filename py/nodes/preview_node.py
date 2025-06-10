try:
    from PIL import Image
    from ..utils.image_utils import create_checkerboard_background, pil_to_comfyui_format
    _image_support = True
except ImportError as e:
    print(f"Warning: Image support not available in preview_node: {e}")
    _image_support = False

from ..utils.ui_utils import format_image_info
from .base_node import BaseNode
from ..utils.i18n import t

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
                t("dci_binary_data"): ("BINARY_DATA",),
            },
            "optional": {
                t("light_background_color"): ([t("light_gray"), t("dark_gray"), t("white"), t("black"), t("transparent"), t("checkerboard"), t("blue"), t("green"), t("red"), t("yellow"), t("cyan"), t("magenta"), t("orange"), t("purple"), t("pink"), t("brown"), t("navy"), t("teal"), t("olive"), t("maroon")], {"default": t("light_gray")}),
                t("dark_background_color"): ([t("light_gray"), t("dark_gray"), t("white"), t("black"), t("transparent"), t("checkerboard"), t("blue"), t("green"), t("red"), t("yellow"), t("cyan"), t("magenta"), t("orange"), t("purple"), t("pink"), t("brown"), t("navy"), t("teal"), t("olive"), t("maroon")], {"default": t("dark_gray")}),
                t("text_font_size"): ("INT", {"default": 18, "min": 8, "max": 50, "step": 1}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Preview')}"
    OUTPUT_NODE = True

    def _execute(self, **kwargs):
        """Preview DCI file contents with in-node display"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        dci_binary_data = kwargs.get(t("dci_binary_data")) if t("dci_binary_data") in kwargs else kwargs.get("dci_binary_data")
        light_background_color = kwargs.get(t("light_background_color")) if t("light_background_color") in kwargs else kwargs.get("light_background_color", t("light_gray"))
        dark_background_color = kwargs.get(t("dark_background_color")) if t("dark_background_color") in kwargs else kwargs.get("dark_background_color", t("dark_gray"))
        text_font_size = kwargs.get(t("text_font_size")) if t("text_font_size") in kwargs else kwargs.get("text_font_size", 18)

        # Convert translated color names back to internal English names for processing
        light_bg_internal = self._translate_color_to_internal(light_background_color)
        dark_bg_internal = self._translate_color_to_internal(dark_background_color)

        return self._execute_impl(dci_binary_data, light_bg_internal, dark_bg_internal, text_font_size)

    def _translate_color_to_internal(self, translated_color):
        """Convert translated color name back to internal English name"""
        # Create reverse mapping from translated names to internal names
        color_mapping = {
            t("light_gray"): "light_gray",
            t("dark_gray"): "dark_gray",
            t("white"): "white",
            t("black"): "black",
            t("transparent"): "transparent",
            t("checkerboard"): "checkerboard",
            t("blue"): "blue",
            t("green"): "green",
            t("red"): "red",
            t("yellow"): "yellow",
            t("cyan"): "cyan",
            t("magenta"): "magenta",
            t("orange"): "orange",
            t("purple"): "purple",
            t("pink"): "pink",
            t("brown"): "brown",
            t("navy"): "navy",
            t("teal"): "teal",
            t("olive"): "olive",
            t("maroon"): "maroon",
        }
        return color_mapping.get(translated_color, translated_color)

    def _execute_impl(self, dci_binary_data, light_background_color="light_gray", dark_background_color="dark_gray", text_font_size=18):
        """Preview DCI file contents with in-node display"""
        try:
            if not _image_support:
                error_msg = "❌ 错误：图像支持不可用\n缺少 PIL/torch 依赖库"
                return {"ui": {"text": [error_msg]}}

            # Check if binary data is provided
            if dci_binary_data is None:
                error_msg = "❌ 错误：未提供 DCI 二进制数据\n"
                error_msg += "请确保连接了有效的 DCI 二进制数据输入。\n"
                error_msg += "数据来源可以是：DCI File 节点或 Binary File Loader 节点"
                return {"ui": {"text": [error_msg]}}

            if not isinstance(dci_binary_data, bytes):
                error_msg = f"❌ 错误：DCI 数据类型不正确\n"
                error_msg += f"期望类型：bytes，实际类型：{type(dci_binary_data)}\n"
                error_msg += f"数据内容：{str(dci_binary_data)[:100]}..."
                return {"ui": {"text": [error_msg]}}

            if len(dci_binary_data) == 0:
                error_msg = "❌ 错误：DCI 二进制数据为空\n"
                error_msg += "请检查数据源是否正确生成了 DCI 文件内容"
                return {"ui": {"text": [error_msg]}}

            # Use binary data
            reader = DCIReader(binary_data=dci_binary_data)
            source_name = "binary_data"

            # Read DCI data with detailed error reporting
            if not reader.read():
                error_msg = "❌ 错误：无法读取 DCI 数据\n"
                error_msg += f"数据大小：{len(dci_binary_data)} 字节\n"
                error_msg += f"数据开头：{dci_binary_data[:32].hex() if len(dci_binary_data) >= 32 else dci_binary_data.hex()}\n"
                error_msg += "可能原因：\n"
                error_msg += "1. 数据不是有效的 DCI 格式\n"
                error_msg += "2. 文件头损坏或格式不正确\n"
                error_msg += "3. 数据在传输过程中被截断"

                # Create error preview image
                error_preview = self._create_error_preview_image(error_msg, text_font_size)
                error_base64 = pil_to_comfyui_format(error_preview, "dci_error_preview")

                return {"ui": {"images": [error_base64], "text": [error_msg]}}

            # Extract images with detailed error reporting
            images = reader.get_icon_images()
            if not images:
                error_msg = "❌ 错误：DCI 文件中未找到图像\n"
                error_msg += f"DCI 文件读取成功，数据大小：{len(dci_binary_data)} 字节\n"

                # Try to get more info from reader
                try:
                    if hasattr(reader, '_directories') and reader._directories:
                        error_msg += f"发现 {len(reader._directories)} 个目录，但无图像数据\n"
                    else:
                        error_msg += "未发现任何目录结构\n"
                except:
                    pass

                error_msg += "可能原因：\n"
                error_msg += "1. DCI 文件为空或只包含目录结构\n"
                error_msg += "2. 图像数据解析失败\n"
                error_msg += "3. 文件格式版本不兼容"

                # Create error preview image
                error_preview = self._create_error_preview_image(error_msg, text_font_size)
                error_base64 = pil_to_comfyui_format(error_preview, "dci_error_preview")

                return {"ui": {"images": [error_base64], "text": [error_msg]}}

            # 根据色调将图像分成Light和Dark两组
            light_images = [img for img in images if img['tone'].lower() == 'light']
            dark_images = [img for img in images if img['tone'].lower() == 'dark']
            other_images = [img for img in images if img['tone'].lower() not in ('light', 'dark')]

            # 确定背景颜色
            light_bg_color = self._get_background_color(light_background_color)
            dark_bg_color = self._get_background_color(dark_background_color)

            # 生成预览图像
            generator = DCIPreviewGenerator(font_size=text_font_size)

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

        except Exception as e:
            # Comprehensive error reporting with preview image
            import traceback
            error_msg = f"❌ 严重错误：DCI 预览过程中发生异常\n"
            error_msg += f"错误类型：{type(e).__name__}\n"
            error_msg += f"错误信息：{str(e)}\n"
            error_msg += f"数据状态：{type(dci_binary_data)} ({len(dci_binary_data) if isinstance(dci_binary_data, bytes) else 'N/A'} 字节)\n"
            error_msg += "\n详细错误堆栈：\n"
            error_msg += traceback.format_exc()

            # Create error preview image
            error_preview = self._create_error_preview_image(error_msg, text_font_size)
            error_base64 = pil_to_comfyui_format(error_preview, "dci_error_preview")

            return {"ui": {"images": [error_base64], "text": [error_msg]}}

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
        # Create a checkerboard pattern background
        width, height = preview_image.size
        checkerboard = Image.new('RGB', (width, height), (255, 255, 255))

        # Create checkerboard pattern
        checker_size = 16  # Size of each checker square
        for y in range(0, height, checker_size):
            for x in range(0, width, checker_size):
                # Determine if this square should be light or dark
                is_dark = ((x // checker_size) + (y // checker_size)) % 2 == 1
                color = (200, 200, 200) if is_dark else (255, 255, 255)

                # Draw the checker square
                for py in range(y, min(y + checker_size, height)):
                    for px in range(x, min(x + checker_size, width)):
                        checkerboard.putpixel((px, py), color)

        # If the preview image has transparency, composite it over the checkerboard
        if preview_image.mode == 'RGBA':
            checkerboard.paste(preview_image, (0, 0), preview_image)
            return checkerboard
        else:
            # If no transparency, just return the original
            return preview_image

    def _create_error_preview_image(self, error_msg, font_size=18):
        """Create an error preview image with the error message"""
        try:
            from PIL import ImageDraw, ImageFont

            # Calculate image size based on error message length
            lines = error_msg.split('\n')
            max_line_length = max(len(line) for line in lines) if lines else 50

            # Estimate dimensions
            char_width = max(6, font_size // 2)
            line_height = max(12, font_size + 4)

            width = min(800, max(400, max_line_length * char_width))
            height = min(600, max(200, len(lines) * line_height + 40))

            # Create image with red background
            error_image = Image.new('RGB', (width, height), (220, 50, 50))
            draw = ImageDraw.Draw(error_image)

            # Try to load a font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()

            # Draw error icon
            draw.text((10, 10), "❌", fill=(255, 255, 255), font=font)

            # Draw error message
            y_offset = 40
            for line in lines[:20]:  # Limit to first 20 lines
                if y_offset + line_height > height - 10:
                    break
                draw.text((10, y_offset), line[:80], fill=(255, 255, 255), font=font)  # Limit line length
                y_offset += line_height

            return error_image

        except Exception as e:
            # Fallback: create a simple red image with basic text
            fallback_image = Image.new('RGB', (400, 200), (220, 50, 50))
            draw = ImageDraw.Draw(fallback_image)
            draw.text((10, 10), "Error occurred", fill=(255, 255, 255))
            draw.text((10, 30), f"Type: {type(e).__name__}", fill=(255, 255, 255))
            draw.text((10, 50), "Check console for details", fill=(255, 255, 255))
            return fallback_image

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
