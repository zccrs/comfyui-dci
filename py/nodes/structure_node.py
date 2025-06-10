"""
DCI Structure Preview Node
专门用于预览DCI文件内部结构的节点，以树状结构展示所有元信息
"""

from .base_node import BaseNode

try:
    from ..dci_reader import DCIReader
except ImportError:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(current_dir))
    from dci_reader import DCIReader


class DCIStructureNode(BaseNode):
    """ComfyUI node for displaying DCI file internal structure in tree format"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dci_binary_data": ("BINARY_DATA",),
            },
            "optional": {
                "show_file_details": ("BOOLEAN", {"default": True}),
                "show_layer_metadata": ("BOOLEAN", {"default": True}),
                "show_file_sizes": ("BOOLEAN", {"default": True}),
                "compact_mode": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "execute"
    CATEGORY = "DCI/Analysis"
    OUTPUT_NODE = True

    def _execute(self, dci_binary_data, show_file_details=True, show_layer_metadata=True, show_file_sizes=True, compact_mode=False):
        """Display DCI file internal structure in tree format"""

        # Use binary data
        reader = DCIReader(binary_data=dci_binary_data)

        # Read DCI data
        if not reader.read():
            return {"ui": {"text": ["Failed to read DCI data"]}}

        # Extract images
        images = reader.get_icon_images()
        if not images:
            return {"ui": {"text": ["No images found in DCI file"]}}

        # Generate tree structure
        tree_structure = self._generate_tree_structure(images, show_file_details, show_layer_metadata, show_file_sizes, compact_mode)

        # Generate summary statistics
        summary = self._generate_summary_statistics(images)

        # Combine structure and summary
        full_output = f"{summary}\n\n{tree_structure}"

        return {"ui": {"text": [full_output]}}

    def _generate_tree_structure(self, images, show_file_details, show_layer_metadata, show_file_sizes, compact_mode):
        """Generate tree structure representation of DCI file"""

        # Organize images by directory structure
        structure = {}

        for img in images:
            # Parse path: size/state.tone/scale/filename
            path_parts = img['path'].split('/')
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

                # Add file info
                file_info = {
                    'filename': img['filename'],
                    'file_size': img['file_size'],
                    'format': img['format'],
                    'image': img
                }

                # Parse layer metadata from filename if requested
                if show_layer_metadata:
                    file_info['layer_metadata'] = self._parse_layer_metadata(img['filename'])

                structure[size][state_tone][scale].append(file_info)

        # Generate tree text
        lines = []
        lines.append("DCI File Structure:")
        lines.append("├─ (Size/State.Tone/Scale/Layer)")

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

                # Parse state and tone for display
                if '.' in state_tone:
                    state, tone = state_tone.split('.', 1)
                    display_name = f"{state}.{tone}"
                else:
                    display_name = state_tone

                lines.append(f"{state_indent}{state_prefix}{display_name}")

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

                        # Build file display name
                        filename = file_info['filename']
                        file_display = filename

                        if show_file_sizes:
                            size_str = self._format_file_size(file_info['file_size'])
                            file_display += f" ({size_str})"

                        lines.append(f"{file_indent}{file_prefix}{file_display}")

                        # Add layer metadata if requested and not in compact mode
                        if show_layer_metadata and not compact_mode and 'layer_metadata' in file_info:
                            metadata = file_info['layer_metadata']
                            if metadata:
                                metadata_indent = file_indent + ("    " if is_last_file else "│   ")
                                for meta_line in metadata:
                                    lines.append(f"{metadata_indent}  {meta_line}")

        return "\n".join(lines)

    def _parse_layer_metadata(self, filename):
        """Parse layer metadata from DCI filename according to specification"""
        metadata = []

        # Remove file extension
        name_without_ext = filename
        if '.' in filename:
            # Handle special cases like .webp.alpha8
            if filename.endswith('.alpha8'):
                # Remove .alpha8 first
                name_without_ext = filename[:-8]
                metadata.append("🔍 Alpha8 format (调色板优化)")
                # Then remove the base format
                if '.' in name_without_ext:
                    name_without_ext = name_without_ext.rsplit('.', 1)[0]
            else:
                name_without_ext = filename.rsplit('.', 1)[0]

        # Parse filename format: priority.padding.palette.color_adjustments
        # Example: 2.5p.0.10_20_30_-10_15_-5_25
        parts = name_without_ext.split('.')

        if len(parts) >= 1:
            # Priority (always present)
            try:
                priority = int(parts[0])
                metadata.append(f"📊 优先级: {priority}")
            except ValueError:
                pass

        if len(parts) >= 2:
            # Padding (format: Np where N is number)
            padding_str = parts[1]
            if padding_str.endswith('p'):
                try:
                    padding = int(padding_str[:-1])
                    if padding > 0:
                        metadata.append(f"📐 外边框: {padding}px")
                except ValueError:
                    pass

        if len(parts) >= 3:
            # Palette
            try:
                palette = int(parts[2])
                palette_names = {
                    -1: "无调色板",
                    0: "前景色",
                    1: "背景色",
                    2: "高亮前景色",
                    3: "高亮色"
                }
                palette_name = palette_names.get(palette, f"调色板{palette}")
                if palette != -1:
                    metadata.append(f"🎨 调色板: {palette_name}")
            except ValueError:
                pass

        if len(parts) >= 4:
            # Color adjustments: hue_saturation_lightness_red_green_blue_alpha
            color_str = parts[3]
            if '_' in color_str:
                try:
                    adjustments = [int(x) for x in color_str.split('_')]
                    if len(adjustments) >= 7:
                        hue, sat, light, red, green, blue, alpha = adjustments[:7]

                        # Only show non-zero adjustments
                        color_adjustments = []
                        if hue != 0:
                            color_adjustments.append(f"色调{hue:+d}%")
                        if sat != 0:
                            color_adjustments.append(f"饱和度{sat:+d}%")
                        if light != 0:
                            color_adjustments.append(f"亮度{light:+d}%")
                        if red != 0:
                            color_adjustments.append(f"红{red:+d}%")
                        if green != 0:
                            color_adjustments.append(f"绿{green:+d}%")
                        if blue != 0:
                            color_adjustments.append(f"蓝{blue:+d}%")
                        if alpha != 0:
                            color_adjustments.append(f"透明度{alpha:+d}%")

                        if color_adjustments:
                            metadata.append(f"🌈 颜色调整: {', '.join(color_adjustments)}")

                except ValueError:
                    pass

        return metadata

    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f}KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f}MB"

    def _generate_summary_statistics(self, images):
        """Generate summary statistics for the DCI file"""
        total_images = len(images)
        total_size = sum(img['file_size'] for img in images)

        # Collect unique values
        sizes = sorted(set(int(img['size']) for img in images))
        states = sorted(set(img['state'] for img in images))
        tones = sorted(set(img['tone'] for img in images))
        scales = sorted(set(float(img['scale']) for img in images))
        formats = sorted(set(img['format'] for img in images))

        # Count by categories
        size_counts = {}
        state_counts = {}
        tone_counts = {}

        for img in images:
            size = img['size']
            state = img['state']
            tone = img['tone']

            size_counts[size] = size_counts.get(size, 0) + 1
            state_counts[state] = state_counts.get(state, 0) + 1
            tone_counts[tone] = tone_counts.get(tone, 0) + 1

        lines = []
        lines.append("📋 DCI File Summary")
        lines.append("=" * 50)
        lines.append(f"📊 总计: {total_images} 个图像文件")
        lines.append(f"💾 总大小: {self._format_file_size(total_size)}")
        lines.append("")

        lines.append(f"📏 图标尺寸: {', '.join(map(str, sizes))}px")
        lines.append(f"🎭 状态类型: {', '.join(states)}")
        lines.append(f"🌓 色调类型: {', '.join(tones)}")
        lines.append(f"🔍 缩放比例: {', '.join(f'{s:g}x' for s in scales)}")
        lines.append(f"🖼️  图像格式: {', '.join(formats)}")
        lines.append("")

        # Detailed breakdown
        lines.append("📈 详细分布:")
        lines.append(f"  尺寸分布: {', '.join(f'{size}px({count})' for size, count in sorted(size_counts.items(), key=lambda x: int(x[0])))}")
        lines.append(f"  状态分布: {', '.join(f'{state}({count})' for state, count in sorted(state_counts.items()))}")
        lines.append(f"  色调分布: {', '.join(f'{tone}({count})' for tone, count in sorted(tone_counts.items()))}")

        return "\n".join(lines)


# Register the node
NODE_CLASS_MAPPINGS = {
    "DCIStructureNode": DCIStructureNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIStructureNode": "DCI Structure Preview"
}
