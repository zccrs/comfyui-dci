try:
    from PIL import Image
    from ..utils.image_utils import create_checkerboard_background, pil_to_comfyui_format, pil_to_tensor
    _image_support = True
except ImportError as e:
    print(f"Warning: Image support not available in preview_node: {e}")
    _image_support = False

try:
    from ..utils.ui_utils import format_image_info
    from .base_node import BaseNode
    from ..utils.i18n import t
    from ..utils.enums import (
        PreviewBackground, translate_ui_to_enum, get_enum_ui_options, get_enum_default_ui_value
    )
except ImportError:
    # Fallback for test environment
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

    try:
        from utils.ui_utils import format_image_info
        from nodes.base_node import BaseNode
        from utils.i18n import t
        from utils.enums import (
            PreviewBackground, translate_ui_to_enum, get_enum_ui_options, get_enum_default_ui_value
        )
    except ImportError as e:
        print(f"Warning: Could not import required modules: {e}")
        # Define minimal fallbacks
        def format_image_info(*args, **kwargs):
            return "Image info not available"

        def t(text):
            return text

        class PreviewBackground:
            LIGHT_GRAY = "light_gray"
            DARK_GRAY = "dark_gray"

        def translate_ui_to_enum(ui_value, enum_class, translator):
            return ui_value

        def get_enum_ui_options(enum_class, translator):
            return ["light_gray", "dark_gray"]

        def get_enum_default_ui_value(default_value, translator):
            return default_value

        class BaseNode:
            pass

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
                t("dci_binary_data"): ("BINARY_DATA,BINARY_DATA_LIST",),
            },
            "optional": {
                t("light_background_color"): (get_enum_ui_options(PreviewBackground, t), {"default": get_enum_default_ui_value(PreviewBackground.LIGHT_GRAY, t)}),
                t("dark_background_color"): (get_enum_ui_options(PreviewBackground, t), {"default": get_enum_default_ui_value(PreviewBackground.DARK_GRAY, t)}),
                t("text_font_size"): ("INT", {"default": 18, "min": 8, "max": 50, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = (t("preview_images"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Preview')}"
    OUTPUT_NODE = True

    def _execute(self, **kwargs):
        """Preview DCI file contents with in-node display and IMAGE output"""
        # Extract parameters with translation support and convert to enums
        # Try both translated and original parameter names for compatibility
        dci_binary_data = kwargs.get(t("dci_binary_data")) if t("dci_binary_data") in kwargs else kwargs.get("dci_binary_data")

        # Convert UI values to enums for type safety
        light_bg_ui = kwargs.get(t("light_background_color")) if t("light_background_color") in kwargs else kwargs.get("light_background_color")
        light_background_color = translate_ui_to_enum(light_bg_ui, PreviewBackground, t) if light_bg_ui else PreviewBackground.LIGHT_GRAY

        dark_bg_ui = kwargs.get(t("dark_background_color")) if t("dark_background_color") in kwargs else kwargs.get("dark_background_color")
        dark_background_color = translate_ui_to_enum(dark_bg_ui, PreviewBackground, t) if dark_bg_ui else PreviewBackground.DARK_GRAY

        text_font_size = kwargs.get(t("text_font_size")) if t("text_font_size") in kwargs else kwargs.get("text_font_size", 18)

        return self._execute_impl(dci_binary_data, light_background_color, dark_background_color, text_font_size)

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

    def _execute_impl(self, dci_binary_data, light_background_color: PreviewBackground = PreviewBackground.LIGHT_GRAY, dark_background_color: PreviewBackground = PreviewBackground.DARK_GRAY, text_font_size=18):
        """Preview DCI file contents with in-node display and IMAGE output"""
        try:
            if not _image_support:
                error_msg = "❌ 错误：图像支持不可用\n缺少 PIL/torch 依赖库"
                return {"ui": {"text": [error_msg]}, "result": (None,)}

            # Check if binary data is provided
            if dci_binary_data is None:
                error_msg = "❌ 错误：未提供 DCI 二进制数据\n"
                error_msg += "请确保连接了有效的 DCI 二进制数据输入。\n"
                error_msg += "数据来源可以是：DCI File 节点或 Binary File Loader 节点"
                return {"ui": {"text": [error_msg]}, "result": (None,)}

            # Handle both single binary data and list of binary data
            binary_data_list = []
            if isinstance(dci_binary_data, list):
                # Multiple binary data
                binary_data_list = dci_binary_data
                print(f"处理 {len(binary_data_list)} 个DCI二进制数据")
            else:
                # Single binary data
                binary_data_list = [dci_binary_data]
                print(f"处理单个DCI二进制数据")

            # Process each binary data and generate previews
            preview_images = []
            ui_images = []
            ui_texts = []

            for i, binary_data in enumerate(binary_data_list):
                print(f"正在处理第 {i+1}/{len(binary_data_list)} 个DCI文件...")

                # Validate individual binary data
                if not isinstance(binary_data, bytes):
                    error_msg = f"❌ 错误：第{i+1}个DCI数据类型不正确\n"
                    error_msg += f"期望类型：bytes，实际类型：{type(binary_data)}\n"
                    ui_texts.append(error_msg)

                    # Create error preview image
                    error_preview = self._create_error_preview_image(error_msg, text_font_size)
                    preview_images.append(error_preview)
                    ui_images.append(pil_to_comfyui_format(error_preview, f"dci_error_preview_{i}"))
                    continue

                if len(binary_data) == 0:
                    error_msg = f"❌ 错误：第{i+1}个DCI二进制数据为空\n"
                    error_msg += "请检查数据源是否正确生成了 DCI 文件内容"
                    ui_texts.append(error_msg)

                    # Create error preview image
                    error_preview = self._create_error_preview_image(error_msg, text_font_size)
                    preview_images.append(error_preview)
                    ui_images.append(pil_to_comfyui_format(error_preview, f"dci_error_preview_{i}"))
                    continue

                # Process individual DCI file
                result = self._process_single_dci(binary_data, light_background_color, dark_background_color, text_font_size, i)

                if result['preview_image']:
                    preview_images.append(result['preview_image'])
                    ui_images.append(result['ui_image'])
                    ui_texts.append(result['summary_text'])
                else:
                    # Error case
                    error_preview = self._create_error_preview_image(result['error_msg'], text_font_size)
                    preview_images.append(error_preview)
                    ui_images.append(pil_to_comfyui_format(error_preview, f"dci_error_preview_{i}"))
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

                print(f"生成了 {len(preview_images)} 个预览图像，输出张量形状: {output_tensor.shape}")
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

        except Exception as e:
            error_msg = f"❌ 预览生成异常: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()

            error_preview = self._create_error_preview_image(error_msg, text_font_size)
            error_base64 = pil_to_comfyui_format(error_preview, "dci_error_preview")

            return {
                "ui": {"images": [error_base64], "text": [error_msg]},
                "result": (pil_to_tensor(error_preview) if _image_support else None,)
            }

    def _process_single_dci(self, binary_data, light_background_color, dark_background_color, text_font_size, index):
        """Process a single DCI binary data and return preview result"""
        try:
            # Use binary data
            reader = DCIReader(binary_data=binary_data)
            source_name = f"binary_data_{index}"

            # Read DCI data with detailed error reporting
            if not reader.read():
                error_msg = f"❌ 错误：无法读取第{index+1}个DCI数据\n"
                error_msg += f"数据大小：{len(binary_data)} 字节\n"
                error_msg += f"数据开头：{binary_data[:32].hex() if len(binary_data) >= 32 else binary_data.hex()}\n"
                error_msg += "可能原因：\n"
                error_msg += "1. 数据不是有效的 DCI 格式\n"
                error_msg += "2. 文件头损坏或格式不正确\n"
                error_msg += "3. 数据在传输过程中被截断"

                return {
                    'preview_image': None,
                    'ui_image': None,
                    'summary_text': error_msg,
                    'error_msg': error_msg
                }

            # Extract images with detailed error reporting
            images = reader.get_icon_images()
            if not images:
                error_msg = f"❌ 错误：第{index+1}个DCI文件中未找到图像\n"
                error_msg += f"DCI 文件读取成功，数据大小：{len(binary_data)} 字节\n"

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

                return {
                    'preview_image': None,
                    'ui_image': None,
                    'summary_text': error_msg,
                    'error_msg': error_msg
                }

            # 根据色调将图像分成Light和Dark两组
            light_images = [img for img in images if img['tone'].lower() == 'light']
            dark_images = [img for img in images if img['tone'].lower() == 'dark']
            other_images = [img for img in images if img['tone'].lower() not in ('light', 'dark')]

            # 确定背景颜色
            light_bg_color = self._get_background_color(str(light_background_color))
            dark_bg_color = self._get_background_color(str(dark_background_color))

            # 生成预览图像
            generator = DCIPreviewGenerator(font_size=text_font_size)

            # 为Light和Dark分别生成单列预览
            light_preview = self._create_preview_with_special_background(generator, light_images, 1, str(light_background_color), light_bg_color) if light_images else None
            dark_preview = self._create_preview_with_special_background(generator, dark_images, 1, str(dark_background_color), dark_bg_color) if dark_images else None

            # 如果有其他色调，将它们添加到默认组(Light)
            if other_images:
                if light_preview:
                    # 如果已有Light预览，合并到Light预览中
                    combined_images = light_images + other_images
                    light_preview = self._create_preview_with_special_background(generator, combined_images, 1, str(light_background_color), light_bg_color)
                else:
                    # 否则创建新的预览
                    light_preview = self._create_preview_with_special_background(generator, other_images, 1, str(light_background_color), light_bg_color)

            # 合并Light和Dark预览（如果两者都存在）
            if light_preview and dark_preview:
                preview_image = self._combine_preview_images(light_preview, dark_preview)
            elif light_preview:
                preview_image = light_preview
            elif dark_preview:
                preview_image = dark_preview
            else:
                # 创建空预览
                preview_image = self._create_preview_with_special_background(generator, [], 1, str(light_background_color), light_bg_color)

            # Convert PIL image to base64 for UI display
            preview_base64 = pil_to_comfyui_format(preview_image, f"dci_preview_{index}")

            # Generate summary text
            summary_text = self._format_detailed_summary(images, source_name, text_font_size)

            return {
                'preview_image': preview_image,
                'ui_image': preview_base64,
                'summary_text': summary_text,
                'error_msg': None
            }

        except Exception as e:
            error_msg = f"❌ 处理第{index+1}个DCI文件时发生异常: {str(e)}"
            return {
                'preview_image': None,
                'ui_image': None,
                'summary_text': error_msg,
                'error_msg': error_msg
            }

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
            # For transparent, create preview with white background first
            # Then convert to RGBA with transparent background
            preview = generator.create_preview_grid(images, grid_cols, (255, 255, 255))
            return self._apply_transparent_background(preview)
        elif background_name == "checkerboard":
            # For checkerboard, create preview with white background first, then apply checkerboard
            preview = generator.create_preview_grid(images, grid_cols, (255, 255, 255))
            return self._apply_checkerboard_to_preview(preview)
        else:
            # Normal color background
            return generator.create_preview_grid(images, grid_cols, background_color)

    def _apply_transparent_background(self, preview_image):
        """Apply transparent background to preview image"""
        # Convert RGB to RGBA with transparent background
        if preview_image.mode != 'RGBA':
            # Convert to RGBA
            rgba_image = Image.new('RGBA', preview_image.size, (255, 255, 255, 0))
            # For transparent background, we need to identify the background areas
            # Since the generator uses white background, we'll make white areas transparent
            preview_rgba = preview_image.convert('RGBA')

            # Create a mask where white pixels become transparent
            pixels = preview_rgba.load()
            for y in range(preview_rgba.height):
                for x in range(preview_rgba.width):
                    r, g, b, a = pixels[x, y]
                    # If pixel is close to white (background), make it transparent
                    if r > 250 and g > 250 and b > 250:
                        pixels[x, y] = (255, 255, 255, 0)  # Transparent
                    else:
                        pixels[x, y] = (r, g, b, 255)  # Keep original color

            return preview_rgba
        else:
            return preview_image

    def _apply_checkerboard_to_preview(self, preview_image):
        """Apply checkerboard pattern to preview image background"""
        # Create a checkerboard pattern background
        width, height = preview_image.size
        checkerboard = Image.new('RGB', (width, height), (255, 255, 255))

        # Create checkerboard pattern with better contrast
        checker_size = 16  # Size of each checker square
        light_color = (240, 240, 240)  # Light gray
        dark_color = (200, 200, 200)   # Darker gray

        for y in range(0, height, checker_size):
            for x in range(0, width, checker_size):
                # Determine if this square should be light or dark
                is_dark = ((x // checker_size) + (y // checker_size)) % 2 == 1
                color = dark_color if is_dark else light_color

                # Draw the checker square more efficiently
                x1, y1 = x, y
                x2, y2 = min(x + checker_size, width), min(y + checker_size, height)

                # Fill the rectangle
                for py in range(y1, y2):
                    for px in range(x1, x2):
                        checkerboard.putpixel((px, py), color)

        # Always composite the preview over the checkerboard
        # Convert preview to RGBA if needed for proper compositing
        if preview_image.mode != 'RGBA':
            preview_rgba = preview_image.convert('RGBA')
        else:
            preview_rgba = preview_image

        # Create a mask to identify background areas (white pixels)
        mask = Image.new('L', preview_image.size, 0)
        pixels = preview_image.load()
        mask_pixels = mask.load()

        for y in range(preview_image.height):
            for x in range(preview_image.width):
                if preview_image.mode == 'RGB':
                    r, g, b = pixels[x, y]
                    # If pixel is close to white (background), make it transparent in mask
                    if r > 250 and g > 250 and b > 250:
                        mask_pixels[x, y] = 0  # Transparent
                    else:
                        mask_pixels[x, y] = 255  # Opaque
                else:  # RGBA
                    r, g, b, a = pixels[x, y]
                    if a < 128 or (r > 250 and g > 250 and b > 250):
                        mask_pixels[x, y] = 0  # Transparent
                    else:
                        mask_pixels[x, y] = 255  # Opaque

        # Composite preview over checkerboard using the mask
        result = checkerboard.copy()
        result.paste(preview_image, (0, 0), mask)

        return result

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
