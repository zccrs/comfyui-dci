def format_file_size(size_in_bytes):
    """Format file size in bytes to human readable format"""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes/1024:.1f} KB"
    else:
        return f"{size_in_bytes/(1024*1024):.1f} MB"

def format_dci_path(size, state, tone, scale, format_type, priority=1, padding=0, palette=-1,
                   hue=0, saturation=0, brightness=0, red=0, green=0, blue=0, alpha=0):
    """Format DCI path components into a standard path with layer parameters

    Args:
        size: Icon size in pixels
        state: Icon state (normal, disabled, hover, pressed)
        tone: Tone type (light, dark)
        scale: Scale factor
        format_type: Image format (png, webp, jpg)
        priority: Layer priority (1-n), default 1
        padding: Outer padding value (integer), default 0, will be formatted with 'p' suffix
        palette: Palette type (-1=none, 0=foreground, 1=background, 2=highlight_foreground, 3=highlight), default -1
        hue: Hue adjustment (-100 to 100), default 0
        saturation: Saturation adjustment (-100 to 100), default 0
        brightness: Brightness adjustment (-100 to 100), default 0
        red: Red adjustment (-100 to 100), default 0
        green: Green adjustment (-100 to 100), default 0
        blue: Blue adjustment (-100 to 100), default 0
        alpha: Alpha adjustment (-100 to 100), default 0
    """
    scale_str = f"{scale:g}"  # Remove trailing zeros

    # Format padding with 'p' suffix according to DCI specification
    padding_str = f"{padding}p"

    # Format color adjustments with underscore separator
    color_adjustments = f"{hue}_{saturation}_{brightness}_{red}_{green}_{blue}_{alpha}"

    # Format layer filename according to DCI specification
    # Format: priority.padding_with_p.palette.color_adjustments_with_underscores.format
    layer_filename = f"{priority}.{padding_str}.{palette}.{color_adjustments}.{format_type}"

    return f"{size}/{state}.{tone}/{scale_str}/{layer_filename}"

def format_image_info(image_data, index=None):
    """Format image information for display"""
    lines = []

    if index is not None:
        lines.append(f"图像 #{index}:")

    # Basic information
    lines.extend([
        f"  📁 DCI路径: {image_data.get('path', 'N/A')}",
        f"  📏 图标尺寸: {image_data.get('size', 'N/A')}px",
        f"  🎭 状态: {image_data.get('state', 'N/A')}",
        f"  🎨 色调: {image_data.get('tone', 'N/A')}",
        f"  🔍 缩放因子: {image_data.get('scale', 'N/A')}x",
        f"  🗂️  图像格式: {image_data.get('format', 'N/A')}",
    ])

    # Layer information
    if 'layer_priority' in image_data:
        lines.extend([
            f"  🏷️  图层优先级: {image_data.get('layer_priority', 1)}",
            f"  📐 外边框: {image_data.get('layer_padding', 0.0)}",
            f"  🎨 调色板: {image_data.get('palette_type', 'none')}",
        ])

        # Color adjustments (only show non-zero values)
        color_adjustments = []
        if image_data.get('hue_adjustment', 0) != 0:
            color_adjustments.append(f"色调:{image_data['hue_adjustment']}")
        if image_data.get('saturation_adjustment', 0) != 0:
            color_adjustments.append(f"饱和度:{image_data['saturation_adjustment']}")
        if image_data.get('brightness_adjustment', 0) != 0:
            color_adjustments.append(f"亮度:{image_data['brightness_adjustment']}")
        if image_data.get('red_adjustment', 0) != 0:
            color_adjustments.append(f"红:{image_data['red_adjustment']}")
        if image_data.get('green_adjustment', 0) != 0:
            color_adjustments.append(f"绿:{image_data['green_adjustment']}")
        if image_data.get('blue_adjustment', 0) != 0:
            color_adjustments.append(f"蓝:{image_data['blue_adjustment']}")
        if image_data.get('alpha_adjustment', 0) != 0:
            color_adjustments.append(f"透明度:{image_data['alpha_adjustment']}")

        if color_adjustments:
            lines.append(f"  🌈 颜色调整: {', '.join(color_adjustments)}")

    # Additional information if available
    if 'actual_size' in image_data:
        lines.append(f"  📊 实际尺寸: {image_data['actual_size']}px")
    if 'file_size' in image_data:
        lines.append(f"  📊 文件大小: {format_file_size(image_data['file_size'])}")
    if 'background_color' in image_data:
        lines.append(f"  🎯 背景处理: {image_data['background_color']}")

    return "\n".join(lines)

def format_binary_info(binary_data):
    """Format binary data information for display"""
    if not binary_data:
        return "No binary data available"

    lines = [
        "🔢 二进制数据信息:",
        f"  📊 文件大小: {format_file_size(len(binary_data))}",
        f"  🔗 数据类型: {type(binary_data).__name__}",
        ""
    ]

    # Show first few bytes as hex
    if len(binary_data) > 0:
        hex_preview = ' '.join(f'{b:02x}' for b in binary_data[:16])
        if len(binary_data) > 16:
            hex_preview += "..."
        lines.extend([
            "🔍 二进制数据预览 (前16字节):",
            f"  {hex_preview}",
            ""
        ])

    return "\n".join(lines)
