#!/usr/bin/env python3
"""
测试字体大小修复的脚本
验证DCI Preview在不同字体大小下是否能正确显示文本内容
"""

import os
import sys
from PIL import Image, ImageDraw

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py', 'nodes'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py', 'utils'))

from dci_format import DCIIconBuilder
from dci_reader import DCIReader, DCIPreviewGenerator
from preview_node import DCIPreviewNode


def create_test_image(size=256, color=(255, 0, 0, 255), text="TEST"):
    """创建测试图像"""
    image = Image.new('RGBA', (size, size), color)
    draw = ImageDraw.Draw(image)

    # 绘制简单图案
    draw.rectangle([size//4, size//4, 3*size//4, 3*size//4],
                  fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)

    # 添加文本
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size//16)
    except:
        font = None

    # 计算文本位置
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = len(text) * 6
        text_height = 11

    x = (size - text_width) // 2
    y = (size - text_height) // 2

    draw.text((x, y), text, fill=(0, 0, 0, 255), font=font)
    return image


def create_test_dci_binary():
    """创建测试DCI二进制数据"""
    print("创建测试DCI数据...")

    builder = DCIIconBuilder()

    # 创建不同状态的图像
    state_images = {
        'normal': create_test_image(color=(0, 255, 0, 255), text="NORMAL"),
        'hover': create_test_image(color=(255, 255, 0, 255), text="HOVER"),
        'pressed': create_test_image(color=(255, 0, 0, 255), text="PRESS"),
    }

    # 添加多种组合的图像
    sizes = [64, 128]
    tones = ['light', 'dark']
    scales = [1, 2]
    formats = ['webp', 'png']

    for size in sizes:
        for state, img in state_images.items():
            for tone in tones:
                for scale in scales:
                    for format in formats:
                        resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
                        builder.add_icon_image(
                            image=resized_img,
                            size=size,
                            state=state,
                            tone=tone,
                            scale=scale,
                            format=format
                        )

    # 构建并返回二进制数据
    temp_path = "temp_test.dci"
    builder.build(temp_path)

    with open(temp_path, 'rb') as f:
        binary_data = f.read()

    # 清理临时文件
    if os.path.exists(temp_path):
        os.remove(temp_path)

    print(f"✓ 创建了 {len(binary_data)} 字节的测试DCI数据")
    return binary_data


def test_font_size_preview():
    """测试不同字体大小的预览效果"""
    print("\n=== 测试字体大小预览效果 ===")

    # 创建测试数据
    binary_data = create_test_dci_binary()

    # 测试不同的字体大小
    font_sizes = [8, 12, 18, 24, 32, 40, 50]

    for font_size in font_sizes:
        print(f"\n测试字体大小: {font_size}px")

        # 创建预览节点
        node = DCIPreviewNode()

        # 生成预览
        result = node._execute(
            dci_binary_data=binary_data,
            light_background_color="light_gray",
            dark_background_color="dark_gray",
            text_font_size=font_size
        )

        # 检查结果
        assert 'ui' in result, f"字体大小 {font_size} 的结果应该有 'ui' 键"
        assert 'images' in result['ui'], f"字体大小 {font_size} 的UI应该有 'images' 键"
        assert 'text' in result['ui'], f"字体大小 {font_size} 的UI应该有 'text' 键"

        # 检查文本内容
        text_content = result['ui']['text'][0]
        assert f"字体大小: {font_size}" in text_content, f"文本应该包含字体大小信息"
        assert "📂" in text_content, f"文本应该包含文件路径信息"

        print(f"  ✓ 字体大小 {font_size}px 测试通过")


def test_preview_generator_directly():
    """直接测试DCIPreviewGenerator的字体大小处理"""
    print("\n=== 直接测试DCIPreviewGenerator ===")

    # 创建测试数据
    binary_data = create_test_dci_binary()

    # 读取DCI数据
    reader = DCIReader(binary_data=binary_data)
    reader.read()
    images = reader.get_icon_images()

    print(f"读取到 {len(images)} 个图像")

    # 测试不同字体大小的预览生成器
    font_sizes = [8, 12, 18, 24, 32, 40, 50]

    for font_size in font_sizes:
        print(f"\n测试DCIPreviewGenerator字体大小: {font_size}px")

        # 创建预览生成器
        generator = DCIPreviewGenerator(font_size=font_size)

        # 检查label_height是否正确计算
        expected_min_height = (font_size + 2) * 7 + 20
        actual_height = generator.label_height

        print(f"  字体大小: {font_size}px")
        print(f"  期望最小高度: {expected_min_height}px")
        print(f"  实际标签高度: {actual_height}px")

        assert actual_height >= expected_min_height, f"标签高度应该至少为 {expected_min_height}px，实际为 {actual_height}px"

        # 生成预览图像
        preview_image = generator.create_preview_grid(images[:4], grid_cols=2)  # 只取前4个图像进行测试

        print(f"  生成预览图像: {preview_image.size[0]}x{preview_image.size[1]}px")

        # 保存测试图像（可选）
        output_path = f"test_font_{font_size}.png"
        preview_image.save(output_path)
        print(f"  ✓ 保存测试图像: {output_path}")


def test_text_overflow_handling():
    """测试文本溢出处理"""
    print("\n=== 测试文本溢出处理 ===")

    # 创建一个有很长路径的测试图像
    test_image = create_test_image(text="LONG")

    # 模拟一个有很长路径的图像信息
    long_path_image = {
        'image': test_image,
        'size': 256,
        'state': 'normal',
        'tone': 'light',
        'scale': 1,
        'format': 'webp',
        'file_size': 12345,
        'path': 'very/long/path/with/many/subdirectories/that/might/cause/overflow',
        'filename': 'very_long_filename_that_might_cause_text_overflow.webp'
    }

    # 测试小字体大小（应该能处理溢出）
    small_font_generator = DCIPreviewGenerator(font_size=8)
    preview_small = small_font_generator.create_preview_grid([long_path_image], grid_cols=1)

    # 测试大字体大小（应该能处理溢出）
    large_font_generator = DCIPreviewGenerator(font_size=40)
    preview_large = large_font_generator.create_preview_grid([long_path_image], grid_cols=1)

    print(f"  小字体预览: {preview_small.size[0]}x{preview_small.size[1]}px")
    print(f"  大字体预览: {preview_large.size[0]}x{preview_large.size[1]}px")

    # 保存测试图像
    preview_small.save("test_overflow_small.png")
    preview_large.save("test_overflow_large.png")

    print("  ✓ 文本溢出处理测试完成")


if __name__ == "__main__":
    print("开始字体大小修复测试...")

    try:
        test_font_size_preview()
        test_preview_generator_directly()
        test_text_overflow_handling()

        print("\n🎉 所有测试通过！字体大小问题已修复。")
        print("\n修复内容:")
        print("1. DCIPreviewGenerator的label_height现在根据字体大小动态计算")
        print("2. 文本绘制时会检查可用空间，防止溢出")
        print("3. 当空间不足时会显示省略号，确保界面整洁")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
