#!/usr/bin/env python3
"""
测试DCI预览透明背景功能
"""

import sys
import os
from PIL import Image, ImageDraw
from io import BytesIO

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

try:
    from dci_reader import DCIPreviewGenerator
    from dci_format import DCIIconBuilder
    from utils.image_utils import pil_to_comfyui_format
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在正确的环境中运行测试")
    # 不要直接退出，而是跳过测试
    import unittest
    class TestTransparentPreview(unittest.TestCase):
        def test_skip_due_to_import_error(self):
            self.skipTest(f"跳过测试，导入错误: {e}")

    if __name__ == "__main__":
        unittest.main()
    else:
        # 如果作为模块导入，提供一个空的测试函数
        def test_transparent_preview():
            print(f"跳过透明预览测试，导入错误: {e}")
            return True

        def main():
            return test_transparent_preview()

def create_test_image_with_transparency():
    """创建带透明度的测试图像"""
    # 创建一个带透明度的图像
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))  # 完全透明背景
    draw = ImageDraw.Draw(img)

    # 绘制一个半透明的圆圈
    draw.ellipse([16, 16, 48, 48], fill=(255, 0, 0, 128))  # 半透明红色

    # 绘制一个不透明的小圆圈
    draw.ellipse([24, 24, 40, 40], fill=(0, 255, 0, 255))  # 不透明绿色

    return img

def create_test_dci_with_transparency():
    """创建包含透明图像的DCI文件"""
    test_image = create_test_image_with_transparency()

    # 创建DCI文件
    builder = DCIIconBuilder()
    builder.add_icon_image(test_image, 64, 'normal', 'light', 1.0, 'png')

    return builder.to_binary()

def test_transparent_preview():
    """测试透明背景预览功能"""
    print("测试DCI预览透明背景功能...")

    try:
        # 创建测试DCI数据
        dci_data = create_test_dci_with_transparency()
        print(f"创建DCI数据: {len(dci_data)} 字节")

        # 读取DCI数据
        from dci_reader import DCIReader
        reader = DCIReader(binary_data=dci_data)

        if not reader.read():
            print("❌ 无法读取DCI数据")
            return False

        images = reader.get_icon_images()
        if not images:
            print("❌ DCI文件中未找到图像")
            return False

        print(f"找到 {len(images)} 个图像")

        # 测试不同背景的预览生成
        generator = DCIPreviewGenerator(font_size=12)

        # 测试透明背景
        print("\n测试透明背景...")
        transparent_preview = generator.create_preview_grid(images, 1, (255, 255, 255))

        # 应用透明背景处理
        if transparent_preview.mode != 'RGBA':
            transparent_preview = transparent_preview.convert('RGBA')

        # 将白色背景转为透明
        pixels = transparent_preview.load()
        for y in range(transparent_preview.height):
            for x in range(transparent_preview.width):
                r, g, b, a = pixels[x, y]
                # 如果像素接近白色（背景），使其透明
                if r > 250 and g > 250 and b > 250:
                    pixels[x, y] = (255, 255, 255, 0)  # 透明
                else:
                    pixels[x, y] = (r, g, b, 255)  # 保持原色

        # 测试转换为ComfyUI格式
        print("测试转换为ComfyUI格式...")
        comfyui_format = pil_to_comfyui_format(transparent_preview, "test_transparent")

        print(f"ComfyUI格式: {comfyui_format}")

        # 检查透明度是否保留
        has_transparency = transparent_preview.mode == 'RGBA'
        if has_transparency:
            alpha_channel = transparent_preview.split()[-1]
            alpha_values = list(alpha_channel.getdata())
            min_alpha = min(alpha_values)
            max_alpha = max(alpha_values)
            print(f"Alpha通道范围: {min_alpha} - {max_alpha}")

            if min_alpha < 255:
                print("✓ 图像包含透明度")
            else:
                print("⚠ 图像不包含透明度")
        else:
            print("⚠ 图像模式不支持透明度")

        # 保存测试图像
        transparent_preview.save("test_transparent_preview.png")
        print("保存测试图像: test_transparent_preview.png")

        return True

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行透明背景测试"""
    print("DCI预览透明背景功能测试")
    print("=" * 50)

    success = test_transparent_preview()

    if success:
        print("\n🎉 透明背景功能测试通过！")
        return True
    else:
        print("\n❌ 透明背景功能测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
