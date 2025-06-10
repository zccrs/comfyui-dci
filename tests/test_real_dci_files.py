#!/usr/bin/env python3
"""
测试真实DCI文件的解析和处理
使用 /home/zccrs/projects/deepin-desktop-theme/bloom/dsg-icons/bloom 中的真实DCI文件
"""

import os
import sys
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from py.dci_reader import DCIReader
from py.utils.ui_utils import format_dci_path

class TestRealDCIFiles(unittest.TestCase):
    """测试真实DCI文件的解析和处理"""

    def setUp(self):
        """设置测试环境"""
        self.dci_dir = Path("/home/zccrs/projects/deepin-desktop-theme/bloom/dsg-icons/bloom")

        # 检查DCI目录是否存在
        if not self.dci_dir.exists():
            self.skipTest(f"DCI目录不存在: {self.dci_dir}")

    def test_dci_directory_exists(self):
        """测试DCI目录是否存在且包含文件"""
        self.assertTrue(self.dci_dir.exists(), "DCI目录应该存在")

        dci_files = list(self.dci_dir.glob("*.dci"))
        self.assertGreater(len(dci_files), 0, "应该包含DCI文件")
        print(f"找到 {len(dci_files)} 个DCI文件")

    def test_read_simple_dci_files(self):
        """测试读取简单的DCI文件"""
        # 选择一些相对简单的DCI文件进行测试
        test_files = [
            "gedit.dci",
            "kate.dci",
            "folder.dci",
            "computer.dci",
            "empty.dci"
        ]

        successful_reads = 0
        for filename in test_files:
            file_path = self.dci_dir / filename
            if file_path.exists():
                try:
                    print(f"\n测试文件: {filename}")
                    reader = DCIReader(str(file_path))
                    success = reader.read()

                    if success:
                        # 验证基本结构
                        self.assertIsInstance(reader.files, list, f"{filename} 应该有files列表")
                        self.assertIsInstance(reader.directory_structure, dict, f"{filename} 应该有directory_structure字典")

                        # 打印基本信息
                        print(f"  文件数量: {len(reader.files)}")
                        print(f"  目录结构: {len(reader.directory_structure)} 个目录")

                        # 获取图像信息
                        images = reader.get_icon_images()
                        print(f"  图像数量: {len(images)}")

                        # 检查前几个图像
                        for i, img_info in enumerate(images[:3]):
                            print(f"  图像 {i}: 尺寸={img_info.get('size', 'unknown')}, 状态={img_info.get('state', 'unknown')}")

                        successful_reads += 1
                    else:
                        print(f"  读取失败")

                except Exception as e:
                    print(f"  读取异常: {e}")
                    # 不让单个文件失败影响整个测试
                    continue
            else:
                print(f"文件不存在: {filename}")

        print(f"\n成功读取 {successful_reads}/{len(test_files)} 个文件")
        self.assertGreater(successful_reads, 0, "至少应该成功读取一个文件")

    def test_layer_filename_parsing(self):
        """测试图层文件名解析功能"""
        # 创建一个DCIReader实例来测试解析方法
        reader = DCIReader()

        # 测试各种图层文件名格式
        test_cases = [
            # 简单格式（真实DCI文件中最常见）
            ("1.webp", {
                'priority': 1,
                'padding': 0,
                'palette': -1,
                'format': 'webp'
            }),
            # 完整格式
            ("1.0p.-1.0_0_0_0_0_0_0.png", {
                'priority': 1,
                'padding': 0,
                'palette': -1,
                'hue': 0,
                'saturation': 0,
                'brightness': 0,
                'red': 0,
                'green': 0,
                'blue': 0,
                'alpha': 0,
                'format': 'png'
            }),
            # 带颜色调整的格式
            ("3.7p.3.0_0_-10_0_0_0_0.png", {
                'priority': 3,
                'padding': 7,
                'palette': 3,
                'hue': 0,
                'saturation': 0,
                'brightness': -10,
                'red': 0,
                'green': 0,
                'blue': 0,
                'alpha': 0,
                'format': 'png'
            }),
            # Alpha8格式
            ("1.7p.3.0_0_0_0_0_0_0.png.alpha8", {
                'priority': 1,
                'padding': 7,
                'palette': 3,
                'hue': 0,
                'saturation': 0,
                'brightness': 0,
                'red': 0,
                'green': 0,
                'blue': 0,
                'alpha': 0,
                'format': 'png',
                'is_alpha8': True
            })
        ]

        for filename, expected in test_cases:
            print(f"\n测试文件名: {filename}")
            parsed = reader._parse_layer_filename(filename)

            for key, value in expected.items():
                self.assertEqual(parsed.get(key), value,
                               f"文件名 {filename} 的 {key} 应该是 {value}, 实际是 {parsed.get(key)}")

            print(f"  解析结果: {parsed}")

    def test_format_dci_path_consistency(self):
        """测试DCI路径格式化的一致性"""
        # 测试各种参数组合
        test_cases = [
            {
                'size': 48,
                'state': 'normal',
                'tone': 'light',
                'scale': 1.0,
                'format_type': 'png',
                'priority': 1,
                'padding': 0,
                'palette': -1,
                'expected_pattern': '1.0p.-1'
            },
            {
                'size': 48,
                'state': 'normal',
                'tone': 'light',
                'scale': 1.0,
                'format_type': 'png',
                'priority': 3,
                'padding': 7,
                'palette': 3,
                'hue': 0,
                'saturation': 0,
                'brightness': -10,
                'red': 0,
                'green': 0,
                'blue': 0,
                'alpha': 0,
                'expected_pattern': '3.7p.3.0_0_-10_0_0_0_0'
            }
        ]

        for case in test_cases:
            expected_pattern = case.pop('expected_pattern')
            result = format_dci_path(**case)

            print(f"\n参数: {case}")
            print(f"生成路径: {result}")
            print(f"期望包含: {expected_pattern}")

            self.assertIn(expected_pattern, result,
                         f"生成的路径应该包含 {expected_pattern}")

    def test_complex_dci_files(self):
        """测试复杂的DCI文件"""
        # 选择一些可能包含多图层的复杂文件
        complex_files = [
            "dde-file-manager.dci",
            "deepin-system-monitor.dci",
            "com.apps.firefox.dci",
            "google-chrome.dci",
            "thunderbird.dci"
        ]

        for filename in complex_files:
            file_path = self.dci_dir / filename
            if file_path.exists():
                try:
                    print(f"\n分析复杂文件: {filename}")
                    reader = DCIReader(str(file_path))
                    success = reader.read()

                    if success:
                        images = reader.get_icon_images()
                        print(f"  图像数量: {len(images)}")

                        # 分析图层类型
                        layer_types = {}
                        alpha8_count = 0

                        for img_info in images:
                            format_type = img_info.get('format', 'unknown')
                            if img_info.get('is_alpha8', False):
                                alpha8_count += 1
                            layer_types[format_type] = layer_types.get(format_type, 0) + 1

                        print(f"  格式分布: {layer_types}")
                        print(f"  Alpha8图层: {alpha8_count}")

                        # 检查目录结构
                        print(f"  目录数量: {len(reader.directory_structure)}")
                        for dir_path in list(reader.directory_structure.keys())[:3]:
                            file_count = len(reader.directory_structure[dir_path])
                            print(f"    {dir_path}: {file_count} 个文件")
                    else:
                        print(f"  读取失败")

                except Exception as e:
                    print(f"  分析失败: {e}")
                    continue
            else:
                print(f"文件不存在: {filename}")

    def test_file_size_analysis(self):
        """分析DCI文件大小分布"""
        dci_files = list(self.dci_dir.glob("*.dci"))

        sizes = []
        for file_path in dci_files:
            size = file_path.stat().st_size
            sizes.append((file_path.name, size))

        # 按大小排序
        sizes.sort(key=lambda x: x[1])

        print(f"\n文件大小分析 (共{len(sizes)}个文件):")
        print("最小的5个文件:")
        for name, size in sizes[:5]:
            print(f"  {name}: {size:,} bytes")

        print("\n最大的5个文件:")
        for name, size in sizes[-5:]:
            print(f"  {name}: {size:,} bytes")

        # 计算统计信息
        total_size = sum(size for _, size in sizes)
        avg_size = total_size / len(sizes)

        print(f"\n统计信息:")
        print(f"  总大小: {total_size:,} bytes")
        print(f"  平均大小: {avg_size:,.0f} bytes")
        print(f"  最小: {sizes[0][1]:,} bytes")
        print(f"  最大: {sizes[-1][1]:,} bytes")

    def test_specific_layer_patterns(self):
        """测试特定的图层模式"""
        # 选择一个中等大小的文件进行详细分析
        test_file = "deepin-calculator.dci"
        file_path = self.dci_dir / test_file

        if file_path.exists():
            try:
                print(f"\n详细分析文件: {test_file}")
                reader = DCIReader(str(file_path))
                success = reader.read()

                if success:
                    images = reader.get_icon_images()
                    print(f"总图像数量: {len(images)}")

                    # 按尺寸分组
                    size_groups = {}
                    for img_info in images:
                        size = img_info.get('size', 0)
                        if size not in size_groups:
                            size_groups[size] = []
                        size_groups[size].append(img_info)

                    print(f"尺寸分组:")
                    for size in sorted(size_groups.keys()):
                        count = len(size_groups[size])
                        print(f"  {size}px: {count} 个图像")

                        # 显示前几个图像的详细信息
                        for i, img_info in enumerate(size_groups[size][:2]):
                            print(f"    图像 {i}: 状态={img_info.get('state', 'unknown')}, "
                                  f"色调={img_info.get('tone', 'unknown')}, "
                                  f"缩放={img_info.get('scale', 'unknown')}")
                else:
                    print(f"读取失败")
            except Exception as e:
                print(f"分析失败: {e}")
        else:
            print(f"测试文件不存在: {test_file}")

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
