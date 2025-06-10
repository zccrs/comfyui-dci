import torch
import numpy as np
from PIL import Image
import os
import tempfile
import struct
from io import BytesIO

# Try relative imports first, fall back to absolute imports
try:
    from .dci_format import create_dci_icon, DCIIconBuilder, DCIFile
    from .dci_reader import DCIReader, DCIPreviewGenerator
except ImportError:
    # Fallback for when module is loaded directly
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from dci_format import create_dci_icon, DCIIconBuilder, DCIFile
    from dci_reader import DCIReader, DCIPreviewGenerator


class DCIPreviewNode:
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

    def preview_dci(self, dci_binary_data,
                   light_background_color="light_gray",
                   dark_background_color="dark_gray",
                   text_font_size=12):
        """Preview DCI file contents with in-node display, separating Light and Dark content into two columns"""

        try:
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

            # 添加调试信息，输出每个图像的路径
            print("调试路径信息:")
            for i, img in enumerate(images):
                print(f"图像 #{i}: 路径={img.get('path', 'None')} 文件名={img.get('filename', 'None')}")

            # 根据色调将图像分成Light和Dark两组
            light_images = [img for img in images if img['tone'].lower() == 'light']
            dark_images = [img for img in images if img['tone'].lower() == 'dark']
            other_images = [img for img in images if img['tone'].lower() not in ('light', 'dark')]

            # 确定背景颜色
            light_bg_color = self._get_background_color(light_background_color)
            dark_bg_color = self._get_background_color(dark_background_color)

            # 生成预览图像
            generator = DCIPreviewGenerator()

            # 为Light和Dark分别生成单列预览，处理特殊背景类型
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
            preview_base64 = self._pil_to_base64(preview_image)

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
            print(f"Error previewing DCI file: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"ui": {"text": [f"Error: {str(e)}"]}}

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

    def _get_background_color(self, color_name):
        """Get RGB color tuple based on color name, or special handling for transparent/checkerboard"""
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
        # In the future, we could enhance this to detect transparent areas and apply checkerboard
        return preview_image

    def _create_checkerboard_background(self, size, square_size=16):
        """Create a checkerboard pattern background"""
        width, height = size
        background = Image.new('RGB', size, (255, 255, 255))

        # Create checkerboard pattern
        for y in range(0, height, square_size):
            for x in range(0, width, square_size):
                # Determine if this square should be gray
                if (x // square_size + y // square_size) % 2 == 1:
                    # Draw gray square
                    for py in range(y, min(y + square_size, height)):
                        for px in range(x, min(x + square_size, width)):
                            background.putpixel((px, py), (200, 200, 200))

        return background

    def _pil_to_base64(self, pil_image):
        """Convert PIL image to base64 string for UI display"""
        import base64
        import hashlib
        import time

        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Save to bytes buffer
        buffer = BytesIO()
        pil_image.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()

        # Generate unique filename
        timestamp = str(int(time.time()))
        hash_obj = hashlib.md5(img_bytes)
        filename = f"dci_preview_{timestamp}_{hash_obj.hexdigest()[:8]}.png"

        # Save to temp directory for ComfyUI
        try:
            import folder_paths
            temp_dir = folder_paths.get_temp_directory()
        except:
            temp_dir = tempfile.gettempdir()

        temp_path = os.path.join(temp_dir, filename)
        with open(temp_path, 'wb') as f:
            f.write(img_bytes)

        # Return in format expected by ComfyUI
        return {
            "filename": filename,
            "subfolder": "",
            "type": "temp"
        }

    def _format_detailed_summary(self, images, source_name, text_font_size=12):
        """Format detailed metadata summary as text with comprehensive information and clear Light/Dark separation"""
        if not images:
            return "No images available"

        # 添加调试信息，再次输出所有路径
        print("_format_detailed_summary 方法中的路径信息:")
        for i, img in enumerate(images):
            path = img.get('path', 'None')
            filename = img.get('filename', 'None')
            print(f"图像 #{i}: 路径={path}, 文件名={filename}")

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
        paths = sorted(set(img['path'] for img in images))

        # Adjust spacing based on font size
        spacing = "" if text_font_size <= 10 else "\n"
        indentation = "   " if text_font_size <= 14 else " "
        separator = "=" * max(20, 50 - text_font_size)

        # Build detailed summary with font size adaptations
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

        # 分别显示Light和Dark的路径列表
        if light_images:
            lines.extend([
                "📂 Light 文件路径列表:",
            ])
            # Sort light images for consistent display
            sorted_light_images = sorted(light_images, key=lambda x: (x['size'], x['state'], x['scale']))
            for img in sorted_light_images:
                # 确保路径和文件名都存在
                path = img.get('path', 'unknown_path')
                filename = img.get('filename', 'unknown_file')
                print(f"Light 图像路径信息: 路径={path}, 文件名={filename}")
                full_path = f"/{path}/{filename}"
                lines.append(f"{indentation}{full_path}")
            lines.append("")

        if dark_images:
            lines.extend([
                "📂 Dark 文件路径列表:",
            ])
            # Sort dark images for consistent display
            sorted_dark_images = sorted(dark_images, key=lambda x: (x['size'], x['state'], x['scale']))
            for img in sorted_dark_images:
                # 确保路径和文件名都存在
                path = img.get('path', 'unknown_path')
                filename = img.get('filename', 'unknown_file')
                print(f"Dark 图像路径信息: 路径={path}, 文件名={filename}")
                full_path = f"/{path}/{filename}"
                lines.append(f"{indentation}{full_path}")
            lines.append("")

        if other_images:
            lines.extend([
                "📂 其他色调文件路径列表:",
            ])
            # Sort other images for consistent display
            sorted_other_images = sorted(other_images, key=lambda x: (x['size'], x['state'], x['scale']))
            for img in sorted_other_images:
                # 确保路径和文件名都存在
                path = img.get('path', 'unknown_path')
                filename = img.get('filename', 'unknown_file')
                print(f"其他 图像路径信息: 路径={path}, 文件名={filename}")
                full_path = f"/{path}/{filename}"
                lines.append(f"{indentation}{full_path}")
            lines.append("")

        lines.extend([
            "📋 详细图像信息:",
            separator
        ])

        # Add detailed info for each image, grouped by tone
        # First Light images
        if light_images:
            lines.append("")
            lines.append("🌞 Light 主题图像:")
            lines.append("")
            self._add_detailed_image_info(lines, light_images, indentation, text_font_size)

        # Then Dark images
        if dark_images:
            lines.append("")
            lines.append("🌙 Dark 主题图像:")
            lines.append("")
            self._add_detailed_image_info(lines, dark_images, indentation, text_font_size)

        # Finally other images if any
        if other_images:
            lines.append("")
            lines.append("⚪ 其他主题图像:")
            lines.append("")
            self._add_detailed_image_info(lines, other_images, indentation, text_font_size)

        return "\n".join(lines)

    def _add_detailed_image_info(self, lines, images, indentation, text_font_size):
        """Helper method to add detailed image information to the summary text"""
        # Sort images for consistent display
        sorted_images = sorted(images, key=lambda x: (x['size'], x['state'], x['scale']))

        # Add detailed info for each image
        for i, img in enumerate(sorted_images, 1):
            # Construct full DCI path
            path = img.get('path', 'unknown_path')
            filename = img.get('filename', 'unknown_file')
            full_path = f"/{path}/{filename}"
            print(f"详细信息中的图像 #{i} 路径: {full_path}")

            # Adjust detail level based on font size
            if text_font_size >= 16:
                # More compact format for larger fonts
                image_info = [
                    f"图像 #{i}: {img['size']}px {img['state']}.{img['tone']} {img['scale']:g}x {img['format']}",
                    f"{indentation}路径: {full_path}",
                    f"{indentation}大小: {img['file_size']:,}字节 ({img['image'].size[0]}×{img['image'].size[1]}px)",
                    ""
                ]
            else:
                # Detailed format for smaller fonts
                image_info = [
                    f"图像 #{i}:",
                    f"{indentation}📁 完整路径: {full_path}",
                    f"{indentation}📏 图标尺寸: {img['size']}px",
                    f"{indentation}🎭 状态: {img['state']}",
                    f"{indentation}🎨 色调: {img['tone']}",
                    f"{indentation}🔍 缩放因子: {img['scale']:g}x",
                    f"{indentation}🗂️  图像格式: {img['format']}",
                    f"{indentation}📊 文件大小: {img['file_size']:,} 字节",
                    f"{indentation}🖼️  实际尺寸: {img['image'].size[0]}×{img['image'].size[1]}px",
                    f"{indentation}🎯 优先级: {img.get('priority', 1)}",
                    ""
                ]
            lines.extend(image_info)


class DCIImage:
    """ComfyUI node for creating DCI image metadata and data"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "icon_size": ("INT", {"default": 256, "min": 16, "max": 1024, "step": 1}),
                "icon_state": (["normal", "disabled", "hover", "pressed"], {"default": "normal"}),
                "tone_type": (["light", "dark"], {"default": "dark"}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "image_format": (["webp", "png", "jpg"], {"default": "webp"}),
            },
            "optional": {
                "background_color": (["transparent", "white", "black", "custom"], {"default": "transparent"}),
                "custom_bg_r": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),
                "custom_bg_g": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),
                "custom_bg_b": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1}),
            }
        }

    RETURN_TYPES = ("DCI_IMAGE_DATA",)
    RETURN_NAMES = ("dci_image_data",)
    FUNCTION = "create_dci_image"
    CATEGORY = "DCI/Export"

    def create_dci_image(self, image, icon_size, icon_state, tone_type, scale, image_format, background_color="transparent", custom_bg_r=255, custom_bg_g=255, custom_bg_b=255):
        """Create DCI image metadata and data"""

        try:
            # Convert ComfyUI image tensor to PIL Image
            if len(image.shape) == 4:
                img_array = image[0].cpu().numpy()
            else:
                img_array = image.cpu().numpy()

            # Convert from 0-1 range to 0-255 range
            img_array = (img_array * 255).astype(np.uint8)

            # Convert to PIL Image
            if img_array.shape[2] == 3:
                pil_image = Image.fromarray(img_array, 'RGB')
            elif img_array.shape[2] == 4:
                pil_image = Image.fromarray(img_array, 'RGBA')
            else:
                pil_image = Image.fromarray(img_array[:, :, 0], 'L').convert('RGB')

            # Handle background color for images with transparency
            if background_color != "transparent" and pil_image.mode in ('RGBA', 'LA'):
                # Determine background color
                if background_color == "white":
                    bg_color = (255, 255, 255)
                elif background_color == "black":
                    bg_color = (0, 0, 0)
                elif background_color == "custom":
                    bg_color = (custom_bg_r, custom_bg_g, custom_bg_b)
                else:
                    bg_color = (255, 255, 255)  # Default to white

                # Create background and composite
                background = Image.new('RGB', pil_image.size, bg_color)
                if pil_image.mode == 'RGBA':
                    background.paste(pil_image, mask=pil_image.split()[-1])
                else:
                    background.paste(pil_image)
                pil_image = background

            # Calculate actual size with scale
            actual_size = int(icon_size * scale)

            # Resize image to target size
            resized_image = pil_image.resize((actual_size, actual_size), Image.Resampling.LANCZOS)

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

            # Create DCI path: size/state.tone/scale/1.0.0.0.0.0.0.0.0.0.format
            # Format scale to remove unnecessary decimal places
            scale_str = f"{scale:g}"  # This removes trailing zeros
            dci_path = f"{icon_size}/{icon_state}.{tone_type}/{scale_str}/1.0.0.0.0.0.0.0.0.0.{image_format}"

            # Create metadata dictionary
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
                'pil_image': resized_image  # Store PIL image for debug purposes
            }

            print(f"Created DCI image: {dci_path} ({len(img_content)} bytes), background: {background_color}")
            return (dci_image_data,)

        except Exception as e:
            print(f"Error creating DCI image: {str(e)}")
            import traceback
            traceback.print_exc()
            return ({},)


class DCIImageDebug:
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

    def debug_dci_image(self, dci_image_data, show_metadata=True, show_binary_info=True, preview_background="checkerboard"):
        """Debug and preview DCI image data"""

        try:
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
            preview_image = self._create_preview_with_background(pil_image, preview_background)

            # Convert to ComfyUI format
            preview_base64 = self._pil_to_base64(preview_image)

            # Generate debug information
            debug_text = self._format_debug_info(dci_image_data, show_metadata, show_binary_info)

            # Create UI output
            ui_output = {
                "ui": {
                    "images": [preview_base64],
                    "text": [debug_text]
                }
            }

            print(f"DCI Image Debug: {dci_image_data.get('path', 'unknown')} - {pil_image.size} - {pil_image.mode}")
            return ui_output

        except Exception as e:
            print(f"Error debugging DCI image: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"ui": {"text": [f"Error: {str(e)}"]}}

    def _create_preview_with_background(self, pil_image, background_type):
        """Create preview image with specified background"""
        if background_type == "transparent" or pil_image.mode != 'RGBA':
            return pil_image

        # Create background
        if background_type == "white":
            background = Image.new('RGB', pil_image.size, (255, 255, 255))
        elif background_type == "black":
            background = Image.new('RGB', pil_image.size, (0, 0, 0))
        elif background_type == "checkerboard":
            background = self._create_checkerboard_background(pil_image.size)
        else:
            return pil_image

        # Composite image onto background
        if pil_image.mode == 'RGBA':
            background.paste(pil_image, mask=pil_image.split()[-1])
        else:
            background.paste(pil_image)

        return background

    def _create_checkerboard_background(self, size, square_size=16):
        """Create a checkerboard pattern background"""
        width, height = size
        background = Image.new('RGB', size, (255, 255, 255))

        # Create checkerboard pattern
        for y in range(0, height, square_size):
            for x in range(0, width, square_size):
                # Determine if this square should be gray
                if (x // square_size + y // square_size) % 2 == 1:
                    # Draw gray square
                    for py in range(y, min(y + square_size, height)):
                        for px in range(x, min(x + square_size, width)):
                            background.putpixel((px, py), (200, 200, 200))

        return background

    def _pil_to_base64(self, pil_image):
        """Convert PIL image to base64 string for UI display"""
        import base64
        import hashlib
        import time

        # Convert to RGB if necessary
        if pil_image.mode not in ('RGB', 'RGBA'):
            pil_image = pil_image.convert('RGB')

        # Save to bytes buffer
        buffer = BytesIO()
        pil_image.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()

        # Generate unique filename
        timestamp = str(int(time.time()))
        hash_obj = hashlib.md5(img_bytes)
        filename = f"dci_debug_{timestamp}_{hash_obj.hexdigest()[:8]}.png"

        # Save to temp directory for ComfyUI
        try:
            import folder_paths
            temp_dir = folder_paths.get_temp_directory()
        except:
            temp_dir = tempfile.gettempdir()

        temp_path = os.path.join(temp_dir, filename)
        with open(temp_path, 'wb') as f:
            f.write(img_bytes)

        # Return in format expected by ComfyUI
        return {
            "filename": filename,
            "subfolder": "",
            "type": "temp"
        }

    def _format_debug_info(self, dci_image_data, show_metadata, show_binary_info):
        """Format debug information as text"""
        lines = [
            "🔍 DCI Image Debug Information",
            "=" * 40,
            ""
        ]

        if show_metadata:
            lines.extend([
                "📋 基本信息:",
                f"  📁 DCI路径: {dci_image_data.get('path', 'N/A')}",
                f"  📏 图标尺寸: {dci_image_data.get('size', 'N/A')}px",
                f"  🎭 状态: {dci_image_data.get('state', 'N/A')}",
                f"  🎨 色调: {dci_image_data.get('tone', 'N/A')}",
                f"  🔍 缩放因子: {dci_image_data.get('scale', 'N/A')}x",
                f"  🗂️  图像格式: {dci_image_data.get('format', 'N/A')}",
                f"  📊 实际尺寸: {dci_image_data.get('actual_size', 'N/A')}px",
                f"  🎯 背景处理: {dci_image_data.get('background_color', 'N/A')}",
                ""
            ])

        if show_binary_info:
            content = dci_image_data.get('content', b'')
            file_size = len(content)

            lines.extend([
                "🔢 二进制数据信息:",
                f"  📊 文件大小: {file_size:,} 字节 ({file_size/1024:.2f} KB)",
                f"  🔗 数据类型: {type(content).__name__}",
                ""
            ])

            if content and len(content) > 0:
                # Show first few bytes as hex
                hex_preview = ' '.join(f'{b:02x}' for b in content[:16])
                if len(content) > 16:
                    hex_preview += "..."

                lines.extend([
                    "🔍 二进制数据预览 (前16字节):",
                    f"  {hex_preview}",
                    ""
                ])

        # PIL Image information
        pil_image = dci_image_data.get('pil_image')
        if pil_image:
            lines.extend([
                "🖼️  PIL图像信息:",
                f"  📐 尺寸: {pil_image.size[0]}×{pil_image.size[1]}px",
                f"  🎨 颜色模式: {pil_image.mode}",
                f"  📊 格式: {getattr(pil_image, 'format', 'N/A')}",
                ""
            ])

        # Add validation status
        lines.extend([
            "✅ 验证状态:",
            f"  📁 路径格式: {'✓' if dci_image_data.get('path') else '✗'}",
            f"  🔢 二进制数据: {'✓' if dci_image_data.get('content') else '✗'}",
            f"  🖼️  PIL图像: {'✓' if dci_image_data.get('pil_image') else '✗'}",
            f"  📊 元数据完整: {'✓' if all(k in dci_image_data for k in ['size', 'state', 'tone', 'scale', 'format']) else '✗'}",
        ])

        return "\n".join(lines)


class DCIFileNode:
    """ComfyUI node for combining multiple DCI images into a DCI file"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "dci_image_1": ("DCI_IMAGE_DATA",),
                "dci_image_2": ("DCI_IMAGE_DATA",),
                "dci_image_3": ("DCI_IMAGE_DATA",),
                "dci_image_4": ("DCI_IMAGE_DATA",),
                "dci_image_5": ("DCI_IMAGE_DATA",),
                "dci_image_6": ("DCI_IMAGE_DATA",),
                "dci_image_7": ("DCI_IMAGE_DATA",),
                "dci_image_8": ("DCI_IMAGE_DATA",),
                "dci_image_9": ("DCI_IMAGE_DATA",),
                "dci_image_10": ("DCI_IMAGE_DATA",),
                "dci_image_11": ("DCI_IMAGE_DATA",),
                "dci_image_12": ("DCI_IMAGE_DATA",),
            }
        }

    RETURN_TYPES = ("BINARY_DATA",)
    RETURN_NAMES = ("dci_binary_data",)
    FUNCTION = "create_dci_file"
    CATEGORY = "DCI/Export"

    def create_dci_file(self, **kwargs):
        """Combine multiple DCI images into a DCI file"""

        try:
            # Collect all DCI image data
            dci_images = []
            for i in range(1, 13):  # Support up to 12 images
                dci_image_key = f"dci_image_{i}"
                if dci_image_key in kwargs and kwargs[dci_image_key]:
                    dci_images.append(kwargs[dci_image_key])

            if not dci_images:
                print("No DCI images provided")
                return (b"",)

            # 添加调试信息：输出所有DCI图像的路径
            print("DCIFileNode: 所有输入图像的路径:")
            for i, dci_image in enumerate(dci_images):
                path = dci_image.get('path', 'None')
                print(f"  图像 #{i+1}: 路径={path}")

            # Create DCI file structure
            dci_file = DCIFile()
            directory_structure = {}

            # Process each DCI image
            for dci_image in dci_images:
                path = dci_image['path']
                content = dci_image['content']

                # Parse path: size/state.tone/scale/filename
                path_parts = path.split('/')
                if len(path_parts) != 4:
                    print(f"Invalid DCI path format: {path}")
                    continue

                size_dir, state_tone_dir, scale_dir, filename_part = path_parts

                # 添加调试信息：输出路径的各个部分
                print(f"解析路径: {path} => size_dir={size_dir}, state_tone_dir={state_tone_dir}, scale_dir={scale_dir}, filename={filename_part}")

                # Build nested directory structure
                if size_dir not in directory_structure:
                    directory_structure[size_dir] = {}
                if state_tone_dir not in directory_structure[size_dir]:
                    directory_structure[size_dir][state_tone_dir] = {}
                if scale_dir not in directory_structure[size_dir][state_tone_dir]:
                    directory_structure[size_dir][state_tone_dir][scale_dir] = {}

                directory_structure[size_dir][state_tone_dir][scale_dir][filename_part] = content

            # Convert directory structure to DCI format
            for size_dir, size_content in directory_structure.items():
                state_tone_dirs = []

                for state_tone_dir, state_tone_content in size_content.items():
                    scale_dirs = []

                    for scale_dir, scale_content in state_tone_content.items():
                        # Create files for this scale directory
                        scale_files = []
                        for filename_part, file_content in scale_content.items():
                            scale_files.append({
                                'name': filename_part,
                                'content': file_content,
                                'type': DCIFile.FILE_TYPE_FILE
                            })

                        # Create scale directory
                        scale_dir_content = self._create_directory_content(scale_files, dci_file)
                        scale_dirs.append({
                            'name': scale_dir,
                            'content': scale_dir_content,
                            'type': DCIFile.FILE_TYPE_DIRECTORY
                        })

                    # Create state.tone directory
                    state_tone_dir_content = self._create_directory_content(scale_dirs, dci_file)
                    state_tone_dirs.append({
                        'name': state_tone_dir,
                        'content': state_tone_dir_content,
                        'type': DCIFile.FILE_TYPE_DIRECTORY
                    })

                # Add size directory to DCI
                dci_file.add_directory(size_dir, state_tone_dirs)

            # Generate binary data
            binary_data = dci_file.to_binary()

            print(f"Created DCI file with {len(dci_images)} images ({len(binary_data)} bytes)")
            return (binary_data,)

        except Exception as e:
            print(f"Error creating DCI file: {str(e)}")
            import traceback
            traceback.print_exc()
            return (b"",)

    def _create_directory_content(self, files, dci_file):
        """Create directory content from file list"""
        dir_content = BytesIO()

        # 添加调试信息：输出所有文件
        print(f"_create_directory_content: 处理 {len(files)} 个文件")

        # Sort files by name
        sorted_files = sorted(files, key=lambda x: dci_file._natural_sort_key(x['name']))

        for file_info in sorted_files:
            # 添加调试信息：输出当前处理的文件
            print(f"  处理文件: 名称={file_info['name']}, 类型={file_info.get('type', DCIFile.FILE_TYPE_FILE)}")

            # File type (1 byte)
            dir_content.write(struct.pack('<B', file_info.get('type', DCIFile.FILE_TYPE_FILE)))

            # File name (63 bytes, null-terminated)
            file_name_bytes = file_info['name'].encode('utf-8')
            name_padded = file_name_bytes + b'\x00' * (63 - len(file_name_bytes))
            dir_content.write(name_padded)

            # Content size (8 bytes)
            content = file_info['content']
            dir_content.write(struct.pack('<Q', len(content)))

            # Content
            dir_content.write(content)

        return dir_content.getvalue()


class BinaryFileLoader:
    """ComfyUI node for loading binary files from file system"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "file_path": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("BINARY_DATA", "STRING")
    RETURN_NAMES = ("binary_data", "file_path")
    FUNCTION = "load_binary_file"
    CATEGORY = "DCI/Files"

    def load_binary_file(self, file_path=""):
        """Load binary file from file system"""

        try:
            if not file_path or not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return (None, "")

            # Read binary file
            with open(file_path, 'rb') as f:
                content = f.read()

            # Get file info
            filename = os.path.basename(file_path)
            file_size = len(content)

            print(f"Loaded binary file: {filename} ({file_size} bytes)")
            # Return the binary content directly, not wrapped in a dictionary
            return (content, file_path)

        except Exception as e:
            print(f"Error loading binary file: {str(e)}")
            import traceback
            traceback.print_exc()
            return (None, "")


class BinaryFileSaver:
    """ComfyUI node for saving binary data to file system"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "binary_data": ("BINARY_DATA",),
                "file_name": ("STRING", {"default": "binary_file", "multiline": False}),
            },
            "optional": {
                "output_directory": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    FUNCTION = "save_binary_file"
    CATEGORY = "DCI/Files"
    OUTPUT_NODE = True

    def save_binary_file(self, binary_data, file_name, output_directory=""):
        """Save binary data to file system"""

        try:
            # Check if binary_data is valid
            if binary_data is None:
                print("No binary data provided (None)")
                return ("",)

            if isinstance(binary_data, bytes) and len(binary_data) == 0:
                print("Empty binary data provided")
                return ("",)

            if not isinstance(binary_data, bytes):
                print(f"Invalid binary data type: {type(binary_data)}")
                return ("",)

            print(f"Processing binary data: {len(binary_data)} bytes")

            # Clean up file name (remove any path separators)
            clean_file_name = os.path.basename(file_name) if file_name else "binary_file"
            if not clean_file_name:
                clean_file_name = "binary_file"

            # Determine output directory
            if output_directory and os.path.exists(output_directory):
                output_dir = output_directory
            else:
                # Use ComfyUI output directory or temp directory
                try:
                    import folder_paths
                    output_dir = folder_paths.get_output_directory()
                    print(f"Using ComfyUI output directory: {output_dir}")
                except ImportError:
                    # ComfyUI folder_paths not available
                    output_dir = tempfile.gettempdir()
                    print(f"ComfyUI not available, using temp directory: {output_dir}")
                except Exception as e:
                    # Any other folder_paths related errors
                    output_dir = tempfile.gettempdir()
                    print(f"Error accessing ComfyUI output directory: {e}, using temp directory: {output_dir}")

            # Create full path
            full_path = os.path.join(output_dir, clean_file_name)
            print(f"Target file path: {full_path}")

            # Ensure directory exists
            dir_path = os.path.dirname(full_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
                print(f"Ensured directory exists: {dir_path}")

            # Write binary data
            with open(full_path, 'wb') as f:
                bytes_written = f.write(binary_data)
                print(f"Wrote {bytes_written} bytes to file")

            # Verify file was written correctly
            if os.path.exists(full_path):
                actual_size = os.path.getsize(full_path)
                print(f"File saved successfully: {full_path} ({actual_size} bytes)")
                return (full_path,)
            else:
                print(f"File was not created: {full_path}")
                return ("",)

        except Exception as e:
            print(f"Error saving binary file: {str(e)}")
            import traceback
            traceback.print_exc()
            return ("",)
