"""
DCI Analysis Node
专门用于分析DCI文件内部结构的节点，以文本形式输出所有元信息
"""

from .base_node import BaseNode
from ..utils.i18n import t

try:
    from ..dci_reader import DCIReader
except ImportError:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(current_dir))
    from dci_reader import DCIReader


class DCIAnalysis(BaseNode):
    """ComfyUI node for analyzing DCI file internal structure and outputting text"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dci_binary_data": ("BINARY_DATA",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = (t("analysis_text"),)
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Analysis')}"

    def _execute(self, dci_binary_data):
        """Analyze DCI file internal structure and return text output"""

        # Use binary data
        reader = DCIReader(binary_data=dci_binary_data)

        # Read DCI data
        if not reader.read():
            return (t("Failed to read DCI data"),)

        # Extract images
        images = reader.get_icon_images()
        if not images:
            return (t("No images found in DCI file"),)

        # Generate tree structure
        tree_structure = self._generate_tree_structure(images)

        return (tree_structure,)

    def _generate_tree_structure(self, images):
        """Generate tree structure representation of DCI file"""

        # Organize images by directory structure
        structure = {}

        for img in images:
            # Parse path: size/state.tone/scale (directory path)
            # Filename is stored separately in 'filename' field
            path_parts = img['path'].split('/')
            filename = img.get('filename', 'unknown.png')

            if len(path_parts) >= 3:
                size = path_parts[0]
                state_tone = path_parts[1]
                scale = path_parts[2]

                # Initialize nested structure
                if size not in structure:
                    structure[size] = {}
                if state_tone not in structure[size]:
                    structure[size][state_tone] = {}
                if scale not in structure[size][state_tone]:
                    structure[size][state_tone][scale] = []

                # Add file info with metadata
                metadata = self._parse_filename_metadata(filename)
                metadata['scale'] = f"{scale}x"  # Set scale from path
                file_info = {
                    'filename': filename,
                    'metadata': metadata
                }

                structure[size][state_tone][scale].append(file_info)

        # Generate tree text
        lines = []

        # Sort sizes numerically
        sorted_sizes = sorted(structure.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

        for i, size in enumerate(sorted_sizes):
            is_last_size = (i == len(sorted_sizes) - 1)
            size_prefix = "└── " if is_last_size else "├── "
            lines.append(f"{size_prefix}{size}")

            # Sort state.tone combinations
            sorted_states = sorted(structure[size].keys())

            for j, state_tone in enumerate(sorted_states):
                is_last_state = (j == len(sorted_states) - 1)
                state_indent = "    " if is_last_size else "│   "
                state_prefix = "└── " if is_last_state else "├── "

                lines.append(f"{state_indent}{state_prefix}{state_tone}")

                # Sort scales
                sorted_scales = sorted(structure[size][state_tone].keys(), key=lambda x: float(x) if x.replace('.', '').isdigit() else float('inf'))

                for k, scale in enumerate(sorted_scales):
                    is_last_scale = (k == len(sorted_scales) - 1)
                    scale_indent = state_indent + ("    " if is_last_state else "│   ")
                    scale_prefix = "└── " if is_last_scale else "├── "

                    lines.append(f"{scale_indent}{scale_prefix}{scale}")

                    # Sort files
                    files = structure[size][state_tone][scale]
                    sorted_files = sorted(files, key=lambda x: x['filename'])

                    for l, file_info in enumerate(sorted_files):
                        is_last_file = (l == len(sorted_files) - 1)
                        file_indent = scale_indent + ("    " if is_last_scale else "│   ")
                        file_prefix = "└── " if is_last_file else "├── "

                        # Build file display with metadata
                        filename = file_info['filename']
                        metadata = file_info['metadata']

                        # Add filename
                        lines.append(f"{file_indent}{file_prefix}{filename}")

                        # Add metadata lines with proper indentation
                        metadata_indent = file_indent + ("    " if is_last_file else "│   ")
                        metadata_lines = self._format_metadata_lines(metadata)
                        for meta_line in metadata_lines:
                            lines.append(f"{metadata_indent}    {meta_line}")

        return "\n".join(lines)

    def _parse_filename_metadata(self, filename):
        """Parse metadata from DCI filename according to specification"""
        metadata = {
            'priority': 1,
            'padding': 0,
            'palette': -1,
            'scale': '1x',
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

        # Remove file extension and handle alpha8 format
        name_without_ext = filename
        if filename.endswith('.alpha8'):
            metadata['is_alpha8'] = True
            name_without_ext = filename[:-8]
            if '.' in name_without_ext:
                name_without_ext = name_without_ext.rsplit('.', 1)[0]
        elif '.' in filename:
            ext = filename.rsplit('.', 1)[1]
            metadata['format'] = ext
            name_without_ext = filename.rsplit('.', 1)[0]

        # Parse filename format: priority.padding.palette.color_adjustments
        # Example: 2.5p.0.10_20_30_-10_15_-5_25
        parts = name_without_ext.split('.')

        if len(parts) >= 1:
            # Priority (always present)
            try:
                metadata['priority'] = int(parts[0])
            except ValueError:
                pass

        if len(parts) >= 2:
            # Padding (format: Np where N is number)
            padding_str = parts[1]
            if padding_str.endswith('p'):
                try:
                    metadata['padding'] = int(padding_str[:-1])
                except ValueError:
                    pass

        if len(parts) >= 3:
            # Palette
            try:
                metadata['palette'] = int(parts[2])
            except ValueError:
                pass

        if len(parts) >= 4:
            # Color adjustments: hue_saturation_brightness_red_green_blue_alpha
            color_str = parts[3]
            if '_' in color_str:
                try:
                    adjustments = [int(x) for x in color_str.split('_')]
                    if len(adjustments) >= 7:
                        metadata['hue'] = adjustments[0]
                        metadata['saturation'] = adjustments[1]
                        metadata['brightness'] = adjustments[2]
                        metadata['red'] = adjustments[3]
                        metadata['green'] = adjustments[4]
                        metadata['blue'] = adjustments[5]
                        metadata['alpha'] = adjustments[6]
                except ValueError:
                    pass

        return metadata

    def _format_metadata_lines(self, metadata):
        """Format metadata into separate lines"""
        lines = []

        # Scale (always show)
        lines.append(f"[{t('metadata.scale')}: {metadata.get('scale', '1x')}]")

        # Priority (always show)
        lines.append(f"[{t('metadata.priority')}: {metadata.get('priority', 1)}]")

        # Palette (only show if not default)
        palette_value = metadata.get('palette', -1)
        if palette_value != -1:
            palette_names = {
                0: t("metadata.palette.foreground"),
                1: t("metadata.palette.background"),
                2: t("metadata.palette.highlight_foreground"),
                3: t("metadata.palette.highlight")
            }
            palette_name = palette_names.get(palette_value, f"Palette{palette_value}")
            lines.append(f"[{t('palette')}: {palette_name}]")

        # Padding (only show if not zero)
        padding = metadata.get('padding', 0)
        if padding > 0:
            lines.append(f"[{t('metadata.padding')}: {padding}{t('px')}]")

        # Color adjustments (only show non-zero values, with clear descriptions)
        if metadata.get('hue', 0) != 0:
            lines.append(f"[{t('metadata.hue_adjustment')}: {metadata['hue']:+d}%]")
        if metadata.get('saturation', 0) != 0:
            lines.append(f"[{t('metadata.saturation_adjustment')}: {metadata['saturation']:+d}%]")
        if metadata.get('brightness', 0) != 0:
            lines.append(f"[{t('metadata.brightness_adjustment')}: {metadata['brightness']:+d}%]")
        if metadata.get('red', 0) != 0:
            lines.append(f"[{t('metadata.red_component')}: {metadata['red']:+d}%]")
        if metadata.get('green', 0) != 0:
            lines.append(f"[{t('metadata.green_component')}: {metadata['green']:+d}%]")
        if metadata.get('blue', 0) != 0:
            lines.append(f"[{t('metadata.blue_component')}: {metadata['blue']:+d}%]")
        if metadata.get('alpha', 0) != 0:
            lines.append(f"[{t('metadata.alpha_adjustment')}: {metadata['alpha']:+d}%]")

        # Alpha8 format (special indicator)
        if metadata.get('is_alpha8', False):
            lines.append(f"[{t('metadata.alpha8_format')}]")

        return lines


# Register the node
NODE_CLASS_MAPPINGS = {
    "DCIAnalysis": DCIAnalysis
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIAnalysis": t("DCI Analysis")
}
