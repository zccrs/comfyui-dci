def format_file_size(size_in_bytes):
    """Format file size in bytes to human readable format"""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes/1024:.1f} KB"
    else:
        return f"{size_in_bytes/(1024*1024):.1f} MB"

def format_dci_path(size, state, tone, scale, format_type):
    """Format DCI path components into a standard path"""
    scale_str = f"{scale:g}"  # Remove trailing zeros
    return f"{size}/{state}.{tone}/{scale_str}/1.0.0.0.0.0.0.0.0.0.{format_type}"

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
