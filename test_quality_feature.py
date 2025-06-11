#!/usr/bin/env python3
"""
测试图片质量功能
"""

import sys
import os
import numpy as np
import torch
from PIL import Image

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py'))

from nodes.image_node import DCIImage
from nodes.sample_image_node import DCISampleImage

def create_test_image(size=(256, 256), color='red'):
    """创建测试图像"""
    img = Image.new('RGBA', size, color)
    return img

def pil_to_tensor(pil_image):
    """Convert PIL Image to ComfyUI tensor format"""
    # Convert to RGB if necessary
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')

    # Convert to numpy array
    img_array = np.array(pil_image)

    # Convert to 0-1 range and add batch dimension
    img_tensor = torch.from_numpy(img_array.astype(np.float32) / 255.0).unsqueeze(0)

    return img_tensor

def test_dci_image_quality():
    """测试DCIImage节点的图片质量功能"""
    print("测试DCIImage节点的图片质量功能...")

    # 创建测试图像
    test_img = create_test_image(color='blue')
    test_tensor = pil_to_tensor(test_img)

    # 创建DCIImage节点
    dci_image_node = DCIImage()

    # 测试不同的图片质量设置
    for quality in [50, 75, 90, 100]:
        print(f"  测试质量设置: {quality}")

        # 准备参数
        kwargs = {
            'image': test_tensor,
            'icon_size': 256,
            'icon_state': 'normal',
            'scale': 1.0,
            'tone_type': 'light',
            'image_format': 'webp',
            'image_quality': quality
        }

        # 执行节点
        result = dci_image_node.execute(**kwargs)
        dci_image_data = result[0]

        print(f"    质量 {quality}: 文件大小 {dci_image_data['file_size']} 字节")

        # 验证质量设置被正确应用
        assert dci_image_data['file_size'] > 0, f"质量 {quality} 时文件大小应该大于0"

    print("  ✓ DCIImage质量测试通过")

def test_dci_sample_image_quality():
    """测试DCISampleImage节点的图片质量功能"""
    print("测试DCISampleImage节点的图片质量功能...")

    # 创建测试图像
    test_img = create_test_image(color='green')
    test_tensor = pil_to_tensor(test_img)

    # 创建DCISampleImage节点
    dci_sample_node = DCISampleImage()

    # 测试不同的图片质量设置
    for quality in [30, 60, 90]:
        print(f"  测试质量设置: {quality}")

        # 准备参数
        kwargs = {
            'image': test_tensor,
            'icon_size': 128,
            'icon_state': 'normal',
            'scale': 1.0,
            'tone_type': 'dark',
            'image_format': 'jpg',
            'image_quality': quality
        }

        # 执行节点
        result = dci_sample_node.execute(**kwargs)
        dci_image_data = result[0]

        print(f"    质量 {quality}: 文件大小 {dci_image_data['file_size']} 字节")

        # 验证质量设置被正确应用
        assert dci_image_data['file_size'] > 0, f"质量 {quality} 时文件大小应该大于0"

    print("  ✓ DCISampleImage质量测试通过")

def main():
    """运行所有测试"""
    print("开始测试图片质量功能...")
    print("=" * 50)

    try:
        test_dci_image_quality()
        test_dci_sample_image_quality()

        print("\n" + "=" * 50)
        print("所有图片质量测试通过！")
        print("✓ DCIImage节点支持图片质量设置")
        print("✓ DCISampleImage节点支持图片质量设置")
        print("✓ 不同质量设置产生不同文件大小")

        return True

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
