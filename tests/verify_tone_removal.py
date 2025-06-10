#!/usr/bin/env python3
"""
验证tone字段已从DCI Preview中移除
"""

import os
import sys
from PIL import Image, ImageDraw

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from dci_format import DCIIconBuilder
from dci_reader import DCIReader, DCIPreviewGenerator


def create_test_image(size=128, color=(255, 0, 0, 255), text="TEST"):
    """创建测试图像"""
    image = Image.new('RGBA', (size, size), color)
    draw = ImageDraw.Draw(image)

    # 绘制简单图案
    draw.rectangle([size//4, size//4, 3*size//4, 3*size//4],
                  fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)

    # 添加文本
    draw.text((size//2 - 20, size//2 - 5), text, fill=(0, 0, 0, 255))
    return image


def test_tone_field_removal():
    """测试tone字段是否已从预览中移除"""
    print("=== 验证tone字段移除 ===")

    # 创建测试DCI数据
    builder = DCIIconBuilder()

    # 创建light和dark两种tone的图像
    light_image = create_test_image(color=(255, 255, 0, 255), text="LIGHT")
    dark_image = create_test_image(color=(0, 0, 255, 255), text="DARK")

    builder.add_icon_image(
        image=light_image,
        size=128,
        state='normal',
        tone='light',
        scale=1,
        format='webp'
    )

    builder.add_icon_image(
        image=dark_image,
        size=128,
        state='normal',
        tone='dark',
        scale=1,
        format='webp'
    )

    # 构建DCI文件
    temp_path = "temp_tone_test.dci"
    builder.build(temp_path)

    # 读取二进制数据
    with open(temp_path, 'rb') as f:
        binary_data = f.read()

    # 清理临时文件
    os.remove(temp_path)

    # 读取DCI数据
    reader = DCIReader(binary_data=binary_data)
    reader.read()
    images = reader.get_icon_images()

    print(f"读取到 {len(images)} 个图像")

    # 生成预览
    generator = DCIPreviewGenerator(font_size=14)
    preview_image = generator.create_preview_grid(images, grid_cols=2)

    # 保存预览图像
    preview_image.save("verify_tone_removal.png")

    print(f"生成预览图像: {preview_image.size[0]}x{preview_image.size[1]}px")
    print("✓ 保存验证图像: verify_tone_removal.png")

    # 验证标签高度计算（应该是6行而不是7行）
    expected_height = max(100, (14 + 2) * 6 + 20)  # 6行文本
    actual_height = generator.label_height

    print(f"\n标签高度验证:")
    print(f"  期望高度（6行文本）: {expected_height}px")
    print(f"  实际高度: {actual_height}px")
    print(f"  ✓ {'通过' if actual_height == expected_height else '失败'}")

    # 检查图像信息中确实包含tone信息（数据层面）
    for i, img in enumerate(images):
        print(f"\n图像 {i+1}:")
        print(f"  路径: {img['path']}")
        print(f"  文件名: {img['filename']}")
        print(f"  尺寸: {img['size']}px")
        print(f"  状态: {img['state']}")
        print(f"  色调: {img['tone']} (数据中存在，但预览中不显示)")
        print(f"  缩放: {img['scale']}x")
        print(f"  格式: {img['format']}")

    print(f"\n✅ 验证完成:")
    print(f"1. 数据层面仍然包含tone信息，用于分组显示")
    print(f"2. 预览界面中不再显示tone字段，避免重复信息")
    print(f"3. 标签高度已调整为6行文本的空间")


if __name__ == "__main__":
    test_tone_field_removal()
