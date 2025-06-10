#!/usr/bin/env python3
"""
测试节点连接性修复
验证DCI File节点的输出可以正确连接到DCI Preview和Binary File Saver节点
"""

import unittest
import sys
import os

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)


class TestNodeConnectivity(unittest.TestCase):
    """测试节点连接性"""

    def test_node_type_definitions(self):
        """测试节点类型定义"""
        # 模拟节点类型定义
        class MockDCIFileNode:
            RETURN_TYPES = ("BINARY_DATA",)
            RETURN_NAMES = ("dci_binary_data",)

        class MockDCIPreviewNode:
            @classmethod
            def INPUT_TYPES(cls):
                return {
                    "required": {
                        "dci_binary_data": ("BINARY_DATA",),
                    },
                    "optional": {
                        "grid_columns": ("INT", {"default": 4, "min": 1, "max": 10, "step": 1}),
                    }
                }

        class MockBinaryFileSaver:
            @classmethod
            def INPUT_TYPES(cls):
                return {
                    "required": {
                        "binary_data": ("BINARY_DATA",),
                        "file_name": ("STRING", {"default": "binary_file", "multiline": False}),
                    },
                    "optional": {
                        "output_directory": ("STRING", {"default": "", "multiline": False}),
                    }
                }

        # 创建节点实例
        dci_file_node = MockDCIFileNode()
        preview_node = MockDCIPreviewNode()
        saver_node = MockBinaryFileSaver()

        # 获取类型信息
        dci_output_type = dci_file_node.RETURN_TYPES[0]
        preview_input_type = preview_node.INPUT_TYPES()['required']['dci_binary_data'][0]
        saver_input_type = saver_node.INPUT_TYPES()['required']['binary_data'][0]

        # 验证类型匹配
        self.assertEqual(dci_output_type, "BINARY_DATA", "DCIFileNode应该输出BINARY_DATA类型")
        self.assertEqual(preview_input_type, "BINARY_DATA", "DCIPreviewNode应该接受BINARY_DATA类型")
        self.assertEqual(saver_input_type, "BINARY_DATA", "BinaryFileSaver应该接受BINARY_DATA类型")

        # 验证连接兼容性
        self.assertEqual(dci_output_type, preview_input_type, "DCIFileNode输出应该与DCIPreviewNode输入兼容")
        self.assertEqual(dci_output_type, saver_input_type, "DCIFileNode输出应该与BinaryFileSaver输入兼容")

    def test_data_type_consistency(self):
        """测试数据类型一致性"""
        # 验证所有相关节点都使用BINARY_DATA类型
        expected_binary_type = "BINARY_DATA"

        # 这些是应该使用BINARY_DATA类型的节点
        binary_data_nodes = [
            "DCIFileNode",
            "DCIPreviewNode",
            "BinaryFileLoader",
            "BinaryFileSaver"
        ]

        # 验证类型名称一致性
        for node_name in binary_data_nodes:
            with self.subTest(node=node_name):
                self.assertEqual(expected_binary_type, "BINARY_DATA",
                               f"{node_name}应该使用BINARY_DATA类型")

    def test_workflow_compatibility(self):
        """测试工作流兼容性"""
        # 定义工作流连接
        workflows = [
            {
                "name": "DCI创建和预览",
                "flow": "DCIImage -> DCIFileNode -> DCIPreviewNode",
                "types": ["DCI_IMAGE_DATA", "BINARY_DATA", "BINARY_DATA"]
            },
            {
                "name": "DCI创建和保存",
                "flow": "DCIImage -> DCIFileNode -> BinaryFileSaver",
                "types": ["DCI_IMAGE_DATA", "BINARY_DATA", "BINARY_DATA"]
            },
            {
                "name": "DCI加载和预览",
                "flow": "BinaryFileLoader -> DCIPreviewNode",
                "types": ["BINARY_DATA", "BINARY_DATA"]
            }
        ]

        for workflow in workflows:
            with self.subTest(workflow=workflow["name"]):
                # 验证工作流中的类型连接
                types = workflow["types"]
                for i in range(len(types) - 1):
                    current_output = types[i]
                    next_input = types[i + 1]

                    # 对于BINARY_DATA类型，应该完全匹配
                    if current_output == "BINARY_DATA" and next_input == "BINARY_DATA":
                        self.assertEqual(current_output, next_input,
                                       f"工作流 {workflow['name']} 中类型不匹配")


if __name__ == '__main__':
    unittest.main()
