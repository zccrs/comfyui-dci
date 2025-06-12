#!/usr/bin/env python3
"""
测试DCI预览边框颜色跟随文字颜色功能
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
except ImportError as e:
    print(f"导入错误: {e}")
    sys.exit(1)

def create_test_dci_with_images():
    """创建包含测试图像的DCI文件"""
    # 创建一个简单的测试图像
    test_image = Image.new('RGBA', (64, 64), (255, 0, 0, 128))  # 半透明红色
    draw = ImageDraw.Draw(test_image)
    draw.ellipse([16, 16, 48, 48], fill=(0, 255, 0, 255))  # 绿色圆圈

    # 创建DCI文件
    builder = DCIIconBuilder()
    builder.add_icon_image(test_image, 64, 'normal', 'light', 1.0, 'png')
    builder.add_icon_image(test_image, 64, 'normal', 'dark', 1.0, 'png')

    return builder.to_binary()

def test_border_color_consistency():
    """测试边框颜色与文字颜色的一致性"""
    print("测试边框颜色跟随文字颜色功能...")

    # 创建测试DCI数据
    dci_data = create_test_dci_with_images()

    # 测试不同背景颜色下的边框和文字颜色
    test_backgrounds = [
        ("白色背景", (255, 255, 255)),
        ("浅灰背景", (240, 240, 240)),
        ("中灰背景", (128, 128, 128)),
        ("深灰背景", (64, 64, 64)),
        ("黑色背景", (0, 0, 0)),
        ("蓝色背景", (0, 100, 200)),
        ("绿色背景", (0, 150, 0)),
        ("红色背景", (200, 0, 0)),
    ]

    results = []

    for bg_name, bg_color in test_backgrounds:
        # 创建预览生成器
        generator = DCIPreviewGenerator(background_color=bg_color, font_size=14)

        # 获取文字颜色和边框颜色
        text_color = generator.text_color
        border_color = generator._get_border_color()

        # 计算颜色相似度
        text_brightness = sum(text_color) / 3
        border_brightness = sum(border_color) / 3
        bg_brightness = sum(bg_color) / 3

        # 检查边框颜色是否与文字颜色相关
        color_diff = abs(text_brightness - border_brightness)

        results.append({
            'background': bg_name,
            'bg_color': bg_color,
            'text_color': text_color,
            'border_color': border_color,
            'bg_brightness': bg_brightness,
            'text_brightness': text_brightness,
            'border_brightness': border_brightness,
            'color_diff': color_diff
        })

        print(f"  {bg_name:12}: 背景{bg_color} -> 文字{text_color} -> 边框{border_color}")
        print(f"    {'':14} 亮度: 背景{bg_brightness:6.1f} 文字{text_brightness:6.1f} 边框{border_brightness:6.1f} 差异{color_diff:6.1f}")

    return results

def test_visual_preview_generation():
    """测试生成实际的预览图像"""
    print("\n生成可视化预览测试...")

    try:
        from dci_reader import DCIReader

        # 创建测试DCI数据
        dci_data = create_test_dci_with_images()

        # 读取DCI数据
        reader = DCIReader(binary_data=dci_data)
        if not reader.read():
            print("  ❌ 无法读取DCI数据")
            return False

        images = reader.get_icon_images()
        if not images:
            print("  ❌ 未找到图像")
            return False

        print(f"  ✓ 成功读取 {len(images)} 个图像")

        # 测试不同背景下的预览生成
        test_backgrounds = [
            ("light", (240, 240, 240)),
            ("dark", (32, 32, 32)),
            ("blue", (0, 100, 200)),
        ]

        for bg_name, bg_color in test_backgrounds:
            generator = DCIPreviewGenerator(background_color=bg_color, font_size=16)
            preview = generator.create_preview_grid(images, grid_cols=2, background_color=bg_color)

            # 保存预览图像
            output_path = f"test_preview_{bg_name}.png"
            preview.save(output_path)
            print(f"  ✓ 生成预览: {output_path}")

        return True

    except Exception as e:
        print(f"  ❌ 预览生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_color_relationships(results):
    """分析颜色关系"""
    print("\n颜色关系分析:")

    # 检查边框颜色是否确实跟随文字颜色
    consistent_count = 0
    total_count = len(results)

    for result in results:
        # 边框颜色应该与文字颜色相关，但有适当的差异以保证可见性
        color_diff = result['color_diff']

        # 合理的颜色差异范围（边框应该比文字稍微亮一些或暗一些）
        is_consistent = 30 <= color_diff <= 100

        if is_consistent:
            consistent_count += 1
            status = "✓"
        else:
            status = "✗"

        print(f"  {status} {result['background']:12}: 颜色差异 {color_diff:6.1f} {'(合理)' if is_consistent else '(需调整)'}")

    consistency_rate = consistent_count / total_count * 100
    print(f"\n  一致性评分: {consistent_count}/{total_count} ({consistency_rate:.1f}%)")

    return consistency_rate >= 70  # 70%以上认为是成功的

def main():
    """运行所有测试"""
    print("DCI预览边框颜色跟随文字颜色测试")
    print("=" * 50)

    try:
        # 测试颜色一致性
        results = test_border_color_consistency()

        # 测试可视化预览生成
        visual_success = test_visual_preview_generation()

        # 分析结果
        color_success = analyze_color_relationships(results)

        print("\n" + "=" * 50)
        print("测试总结:")
        print(f"颜色一致性测试: {'✓ 通过' if color_success else '✗ 失败'}")
        print(f"可视化预览测试: {'✓ 通过' if visual_success else '✗ 失败'}")

        if color_success and visual_success:
            print("\n🎉 边框颜色跟随文字颜色功能正常工作！")
            print("边框颜色现在会根据文字颜色自动调整，保持视觉一致性。")
            return True
        else:
            print("\n❌ 某些测试失败，需要进一步调整")
            return False

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
