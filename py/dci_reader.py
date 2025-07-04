import struct
import os
from typing import List, Dict, Optional, Tuple
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import re


class DCIReader:
    """DCI file reader and parser"""

    MAGIC = b'DCI\x00'

    # File types
    FILE_TYPE_RESERVED = 0
    FILE_TYPE_FILE = 1
    FILE_TYPE_DIRECTORY = 2
    FILE_TYPE_LINK = 3

    def __init__(self, file_path: str = None, binary_data: bytes = None):
        self.file_path = file_path
        self.binary_data = binary_data
        self.files = []
        self.directory_structure = {}

    def read(self) -> bool:
        """Read and parse DCI file from file path or binary data"""
        try:
            if self.binary_data is not None:
                return self._read_from_binary_data()
            elif self.file_path is not None:
                return self._read_from_file()
            else:
                raise ValueError("Either file_path or binary_data must be provided")
        except Exception as e:
            print(f"Error reading DCI file: {e}")
            return False

    def _read_from_file(self) -> bool:
        """Read and parse DCI file from file path"""
        with open(self.file_path, 'rb') as f:
            return self._read_from_stream(f)

    def _read_from_binary_data(self) -> bool:
        """Read and parse DCI file from binary data"""
        stream = BytesIO(self.binary_data)
        return self._read_from_stream(stream)

    def _read_from_stream(self, stream) -> bool:
        """Read and parse DCI file from a stream"""
        # Read header
        magic = stream.read(4)
        if magic != self.MAGIC:
            raise ValueError(f"Invalid DCI file: wrong magic header {magic}")

        version = struct.unpack('<B', stream.read(1))[0]
        if version != 1:
            raise ValueError(f"Unsupported DCI version: {version}")

        # Read file count (3 bytes)
        file_count_bytes = stream.read(3) + b'\x00'
        file_count = struct.unpack('<I', file_count_bytes)[0]

        # Read files
        for i in range(file_count):
            file_info = self._read_file_entry(stream)
            self.files.append(file_info)

        # Parse directory structure
        self._parse_directory_structure()
        return True

    def _read_file_entry(self, f) -> Dict:
        """Read a single file entry from DCI"""
        # File type (1 byte)
        file_type = struct.unpack('<B', f.read(1))[0]

        # File name (63 bytes, null-terminated)
        name_bytes = f.read(63)
        name = name_bytes.rstrip(b'\x00').decode('utf-8')

        # Content size (8 bytes)
        content_size = struct.unpack('<Q', f.read(8))[0]

        # Content
        content = f.read(content_size)

        return {
            'name': name,
            'type': file_type,
            'size': content_size,
            'content': content
        }

    def _parse_directory_structure(self):
        """Parse the directory structure from files"""
        for file_info in self.files:
            if file_info['type'] == self.FILE_TYPE_DIRECTORY:
                self._parse_directory_content(file_info['name'], file_info['content'])

    def _parse_directory_content(self, dir_name: str, content: bytes):
        """Parse directory content recursively"""
        if dir_name not in self.directory_structure:
            self.directory_structure[dir_name] = {}

        content_stream = BytesIO(content)

        while content_stream.tell() < len(content):
            try:
                # Read file type
                file_type_bytes = content_stream.read(1)
                if not file_type_bytes:
                    break
                file_type = struct.unpack('<B', file_type_bytes)[0]

                # Read file name
                name_bytes = content_stream.read(63)
                if len(name_bytes) < 63:
                    break
                name = name_bytes.rstrip(b'\x00').decode('utf-8')

                # Read content size
                size_bytes = content_stream.read(8)
                if len(size_bytes) < 8:
                    break
                size = struct.unpack('<Q', size_bytes)[0]

                # Read content
                file_content = content_stream.read(size)
                if len(file_content) < size:
                    break

                if file_type == self.FILE_TYPE_DIRECTORY:
                    # Recursively parse subdirectory
                    subdir_path = f"{dir_name}/{name}"
                    self._parse_directory_content(subdir_path, file_content)
                else:
                    # Store file info
                    self.directory_structure[dir_name][name] = {
                        'type': file_type,
                        'size': size,
                        'content': file_content
                    }

            except Exception as e:
                print(f"Error parsing directory content: {e}")
                break

    def get_icon_images(self) -> List[Dict]:
        """Extract all icon images with metadata"""
        images = []

        print("DCIReader.get_icon_images: 开始提取图像...")

        for dir_path, files in self.directory_structure.items():
            # Parse directory path to extract metadata
            path_parts = dir_path.split('/')

            print(f"处理目录: {dir_path}, 包含 {len(files)} 个文件")

            if len(path_parts) >= 3:
                # Expected format: size/state.tone/scale
                size_str = path_parts[0]
                state_tone_str = path_parts[1] if len(path_parts) > 1 else ""
                scale_str = path_parts[2] if len(path_parts) > 2 else ""

                # Parse state and tone
                state, tone = self._parse_state_tone(state_tone_str)

                # Parse size and scale
                try:
                    size = int(size_str) if size_str.isdigit() else 0
                    # Support both integer and float scale values
                    try:
                        scale = float(scale_str) if scale_str else 1.0
                    except ValueError:
                        scale = 1.0
                except ValueError:
                    size = 0
                    scale = 1.0

                # Process files in this directory
                for filename, file_info in files.items():
                    if file_info['type'] == self.FILE_TYPE_FILE:
                        print(f"处理文件: {filename} (在目录 {dir_path} 中)")

                        # Parse layer filename for additional metadata
                        layer_info = self._parse_layer_filename(filename)

                        try:
                            # Load image from content
                            image = Image.open(BytesIO(file_info['content']))

                            image_info = {
                                'image': image,
                                'size': size,
                                'state': state,
                                'tone': tone,
                                'scale': scale,
                                'format': layer_info.get('format', 'unknown'),
                                'priority': layer_info.get('priority', 1),
                                'path': dir_path,
                                'filename': filename,
                                'file_size': file_info['size'],

                                # Layer information
                                'layer_priority': layer_info.get('priority', 1),
                                'layer_padding': layer_info.get('padding', 0.0),
                                'palette_type': layer_info.get('palette_name', 'none'),
                                'palette_value': layer_info.get('palette', -1),
                                'hue_adjustment': layer_info.get('hue', 0),
                                'saturation_adjustment': layer_info.get('saturation', 0),
                                'brightness_adjustment': layer_info.get('brightness', 0),
                                'red_adjustment': layer_info.get('red', 0),
                                'green_adjustment': layer_info.get('green', 0),
                                'blue_adjustment': layer_info.get('blue', 0),
                                'alpha_adjustment': layer_info.get('alpha', 0),
                            }

                            # 打印完整的图像信息以进行调试
                            print(f"添加图像: 路径={image_info['path']}, 文件名={image_info['filename']}")

                            images.append(image_info)

                        except Exception as e:
                            print(f"Error loading image {filename}: {e}")

        print(f"DCIReader.get_icon_images: 共提取 {len(images)} 个图像")
        return images

    def _parse_state_tone(self, state_tone_str: str) -> Tuple[str, str]:
        """Parse state.tone string"""
        if '.' in state_tone_str:
            parts = state_tone_str.split('.')
            state = parts[0] if parts[0] else 'unknown'
            tone = parts[1] if len(parts) > 1 and parts[1] else 'unknown'
        else:
            state = state_tone_str if state_tone_str else 'unknown'
            tone = 'unknown'

        return state, tone

    def _parse_layer_filename(self, filename: str) -> Dict:
        """Parse layer filename to extract metadata according to DCI specification

        Based on official implementation from dtkgui/ddciicon.cpp
        Uses step-by-step parsing: Priority -> Format/Alpha8 -> Padding -> Palette

        Supports both full format and simplified format:
        - Full: priority.padding_with_p.palette.hue_saturation_brightness_red_green_blue_alpha.format[.alpha8]
        - Simple: priority.format (e.g., 1.webp)
        """
        parts = filename.split('.')

        if len(parts) < 2:
            return {'format': 'unknown', 'is_alpha8': False}

        # Initialize layer info with defaults
        layer_info = {
            'priority': 1,
            'padding': 0,
            'palette': -1,  # NoPalette
            'hue': 0,
            'saturation': 0,
            'brightness': 0,
            'red': 0,
            'green': 0,
            'blue': 0,
            'alpha': 0,
            'format': 'unknown',
            'is_alpha8': False
        }

        # Step 1: Priority Step - always process first part
        try:
            layer_info['priority'] = int(parts[0])
            remaining_parts = parts[1:]
        except (ValueError, IndexError):
            return layer_info  # Invalid priority

        if not remaining_parts:
            return layer_info

        # Step 2: Format and Alpha8 Step - always process last part(s)
        is_alpha8 = remaining_parts[-1].lower() == 'alpha8'
        if is_alpha8:
            if len(remaining_parts) >= 2:
                layer_info['format'] = remaining_parts[-2]  # Just the format, not with .alpha8
                layer_info['is_alpha8'] = True
                # Remove both format and alpha8 from remaining parts
                remaining_parts = remaining_parts[:-2]
            else:
                return layer_info  # Invalid alpha8 format
        else:
            layer_info['format'] = remaining_parts[-1]
            # Remove format from remaining parts
            remaining_parts = remaining_parts[:-1]

        if not remaining_parts:
            return layer_info  # Only priority and format, return with defaults

        # Step 3: Padding Step - find part ending with 'p'
        padding_part = None
        for i, part in enumerate(remaining_parts):
            if part.endswith('p'):
                try:
                    layer_info['padding'] = int(part[:-1])  # Remove 'p' suffix
                    padding_part = i
                    break
                except ValueError:
                    continue

        # Remove padding part if found
        if padding_part is not None:
            remaining_parts.pop(padding_part)

        if not remaining_parts:
            return layer_info  # No palette info, return with defaults

                # Step 4: Palette Step - process remaining parts
        # Handle both formats:
        # 1. Single part with palette and color adjustments: "3_0_0_-10_0_0_0_0"
        # 2. Separate parts: "3" and "0_0_-10_0_0_0_0" (our format)

        if len(remaining_parts) == 1:
            # Single part format (official format)
            palette_part = remaining_parts[0]
        elif len(remaining_parts) == 2:
            # Two parts format (our format): palette and color_adjustments
            palette_part = f"{remaining_parts[0]}_{remaining_parts[1]}"
        else:
            # Fallback to first part only
            palette_part = remaining_parts[0] if remaining_parts else ""

        # Check if it contains color adjustments (underscore-separated)
        if '_' in palette_part:
            color_parts = palette_part.split('_')
            if len(color_parts) == 8:  # role_hue_saturation_lightness_red_green_blue_alpha
                try:
                    layer_info['palette'] = int(color_parts[0])
                    layer_info['hue'] = int(color_parts[1])
                    layer_info['saturation'] = int(color_parts[2])
                    layer_info['brightness'] = int(color_parts[3])  # lightness in original
                    layer_info['red'] = int(color_parts[4])
                    layer_info['green'] = int(color_parts[5])
                    layer_info['blue'] = int(color_parts[6])
                    layer_info['alpha'] = int(color_parts[7])
                except ValueError:
                    # If parsing fails, treat as simple palette
                    try:
                        layer_info['palette'] = int(palette_part.split('_')[0])
                    except ValueError:
                        pass
            else:
                # Invalid color adjustment format, treat as simple palette
                try:
                    layer_info['palette'] = int(palette_part.split('_')[0])
                except ValueError:
                    pass
        else:
            # Simple palette without color adjustments
            try:
                layer_info['palette'] = int(palette_part)
            except ValueError:
                pass

        # Validate palette range
        if layer_info['palette'] < -1 or layer_info['palette'] > 3:
            layer_info['palette'] = -1  # Reset to NoPalette if invalid

        # Add palette name for convenience
        palette_names = {
            -1: "none",
            0: "foreground",
            1: "background",
            2: "highlight_foreground",
            3: "highlight"
        }
        layer_info['palette_name'] = palette_names.get(layer_info['palette'], "unknown")

        return layer_info


class DCIPreviewGenerator:
    """Generate preview images with metadata annotations"""

    def __init__(self, background_color=(240, 240, 240), font_size=12):
        self.font_size = font_size
        self.margin = 10
        # 动态计算label_height，根据字体大小和文本行数
        # 5行文本 + 行间距，确保有足够空间显示所有文本（移除了tone和format字段）
        self.label_height = max(100, (self.font_size + 2) * 5 + 20)  # 5行文本 + 额外空间
        self.background_color = background_color
        self.text_color = self._get_contrasting_text_color(background_color)

    def _get_contrasting_text_color(self, bg_color):
        """Calculate contrasting text color based on background color brightness"""
        # Calculate relative luminance using the formula for sRGB
        r, g, b = bg_color

        # Convert to linear RGB
        def to_linear(c):
            c = c / 255.0
            if c <= 0.03928:
                return c / 12.92
            else:
                return pow((c + 0.055) / 1.055, 2.4)

        r_linear = to_linear(r)
        g_linear = to_linear(g)
        b_linear = to_linear(b)

        # Calculate relative luminance
        luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

        # Return black for light backgrounds, white for dark backgrounds
        if luminance > 0.5:
            return (0, 0, 0)  # Black text for light background
        else:
            return (255, 255, 255)  # White text for dark background

    def create_preview_grid(self, images: List[Dict], grid_cols: int = 4, background_color=None) -> Image.Image:
        """Create a grid preview of all images with metadata"""
        if not images:
            return self._create_empty_preview(background_color)

        # Update background color if provided
        if background_color is not None:
            self.background_color = background_color
            self.text_color = self._get_contrasting_text_color(background_color)

        # Sort images by size, state, tone, scale
        sorted_images = sorted(images, key=lambda x: (
            x['size'], x['state'], x['tone'], x['scale']
        ))

        # Calculate grid dimensions
        grid_rows = (len(sorted_images) + grid_cols - 1) // grid_cols

        # Find maximum image size for consistent cell sizing
        max_image_size = max(img['image'].size[0] for img in sorted_images)

        # Calculate maximum text width needed
        max_text_width = self._calculate_max_text_width(sorted_images)

        # Cell width should accommodate both image and text
        cell_width = max(max_image_size + self.margin * 2, max_text_width + self.margin * 2)
        cell_height = max_image_size + self.label_height + self.margin * 2

        # Create preview canvas with specified background color
        canvas_width = cell_width * grid_cols
        canvas_height = cell_height * grid_rows
        canvas = Image.new('RGB', (canvas_width, canvas_height), self.background_color)

        # Draw images and labels
        for i, img_info in enumerate(sorted_images):
            row = i // grid_cols
            col = i % grid_cols

            x = col * cell_width + self.margin
            y = row * cell_height + self.margin

            self._draw_image_cell(canvas, img_info, x, y, max_image_size, cell_width - self.margin * 2)

        return canvas

    def _calculate_max_text_width(self, images: List[Dict]) -> int:
        """Calculate the maximum text width needed for metadata display"""
        # Try to load a font for measurement
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size)
            except:
                font = ImageFont.load_default()

        max_width = 0

        # Create a temporary image for text measurement
        temp_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(temp_img)

        for img_info in images:
            # Create metadata text lines
            file_path = f"{img_info['path']}/{img_info['filename']}"
            metadata_lines = [
                f"Path: {file_path}",
                f"Size: {img_info['size']}px",
                f"State: {img_info['state']}",
                f"Scale: {img_info['scale']:g}x",
                f"File: {img_info['file_size']}B"
            ]

            # Find the maximum width among all lines
            for line in metadata_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                max_width = max(max_width, line_width)

        # Add some padding for safety
        return max_width + 20

    def _draw_image_cell(self, canvas: Image.Image, img_info: Dict, x: int, y: int, cell_size: int, text_width: int):
        """Draw a single image cell with metadata"""
        image = img_info['image']

        # Resize image to fit cell while maintaining aspect ratio
        image_size = min(cell_size, max(image.size))
        if image.size[0] != image_size or image.size[1] != image_size:
            image = image.resize((image_size, image_size), Image.Resampling.LANCZOS)

        # Position image at left side of cell instead of center
        img_x = x  # Left align instead of centering
        img_y = y + (cell_size - image.size[1]) // 2  # Still center vertically

        # Paste image
        if image.mode == 'RGBA':
            canvas.paste(image, (img_x, img_y), image)
        else:
            canvas.paste(image, (img_x, img_y))

        # Draw border around the icon to show its actual range
        draw = ImageDraw.Draw(canvas)

        # Calculate border coordinates (around the actual image)
        border_x1 = img_x - 1
        border_y1 = img_y - 1
        border_x2 = img_x + image.size[0]
        border_y2 = img_y + image.size[1]

        # Choose border color based on background brightness
        border_color = self._get_border_color()

        # Draw a thin border around the icon
        draw.rectangle([border_x1, border_y1, border_x2, border_y2],
                      outline=border_color, width=1)

        # Draw padding indicator if padding exists
        padding = img_info.get('layer_padding', 0)
        if padding > 0:
            # Calculate padding area in pixels
            # Padding is typically a percentage or ratio, convert to pixels
            padding_pixels = int(padding * image.size[0] / 100) if padding < 1 else int(padding)

            # Calculate inner content area (after removing padding)
            inner_x1 = img_x + padding_pixels
            inner_y1 = img_y + padding_pixels
            inner_x2 = img_x + image.size[0] - padding_pixels
            inner_y2 = img_y + image.size[1] - padding_pixels

            # Only draw if the inner area is valid
            if inner_x2 > inner_x1 and inner_y2 > inner_y1:
                # Draw dashed border around the content area (excluding padding)
                self._draw_dashed_rectangle(draw, inner_x1, inner_y1, inner_x2, inner_y2, border_color)

        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size)
            except:
                font = ImageFont.load_default()

        # Create metadata text with file path as first line
        file_path = f"{img_info['path']}/{img_info['filename']}"
        metadata_lines = [
            f"Path: {file_path}",
            f"Size: {img_info['size']}px",
            f"State: {img_info['state']}",
            f"Scale: {img_info['scale']:g}x",
            f"File: {img_info['file_size']}B"
        ]

        # Add padding info if it exists
        if padding > 0:
            metadata_lines.append(f"Padding: {padding}")

        # Process text lines with wrapping if needed
        wrapped_lines = []
        for line in metadata_lines:
            wrapped_lines.extend(self._wrap_text(line, text_width, font, draw))

        # 计算实际需要的文本高度
        line_height = self.font_size + 2
        total_text_height = len(wrapped_lines) * line_height

        # 确保文本区域有足够的空间
        text_start_y = y + cell_size + 5
        available_height = self.label_height - 10  # 留一些边距

        # 如果文本太多，调整行高或截断文本
        if total_text_height > available_height:
            # 调整行高以适应可用空间
            line_height = max(self.font_size, available_height // len(wrapped_lines))

        # Draw metadata text with contrasting color
        text_y = text_start_y
        for i, line in enumerate(wrapped_lines):
            # 确保不超出可用区域
            if text_y + line_height <= text_start_y + available_height:
                draw.text((x, text_y), line, fill=self.text_color, font=font)
                text_y += line_height
            else:
                # 如果空间不够，显示省略号
                if i < len(wrapped_lines) - 1:
                    draw.text((x, text_y), "...", fill=self.text_color, font=font)
                break

    def _draw_dashed_rectangle(self, draw, x1, y1, x2, y2, color, dash_length=4, gap_length=2):
        """Draw a dashed rectangle border"""
        # Draw top edge
        self._draw_dashed_line(draw, x1, y1, x2, y1, color, dash_length, gap_length)
        # Draw right edge
        self._draw_dashed_line(draw, x2, y1, x2, y2, color, dash_length, gap_length)
        # Draw bottom edge
        self._draw_dashed_line(draw, x2, y2, x1, y2, color, dash_length, gap_length)
        # Draw left edge
        self._draw_dashed_line(draw, x1, y2, x1, y1, color, dash_length, gap_length)

    def _draw_dashed_line(self, draw, x1, y1, x2, y2, color, dash_length=4, gap_length=2):
        """Draw a dashed line between two points"""
        # Calculate line length and direction
        dx = x2 - x1
        dy = y2 - y1
        line_length = (dx * dx + dy * dy) ** 0.5

        if line_length == 0:
            return

        # Normalize direction vector
        dx_norm = dx / line_length
        dy_norm = dy / line_length

        # Draw dashes
        current_pos = 0
        while current_pos < line_length:
            # Calculate dash start and end positions
            dash_start = current_pos
            dash_end = min(current_pos + dash_length, line_length)

            # Calculate actual coordinates
            start_x = x1 + dx_norm * dash_start
            start_y = y1 + dy_norm * dash_start
            end_x = x1 + dx_norm * dash_end
            end_y = y1 + dy_norm * dash_end

            # Draw the dash
            draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=1)

            # Move to next dash position
            current_pos += dash_length + gap_length

    def _get_border_color(self):
        """Get border color that follows text color for better visual consistency"""
        # Use the same color as text for border, but with reduced opacity effect
        # This creates a cohesive visual appearance where border and text match

        # Get the current text color
        text_r, text_g, text_b = self.text_color

        # Create a slightly lighter/darker version of text color for border
        # This maintains color consistency while ensuring the border is visible
        if text_r + text_g + text_b > 384:  # Light text (white-ish)
            # For light text, make border slightly darker
            border_r = max(0, text_r - 64)
            border_g = max(0, text_g - 64)
            border_b = max(0, text_b - 64)
        else:  # Dark text (black-ish)
            # For dark text, make border slightly lighter
            border_r = min(255, text_r + 64)
            border_g = min(255, text_g + 64)
            border_b = min(255, text_b + 64)

        return (border_r, border_g, border_b)

    def _wrap_text(self, text: str, max_width: int, font, draw) -> List[str]:
        """Wrap text to fit within the specified width"""
        # Check if text fits in one line
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            return [text]

        # Text is too long, need to wrap
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]

            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Single word is too long, truncate it
                    truncated_word = word
                    while len(truncated_word) > 3:
                        test_word = truncated_word[:-3] + "..."
                        bbox = draw.textbbox((0, 0), test_word, font=font)
                        test_width = bbox[2] - bbox[0]
                        if test_width <= max_width:
                            lines.append(test_word)
                            break
                        truncated_word = truncated_word[:-1]
                    else:
                        lines.append("...")
                    current_line = ""

        if current_line:
            lines.append(current_line)

        return lines

    def _create_empty_preview(self, background_color=None) -> Image.Image:
        """Create an empty preview image"""
        bg_color = background_color if background_color is not None else self.background_color
        text_color = self._get_contrasting_text_color(bg_color)

        canvas = Image.new('RGB', (400, 200), bg_color)
        draw = ImageDraw.Draw(canvas)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()

        text = "No DCI images found"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (canvas.width - text_width) // 2
        y = (canvas.height - text_height) // 2

        draw.text((x, y), text, fill=text_color, font=font)

        return canvas

    def create_metadata_summary(self, images: List[Dict]) -> Dict:
        """Create a summary of metadata from all images"""
        if not images:
            return {}

        summary = {
            'total_images': len(images),
            'sizes': set(),
            'states': set(),
            'tones': set(),
            'scales': set(),
            'formats': set(),
            'total_file_size': 0
        }

        for img in images:
            summary['sizes'].add(img['size'])
            summary['states'].add(img['state'])
            summary['tones'].add(img['tone'])
            summary['scales'].add(img['scale'])
            summary['formats'].add(img['format'])
            summary['total_file_size'] += img['file_size']

        # Convert sets to sorted lists
        summary['sizes'] = sorted(list(summary['sizes']))
        summary['states'] = sorted(list(summary['states']))
        summary['tones'] = sorted(list(summary['tones']))
        summary['scales'] = sorted(list(summary['scales']))
        summary['formats'] = sorted(list(summary['formats']))

        return summary
