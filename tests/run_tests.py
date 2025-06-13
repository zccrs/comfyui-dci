#!/usr/bin/env python3
"""
智能测试运行器 - 根据环境自动选择合适的测试
"""

import sys
import os
import subprocess
import importlib.util

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

def check_dependency(module_name):
    """检查依赖是否可用"""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except ImportError:
        return False

def detect_environment():
    """检测当前环境"""
    has_torch = check_dependency('torch')
    has_comfyui = check_dependency('folder_paths')
    has_pytest = check_dependency('pytest')

    return {
        'torch': has_torch,
        'comfyui': has_comfyui,
        'pytest': has_pytest
    }

def run_pure_python_tests():
    """运行纯Python测试"""
    print("运行纯Python测试...")

    try:
        # 直接运行纯Python测试
        from test_pure_python_only import run_pure_python_tests
        return run_pure_python_tests()
    except Exception as e:
        print(f"纯Python测试失败: {e}")
        return False

def run_pytest_tests(env_info):
    """使用pytest运行测试"""
    print("使用pytest运行测试...")

    cmd = ['python', '-m', 'pytest', '-v']

    # 根据环境添加标记
    if not env_info['torch']:
        cmd.extend(['-m', 'not requires_torch'])
    if not env_info['comfyui']:
        cmd.extend(['-m', 'not requires_comfyui'])

    # 添加测试目录
    cmd.append('tests/')

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"pytest运行失败: {e}")
        return False

def run_unittest_tests():
    """使用unittest运行基础测试"""
    print("使用unittest运行基础测试...")

    # 运行特定的测试文件
    test_files = [
        'test_pure_python_only.py',
        'test_dci_format.py',
        'test_border_color.py'
    ]

    success = True
    for test_file in test_files:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            print(f"\n运行 {test_file}...")
            try:
                result = subprocess.run([
                    sys.executable, test_path
                ], capture_output=True, text=True)

                print(result.stdout)
                if result.stderr:
                    print("错误输出:", result.stderr)

                if result.returncode != 0:
                    success = False
                    print(f"❌ {test_file} 测试失败")
                else:
                    print(f"✓ {test_file} 测试通过")
            except Exception as e:
                print(f"运行 {test_file} 时出错: {e}")
                success = False
        else:
            print(f"⚠ 测试文件 {test_file} 不存在")

    return success

def main():
    """主函数"""
    print("DCI项目智能测试运行器")
    print("=" * 50)

    # 检测环境
    env_info = detect_environment()

    print("环境检测结果:")
    print(f"  torch: {'✓' if env_info['torch'] else '✗'}")
    print(f"  ComfyUI: {'✓' if env_info['comfyui'] else '✗'}")
    print(f"  pytest: {'✓' if env_info['pytest'] else '✗'}")
    print()

    # 选择测试策略
    if env_info['pytest']:
        print("使用pytest运行测试（推荐）")
        success = run_pytest_tests(env_info)
    elif env_info['torch'] and env_info['comfyui']:
        print("ComfyUI环境，运行完整测试")
        success = run_unittest_tests()
    else:
        print("纯Python环境，运行基础测试")
        success = run_pure_python_tests()

    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
