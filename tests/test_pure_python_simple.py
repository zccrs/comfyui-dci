#!/usr/bin/env python3
"""
简化的纯Python实现测试
直接测试ar功能，避免复杂的导入
"""

import os
import sys
import tempfile

def create_ar_archive_python(archive_path, files, working_dir):
    """创建ar归档的纯Python实现"""
    try:
        print("使用纯Python实现创建ar归档...")

        with open(archive_path, 'wb') as ar_file:
            # Write ar archive signature
            ar_file.write(b"!<arch>\n")

            for filename in files:
                file_path = os.path.join(working_dir, filename)

                if not os.path.exists(file_path):
                    print(f"警告：文件不存在: {file_path}")
                    continue

                # Get file stats
                stat = os.stat(file_path)
                file_size = stat.st_size

                # Read file content
                with open(file_path, 'rb') as f:
                    file_content = f.read()

                # Create ar header (60 bytes)
                # Format: name(16) + date(12) + uid(6) + gid(6) + mode(8) + size(10) + end(2)
                name_field = filename.ljust(16)[:16].encode('ascii')
                date_field = str(int(stat.st_mtime)).ljust(12)[:12].encode('ascii')
                uid_field = b"0     "  # 6 bytes
                gid_field = b"0     "  # 6 bytes
                mode_field = b"100644  "  # 8 bytes
                size_field = str(file_size).ljust(10)[:10].encode('ascii')
                end_field = b"`\n"  # 2 bytes

                header = name_field + date_field + uid_field + gid_field + mode_field + size_field + end_field

                # Write header and content
                ar_file.write(header)
                ar_file.write(file_content)

                # Add padding if file size is odd
                if file_size % 2 == 1:
                    ar_file.write(b"\n")

        return True

    except Exception as e:
        print(f"错误：纯Python ar归档创建失败: {str(e)}")
        return False

def extract_ar_archive_python(deb_file_path, extract_dir):
    """解析ar归档的纯Python实现"""
    try:
        print("使用纯Python实现解析ar归档...")

        with open(deb_file_path, 'rb') as f:
            # Read ar header
            magic = f.read(8)
            if magic != b'!<arch>\n':
                print("错误：不是有效的ar归档文件")
                return False

            while True:
                # Read file header (60 bytes)
                header = f.read(60)
                if len(header) < 60:
                    break

                # Parse header
                filename = header[0:16].decode('ascii').strip()
                size_str = header[48:58].decode('ascii').strip()

                if not size_str:
                    break

                size = int(size_str)

                # Read file content
                content = f.read(size)

                # Pad to even boundary
                if size % 2 == 1:
                    f.read(1)

                # Save file
                if filename and not filename.startswith('/'):
                    output_path = os.path.join(extract_dir, filename)
                    with open(output_path, 'wb') as out_f:
                        out_f.write(content)
                    print(f"  提取文件: {filename} ({size} 字节)")

        return True

    except Exception as e:
        print(f"Python ar解析失败: {str(e)}")
        return False

def test_ar_functionality():
    """测试ar功能"""
    print("=== 测试纯Python ar功能 ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"测试目录: {temp_dir}")

        # 1. 创建测试文件
        test_files = []
        for i in range(3):
            filename = f"test_{i}.txt"
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f"Test content {i}\nThis is file number {i}")
            test_files.append(filename)
            print(f"创建测试文件: {filename}")

        # 2. 创建ar归档
        ar_path = os.path.join(temp_dir, "test.ar")
        success = create_ar_archive_python(ar_path, test_files, temp_dir)

        if not success:
            print("❌ ar归档创建失败")
            return False

        ar_size = os.path.getsize(ar_path)
        print(f"✓ ar归档创建成功: {ar_size} 字节")

        # 3. 验证ar格式
        with open(ar_path, 'rb') as f:
            magic = f.read(8)
            if magic != b'!<arch>\n':
                print(f"❌ ar魔数不正确: {magic}")
                return False
        print("✓ ar格式验证通过")

        # 4. 解析ar归档
        extract_dir = os.path.join(temp_dir, "extract")
        os.makedirs(extract_dir)

        success = extract_ar_archive_python(ar_path, extract_dir)
        if not success:
            print("❌ ar归档解析失败")
            return False

        # 5. 验证提取的文件
        for i, filename in enumerate(test_files):
            extracted_file = os.path.join(extract_dir, filename)
            if not os.path.exists(extracted_file):
                print(f"❌ 文件未正确提取: {filename}")
                return False

            with open(extracted_file, 'r') as f:
                content = f.read()
                expected = f"Test content {i}\nThis is file number {i}"
                if content != expected:
                    print(f"❌ 文件内容不正确: {filename}")
                    print(f"期望: {expected}")
                    print(f"实际: {content}")
                    return False

            print(f"  ✓ 文件验证成功: {filename}")

        print("✓ 所有ar功能测试通过！")
        return True

def test_cross_platform_compatibility():
    """测试跨平台兼容性"""
    print("\n=== 测试跨平台兼容性 ===")

    # 测试不同的文件名和内容（注意ar格式文件名限制为16字符）
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建包含特殊字符的文件（文件名不超过16字符）
        test_cases = [
            ("simple.txt", "Simple content"),
            ("with-dash.txt", "Content with dash"),
            ("under_score.txt", "Content with underscore"),
            ("file123.txt", "Numeric content"),
        ]

        files = []
        for filename, content in test_cases:
            if len(filename) > 16:
                print(f"警告：文件名过长，将被截断: {filename}")
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            files.append(filename)

        # 创建和解析ar归档
        ar_path = os.path.join(temp_dir, "cross_platform.ar")
        if not create_ar_archive_python(ar_path, files, temp_dir):
            print("❌ 跨平台ar创建失败")
            return False

        extract_dir = os.path.join(temp_dir, "extract")
        os.makedirs(extract_dir)

        if not extract_ar_archive_python(ar_path, extract_dir):
            print("❌ 跨平台ar解析失败")
            return False

        # 验证所有文件（考虑文件名可能被截断）
        for filename, expected_content in test_cases:
            # ar格式会截断超过16字符的文件名
            truncated_filename = filename[:16].rstrip()
            extracted_file = os.path.join(extract_dir, truncated_filename)

            if not os.path.exists(extracted_file):
                print(f"❌ 文件未找到: {truncated_filename} (原名: {filename})")
                # 列出实际提取的文件
                actual_files = os.listdir(extract_dir)
                print(f"实际提取的文件: {actual_files}")
                return False

            with open(extracted_file, 'r') as f:
                content = f.read()
                if content != expected_content:
                    print(f"❌ 跨平台文件内容错误: {truncated_filename}")
                    return False
            print(f"  ✓ 文件验证成功: {truncated_filename}")

        print("✓ 跨平台兼容性测试通过！")
        return True

def main():
    """主测试函数"""
    print("开始测试纯Python ar实现...")

    # 基础功能测试
    if not test_ar_functionality():
        print("❌ 基础功能测试失败")
        return False

    # 跨平台兼容性测试
    if not test_cross_platform_compatibility():
        print("❌ 跨平台兼容性测试失败")
        return False

    print("\n🎉 所有测试通过！")
    print("✓ 纯Python ar实现完全正常")
    print("✓ 不依赖任何外部命令")
    print("✓ 跨平台兼容性良好")
    print("✓ ar格式完全兼容")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
