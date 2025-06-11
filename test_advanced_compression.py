#!/usr/bin/env python3
"""
测试WebP和PNG高级压缩设置功能
"""

import sys
import os
from PIL import Image, ImageDraw
from io import BytesIO

def create_complex_test_image(size=(256, 256)):
    """创建复杂的测试图像，包含透明度和细节"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))  # 透明背景
    draw = ImageDraw.Draw(img)

    # 添加复杂的图案来更好地展示压缩差异
    for i in range(0, size[0], 16):
        for j in range(0, size[1], 16):
            # 创建带透明度的彩色方块
            alpha = (i + j) % 256
            color = (i % 256, j % 256, (i+j) % 256, alpha)
            draw.rectangle([i, j, i+15, j+15], fill=color)

    return img

def test_webp_settings():
    """测试WebP的各种设置"""
    print("测试WebP高级设置...")

    img = create_complex_test_image()

    # 测试不同的WebP设置
    settings = [
        {"name": "标准有损", "lossless": False, "quality": 80, "near_lossless": 100, "alpha_quality": 100},
        {"name": "无损压缩", "lossless": True, "quality": 80, "near_lossless": 100, "alpha_quality": 100},
        {"name": "近无损80", "lossless": False, "quality": 80, "near_lossless": 80, "alpha_quality": 100},
        {"name": "低透明度质量", "lossless": False, "quality": 80, "near_lossless": 100, "alpha_quality": 50},
    ]

    results = []

    for setting in settings:
        webp_bytes = BytesIO()

        if setting["lossless"]:
            img.save(webp_bytes, format='WEBP', lossless=True)
        elif setting["near_lossless"] < 100:
            img.save(webp_bytes, format='WEBP', quality=setting["quality"], method=6, near_lossless=setting["near_lossless"])
        else:
            img.save(webp_bytes, format='WEBP', quality=setting["quality"], alpha_quality=setting["alpha_quality"])

        size = len(webp_bytes.getvalue())
        results.append((setting["name"], size))

        print(f"  {setting['name']:15}: {size:6d} 字节")

    return results

def test_png_settings():
    """测试PNG的压缩等级设置"""
    print("\n测试PNG压缩等级...")

    img = create_complex_test_image()

    results = []

    for compress_level in range(0, 10):  # PNG压缩等级 0-9
        png_bytes = BytesIO()
        img.save(png_bytes, format='PNG', compress_level=compress_level)
        size = len(png_bytes.getvalue())
        results.append((f"等级 {compress_level}", size))

        print(f"  压缩等级 {compress_level}: {size:6d} 字节")

    return results

def main():
    """运行所有测试"""
    print("WebP和PNG高级压缩设置测试")
    print("=" * 50)

    try:
        # 测试WebP设置
        webp_results = test_webp_settings()

        # 测试PNG设置
        png_results = test_png_settings()

        print("\n" + "=" * 50)
        print("测试总结:")

        # WebP结果分析
        webp_sizes = [size for _, size in webp_results]
        print(f"WebP 文件大小范围: {min(webp_sizes)} - {max(webp_sizes)} 字节")

        # PNG结果分析
        png_sizes = [size for _, size in png_results]
        print(f"PNG 文件大小范围: {min(png_sizes)} - {max(png_sizes)} 字节")

        # 验证设置是否有效
        webp_effective = max(webp_sizes) > min(webp_sizes)
        png_effective = max(png_sizes) > min(png_sizes)

        print(f"WebP 设置有效性: {'✓' if webp_effective else '✗'}")
        print(f"PNG 设置有效性: {'✓' if png_effective else '✗'}")

        if webp_effective and png_effective:
            print("\n🎉 所有高级压缩设置功能正常工作！")
            return True
        else:
            print("\n❌ 某些设置可能无效")
            return False

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
