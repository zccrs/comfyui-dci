#!/usr/bin/env python3
"""
纯Python测试 - 不依赖torch或ComfyUI环境
测试DCI文件格式的核心功能
"""

import sys
import os
import unittest
from PIL import Image, ImageDraw
from io import BytesIO

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

# 导入纯Python模块
from dci_reader import DCIReader, DCIPreviewGenerator
from dci_format import DCIIconBuilder


class TestPurePythonDCI(unittest.TestCase):
    """纯Python DCI功能测试"""

    def setUp(self):
        """设置测试环境"""
        self.test_images = []

    def create_test_image(self, size=(64, 64), color='red', text='Test'):
        """创建测试图像"""
        img = Image.new('RGB', size, color=color)
        draw = ImageDraw.Draw(img)

        # 计算文本位置
        text_width = len(text) * 6  # 粗略估计
        text_height = 11
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2

        draw.text((x, y), text, fill='white')
        return img

    def test_dci_format_creation(self):
        """测试DCI格式创建"""
        print("测试DCI格式创建...")

        # 创建测试图像
        test_img = self.create_test_image(color='blue', text='Test')

        # 创建DCI构建器
        builder = DCIIconBuilder()

        # 添加图像
        builder.add_icon_image(test_img, 64, 'normal', 'light', 1.0, 'png')
        builder.add_icon_image(test_img, 64, 'normal', 'dark', 1.0, 'png')
        builder.add_icon_image(test_img, 64, 'hover', 'light', 1.0, 'png')

        # 生成DCI数据
        dci_data = builder.to_binary()

        self.assertIsInstance(dci_data, bytes)
        self.assertGreater(len(dci_data), 100)  # 应该有一定的大小

        print(f"  ✓ 创建了 {len(dci_data)} 字节的DCI数据")

    def test_dci_format_reading(self):
        """测试DCI格式读取"""
        print("测试DCI格式读取...")

        # 创建测试DCI数据
        test_img = self.create_test_image(color='green', text='Read')
        builder = DCIIconBuilder()
        builder.add_icon_image(test_img, 64, 'normal', 'light', 1.0, 'png')
        builder.add_icon_image(test_img, 64, 'normal', 'dark', 1.0, 'png')
        dci_data = builder.to_binary()

        # 读取DCI数据
        reader = DCIReader(binary_data=dci_data)
        success = reader.read()

        self.assertTrue(success)

        # 获取图像
        images = reader.get_icon_images()
        self.assertGreater(len(images), 0)

        print(f"  ✓ 成功读取了 {len(images)} 个图像")

        # 验证图像属性
        for img_info in images:
            self.assertIn('image', img_info)
            self.assertIn('size', img_info)
            self.assertIn('state', img_info)
            self.assertIn('tone', img_info)
            self.assertIn('scale', img_info)
            self.assertIsInstance(img_info['image'], Image.Image)

    def test_dci_preview_generation(self):
        """测试DCI预览生成"""
        print("测试DCI预览生成...")

        # 创建多个测试图像
        images = []
        colors = ['red', 'green', 'blue']
        states = ['normal', 'hover']
        tones = ['light', 'dark']

        builder = DCIIconBuilder()

        for i, color in enumerate(colors):
            for state in states:
                for tone in tones:
                    test_img = self.create_test_image(
                        color=color,
                        text=f'{state[0].upper()}{tone[0].upper()}'
                    )
                    builder.add_icon_image(test_img, 64, state, tone, 1.0, 'png')

        # 生成DCI数据并读取
        dci_data = builder.to_binary()
        reader = DCIReader(binary_data=dci_data)
        reader.read()
        images = reader.get_icon_images()

        # 生成预览
        generator = DCIPreviewGenerator(font_size=10)
        preview = generator.create_preview_grid(images, grid_cols=3)

        self.assertIsInstance(preview, Image.Image)
        self.assertGreater(preview.width, 0)
        self.assertGreater(preview.height, 0)

        print(f"  ✓ 生成了 {preview.width}x{preview.height} 的预览图像")

    def test_decimal_scale_support(self):
        """测试小数缩放支持"""
        print("测试小数缩放支持...")

        test_img = self.create_test_image(color='purple', text='1.5x')
        builder = DCIIconBuilder()

        # 测试小数缩放
        builder.add_icon_image(test_img, 64, 'normal', 'light', 1.5, 'png')
        builder.add_icon_image(test_img, 64, 'normal', 'light', 2.25, 'png')

        dci_data = builder.to_binary()
        reader = DCIReader(binary_data=dci_data)
        reader.read()
        images = reader.get_icon_images()

        # 验证缩放值
        scales = [img['scale'] for img in images]
        self.assertIn(1.5, scales)
        self.assertIn(2.25, scales)

        print(f"  ✓ 支持小数缩放: {scales}")

    def test_metadata_parsing(self):
        """测试元数据解析"""
        print("测试元数据解析...")

        test_img = self.create_test_image(color='orange', text='Meta')
        builder = DCIIconBuilder()

        # 添加带有不同元数据的图像
        builder.add_icon_image(test_img, 32, 'normal', 'light', 1.0, 'png')
        builder.add_icon_image(test_img, 64, 'hover', 'dark', 2.0, 'webp')
        builder.add_icon_image(test_img, 128, 'pressed', 'light', 1.5, 'png')

        dci_data = builder.to_binary()
        reader = DCIReader(binary_data=dci_data)
        reader.read()
        images = reader.get_icon_images()

        # 验证元数据
        sizes = set(img['size'] for img in images)
        states = set(img['state'] for img in images)
        tones = set(img['tone'] for img in images)
        formats = set(img['format'] for img in images)

        self.assertEqual(sizes, {32, 64, 128})
        self.assertEqual(states, {'normal', 'hover', 'pressed'})
        self.assertEqual(tones, {'light', 'dark'})
        self.assertEqual(formats, {'png', 'webp'})

        print(f"  ✓ 元数据解析正确: sizes={sizes}, states={states}")

    def test_empty_dci_handling(self):
        """测试空DCI文件处理"""
        print("测试空DCI文件处理...")

        # 创建空的DCI构建器
        builder = DCIIconBuilder()
        dci_data = builder.to_binary()

        # 读取空DCI
        reader = DCIReader(binary_data=dci_data)
        success = reader.read()

        self.assertTrue(success)

        images = reader.get_icon_images()
        self.assertEqual(len(images), 0)

        # 测试空预览生成
        generator = DCIPreviewGenerator()
        preview = generator.create_preview_grid(images)

        self.assertIsInstance(preview, Image.Image)

        print("  ✓ 正确处理空DCI文件")

    def test_large_image_handling(self):
        """测试大图像处理"""
        print("测试大图像处理...")

        # 创建较大的测试图像
        large_img = self.create_test_image(size=(512, 512), color='cyan', text='Large')
        builder = DCIIconBuilder()
        builder.add_icon_image(large_img, 512, 'normal', 'light', 1.0, 'png')

        dci_data = builder.to_binary()
        reader = DCIReader(binary_data=dci_data)
        success = reader.read()

        self.assertTrue(success)

        images = reader.get_icon_images()
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['size'], 512)

        print(f"  ✓ 成功处理 {images[0]['size']}x{images[0]['size']} 大图像")


def run_pure_python_tests():
    """运行纯Python测试"""
    print("运行纯Python DCI测试")
    print("=" * 50)

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPurePythonDCI)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_pure_python_tests()
    sys.exit(0 if success else 1)
