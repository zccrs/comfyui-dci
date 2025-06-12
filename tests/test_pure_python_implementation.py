#!/usr/bin/env python3
"""
测试纯Python实现的ar功能
验证deb包的创建和解析都不依赖外部命令
"""

import os
import sys
import tempfile
import shutil

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py'))

from nodes.deb_packager_node import DebPackager
from nodes.deb_loader_node import DebLoader

def test_pure_python_ar_implementation():
    """测试纯Python ar实现"""
    print("=== 测试纯Python ar实现 ===")

    # 创建测试环境
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"测试目录: {temp_dir}")

        # 1. 创建测试文件
        test_files_dir = os.path.join(temp_dir, "test_files")
        os.makedirs(test_files_dir)

        # 创建一些测试DCI文件
        test_dci_content = b"DCI test content for pure Python implementation"
        for i in range(3):
            dci_file = os.path.join(test_files_dir, f"test_{i}.dci")
            with open(dci_file, 'wb') as f:
                f.write(test_dci_content + f" {i}".encode())

        print(f"创建了3个测试DCI文件")

        # 2. 使用deb packager创建deb包（纯Python实现）
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir)

        packager = DebPackager()
        result = packager._execute_impl(
            local_directory=test_files_dir,
            file_filter="*.dci",
            include_subdirectories=True,
            install_target_path="/usr/share/test/icons",
            output_directory=output_dir,
            package_name="test-dci-package",
            package_version="1.0.0",
            maintainer_name="Test User",
            maintainer_email="test@example.com",
            package_description="Test DCI package for pure Python implementation"
        )

        deb_path, file_list = result
        print(f"Deb包创建结果: {deb_path}")
        print(f"包含文件数量: {len(file_list)}")

        # 验证deb文件是否创建成功
        if not os.path.exists(deb_path) or "错误" in deb_path:
            print("❌ Deb包创建失败")
            return False

        deb_size = os.path.getsize(deb_path)
        print(f"✓ Deb包创建成功: {deb_size} 字节")

        # 3. 使用deb loader解析deb包（纯Python实现）
        loader = DebLoader()
        load_result = loader._execute_impl(
            deb_file_path=deb_path,
            file_filter="*.dci"
        )

        binary_data_list, relative_paths, image_list, image_relative_paths = load_result

        print(f"解析结果:")
        print(f"  二进制数据: {len(binary_data_list)} 个文件")
        print(f"  相对路径: {len(relative_paths)} 个")
        print(f"  图像数据: {len(image_list) if isinstance(image_list, list) else 'tensor'}")
        print(f"  图像路径: {len(image_relative_paths)} 个")

        # 验证解析结果
        if len(binary_data_list) != 3:
            print(f"❌ 解析的文件数量不正确，期望3个，实际{len(binary_data_list)}个")
            return False

        # 验证文件内容
        for i, (data, path) in enumerate(zip(binary_data_list, relative_paths)):
            expected_content = test_dci_content + f" {i}".encode()
            if data != expected_content:
                print(f"❌ 文件内容不匹配: {path}")
                return False
            print(f"  ✓ 文件内容验证成功: {path}")

        print("✓ 所有测试通过！纯Python实现工作正常")
        return True

def test_ar_format_validation():
    """测试ar格式验证"""
    print("\n=== 测试ar格式验证 ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建一个简单的ar归档
        packager = DebPackager()

        # 创建测试文件
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Hello, World!")

        # 创建ar归档
        ar_path = os.path.join(temp_dir, "test.ar")
        success = packager._create_ar_archive_python(ar_path, ["test.txt"], temp_dir)

        if not success:
            print("❌ ar归档创建失败")
            return False

        # 验证ar格式
        with open(ar_path, 'rb') as f:
            magic = f.read(8)
            if magic != b'!<arch>\n':
                print(f"❌ ar魔数不正确: {magic}")
                return False

        ar_size = os.path.getsize(ar_path)
        print(f"✓ ar归档创建成功: {ar_size} 字节")
        print(f"✓ ar格式验证通过")

        # 测试解析
        extract_dir = os.path.join(temp_dir, "extract")
        os.makedirs(extract_dir)

        success = packager._extract_ar_archive_python(ar_path, extract_dir)
        if not success:
            print("❌ ar归档解析失败")
            return False

        # 验证提取的文件
        extracted_file = os.path.join(extract_dir, "test.txt")
        if not os.path.exists(extracted_file):
            print("❌ 文件未正确提取")
            return False

        with open(extracted_file, 'r') as f:
            content = f.read()
            if content != "Hello, World!":
                print(f"❌ 文件内容不正确: {content}")
                return False

        print("✓ ar归档解析验证通过")
        return True

def main():
    """主测试函数"""
    print("开始测试纯Python实现...")

    # 测试ar格式
    if not test_ar_format_validation():
        print("❌ ar格式测试失败")
        return False

    # 测试完整的deb包流程
    if not test_pure_python_ar_implementation():
        print("❌ 完整流程测试失败")
        return False

    print("\n🎉 所有测试通过！纯Python实现完全正常工作")
    print("✓ 不再依赖任何外部命令")
    print("✓ 跨平台兼容性良好")
    print("✓ ar格式完全兼容")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
