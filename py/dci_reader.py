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
                                'file_size': file_info['size']
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
        """Parse layer filename to extract metadata"""
        # Expected format: priority.padding.palette.hue.saturation.brightness.red.green.blue.alpha.format
        parts = filename.split('.')

        if len(parts) >= 2:
            format_ext = parts[-1]

            layer_info = {'format': format_ext}

            if len(parts) >= 11:  # Full layer info
                try:
                    layer_info.update({
                        'priority': int(parts[0]) if parts[0].isdigit() else 1,
                        'padding': float(parts[1]) if parts[1].replace('.', '').isdigit() else 0.0,
                        'palette': int(parts[2]) if parts[2].isdigit() else 0,
                        'hue': float(parts[3]) if parts[3].replace('.', '').isdigit() else 0.0,
                        'saturation': float(parts[4]) if parts[4].replace('.', '').isdigit() else 0.0,
                        'brightness': float(parts[5]) if parts[5].replace('.', '').isdigit() else 0.0,
                        'red': float(parts[6]) if parts[6].replace('.', '').isdigit() else 0.0,
                        'green': float(parts[7]) if parts[7].replace('.', '').isdigit() else 0.0,
                        'blue': float(parts[8]) if parts[8].replace('.', '').isdigit() else 0.0,
                        'alpha': float(parts[9]) if parts[9].replace('.', '').isdigit() else 0.0,
                    })
                except (ValueError, IndexError):
                    pass

            return layer_info

        return {'format': 'unknown'}


class DCIPreviewGenerator:
    """Generate preview images with metadata annotations"""

    def __init__(self, background_color=(240, 240, 240)):
        self.font_size = 12
        self.margin = 10
        self.label_height = 80
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
        max_size = max(img['image'].size[0] for img in sorted_images)
        cell_width = max_size + self.margin * 2
        cell_height = max_size + self.label_height + self.margin * 2

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

            self._draw_image_cell(canvas, img_info, x, y, max_size)

        return canvas

    def _draw_image_cell(self, canvas: Image.Image, img_info: Dict, x: int, y: int, cell_size: int):
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

        # Draw metadata labels
        draw = ImageDraw.Draw(canvas)

        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size)
            except:
                font = ImageFont.load_default()

        # Create metadata text
        metadata_lines = [
            f"Size: {img_info['size']}px",
            f"State: {img_info['state']}",
            f"Tone: {img_info['tone']}",
            f"Scale: {img_info['scale']:g}x",
            f"Format: {img_info['format']}",
            f"File: {img_info['file_size']}B"
        ]

        # Draw metadata text with contrasting color
        text_y = y + cell_size + 5
        for line in metadata_lines:
            draw.text((x, text_y), line, fill=self.text_color, font=font)
            text_y += self.font_size + 2

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
