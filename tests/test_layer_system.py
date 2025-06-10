#!/usr/bin/env python3
"""
Test script for DCI layer system functionality
测试DCI图层系统功能的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from py.utils.ui_utils import format_dci_path
    from py.dci_reader import DCIReader
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"项目根目录: {project_root}")
    print(f"Python路径: {sys.path}")
    sys.exit(1)

from io import BytesIO
import struct

def test_format_dci_path():
    """测试DCI路径格式化功能"""
    print("=== 测试DCI路径格式化 ===")

    # 测试基础路径
    basic_path = format_dci_path(256, "normal", "light", 1.0, "webp")
    print(f"基础路径: {basic_path}")
    expected_basic = "256/normal.light/1/1.0p.-1.0_0_0_0_0_0_0.webp"
    assert basic_path == expected_basic, f"期望: {expected_basic}, 实际: {basic_path}"

    # 测试带图层参数的路径
    layer_path = format_dci_path(
        size=64, state="hover", tone="dark", scale=2.0, format_type="png",
        priority=2, padding=5, palette=1,
        hue=10, saturation=20, brightness=30,
        red=-10, green=15, blue=-5, alpha=25
    )
    print(f"图层路径: {layer_path}")
    expected_layer = "64/hover.dark/2/2.5p.1.10_20_30_-10_15_-5_25.png"
    assert layer_path == expected_layer, f"期望: {expected_layer}, 实际: {layer_path}"

    # 测试小数缩放
    decimal_path = format_dci_path(128, "pressed", "light", 1.25, "webp", priority=3)
    print(f"小数缩放路径: {decimal_path}")
    expected_decimal = "128/pressed.light/1.25/3.0p.-1.0_0_0_0_0_0_0.webp"
    assert decimal_path == expected_decimal, f"期望: {expected_decimal}, 实际: {decimal_path}"

    print("✅ DCI路径格式化测试通过")

def test_layer_filename_parsing():
    """测试图层文件名解析功能"""
    print("\n=== 测试图层文件名解析 ===")

    reader = DCIReader()

    # 测试基础文件名
    basic_result = reader._parse_layer_filename("1.0p.-1.0_0_0_0_0_0_0.webp")
    print(f"基础文件名解析: {basic_result}")
    assert basic_result['priority'] == 1
    assert basic_result['padding'] == 0
    assert basic_result['palette'] == -1
    assert basic_result['palette_name'] == "none"
    assert basic_result['format'] == "webp"

    # 测试复杂图层文件名
    # 格式: priority.padding_with_p.palette.hue_saturation_brightness_red_green_blue_alpha.format
    complex_result = reader._parse_layer_filename("3.2p.5.1_-10_20_30_40_-50_60.png")
    print(f"复杂文件名解析: {complex_result}")
    assert complex_result['priority'] == 3
    assert complex_result['padding'] == 2  # 整数类型，去掉p后缀
    assert complex_result['palette'] == 5
    assert complex_result['palette_name'] == "unknown"  # 5不在预定义的调色板中
    assert complex_result['hue'] == 1
    assert complex_result['saturation'] == -10
    assert complex_result['brightness'] == 20
    assert complex_result['red'] == 30
    assert complex_result['green'] == 40
    assert complex_result['blue'] == -50
    assert complex_result['alpha'] == 60
    assert complex_result['format'] == "png"

    # 测试调色板类型映射
    palette_tests = [
        ("1.0p.-1.0_0_0_0_0_0_0.webp", "none"),
        ("1.0p.0.0_0_0_0_0_0_0.webp", "foreground"),
        ("1.0p.1.0_0_0_0_0_0_0.webp", "background"),
        ("1.0p.2.0_0_0_0_0_0_0.webp", "highlight_foreground"),
        ("1.0p.3.0_0_0_0_0_0_0.webp", "highlight"),
    ]

    for filename, expected_palette in palette_tests:
        result = reader._parse_layer_filename(filename)
        assert result['palette_name'] == expected_palette, \
            f"文件名 {filename} 期望调色板 {expected_palette}, 实际 {result['palette_name']}"

    print("✅ 图层文件名解析测试通过")

def test_palette_mapping():
    """测试调色板类型映射"""
    print("\n=== 测试调色板类型映射 ===")

    # 测试字符串到数值的映射
    palette_map = {
        "none": -1,
        "foreground": 0,
        "background": 1,
        "highlight_foreground": 2,
        "highlight": 3
    }

    for palette_name, expected_value in palette_map.items():
        path = format_dci_path(256, "normal", "light", 1.0, "webp", palette=expected_value)
        print(f"调色板 {palette_name} ({expected_value}): {path}")

        # 验证路径中包含正确的调色板值
        parts = path.split('/')
        filename = parts[-1]
        filename_parts = filename.split('.')
        actual_palette = int(filename_parts[2])
        assert actual_palette == expected_value, \
            f"调色板 {palette_name} 期望值 {expected_value}, 实际值 {actual_palette}"

    print("✅ 调色板类型映射测试通过")

def test_color_adjustment_ranges():
    """测试颜色调整参数范围"""
    print("\n=== 测试颜色调整参数范围 ===")

    # 测试边界值
    boundary_tests = [
        (-100, -100, -100, -100, -100, -100, -100),  # 最小值
        (100, 100, 100, 100, 100, 100, 100),         # 最大值
        (0, 0, 0, 0, 0, 0, 0),                       # 零值
        (-50, 25, 75, -25, 50, -75, 10),             # 混合值
    ]

    for hue, sat, bright, red, green, blue, alpha in boundary_tests:
        path = format_dci_path(
            256, "normal", "light", 1.0, "webp",
            hue=hue, saturation=sat, brightness=bright,
            red=red, green=green, blue=blue, alpha=alpha
        )
        print(f"颜色调整 H:{hue} S:{sat} B:{bright} R:{red} G:{green} B:{blue} A:{alpha}")
        print(f"  生成路径: {path}")

        # 验证解析结果
        reader = DCIReader()
        filename = path.split('/')[-1]
        parsed = reader._parse_layer_filename(filename)

        assert parsed['hue'] == hue, f"色调期望 {hue}, 实际 {parsed['hue']}"
        assert parsed['saturation'] == sat, f"饱和度期望 {sat}, 实际 {parsed['saturation']}"
        assert parsed['brightness'] == bright, f"亮度期望 {bright}, 实际 {parsed['brightness']}"
        assert parsed['red'] == red, f"红色期望 {red}, 实际 {parsed['red']}"
        assert parsed['green'] == green, f"绿色期望 {green}, 实际 {parsed['green']}"
        assert parsed['blue'] == blue, f"蓝色期望 {blue}, 实际 {parsed['blue']}"
        assert parsed['alpha'] == alpha, f"透明度期望 {alpha}, 实际 {parsed['alpha']}"

    print("✅ 颜色调整参数范围测试通过")

def test_layer_priority_and_padding():
    """测试图层优先级和外边框"""
    print("\n=== 测试图层优先级和外边框 ===")

    test_cases = [
        (1, 0),      # 默认值
        (5, 2),      # 常用值
        (100, 50),   # 最大值
        (10, 1),     # 小整数外边框
    ]

    for priority, padding in test_cases:
        path = format_dci_path(
            256, "normal", "light", 1.0, "webp",
            priority=priority, padding=padding
        )
        print(f"优先级:{priority}, 外边框:{padding} -> {path}")

        # 验证解析
        reader = DCIReader()
        filename = path.split('/')[-1]
        parsed = reader._parse_layer_filename(filename)

        assert parsed['priority'] == priority, f"优先级期望 {priority}, 实际 {parsed['priority']}"
        assert parsed['padding'] == padding, f"外边框期望 {padding}, 实际 {parsed['padding']}"

    print("✅ 图层优先级和外边框测试通过")

def main():
    """运行所有测试"""
    print("开始测试DCI图层系统功能...\n")

    try:
        test_format_dci_path()
        test_layer_filename_parsing()
        test_palette_mapping()
        test_color_adjustment_ranges()
        test_layer_priority_and_padding()

        print("\n🎉 所有测试通过！DCI图层系统功能正常。")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
