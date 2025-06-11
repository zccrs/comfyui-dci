import os
import fnmatch
from collections import deque
from PIL import Image
import io
import torch
import numpy as np
from ..utils.file_utils import load_binary_data
from ..utils.i18n import t
from .base_node import BaseNode

class DirectoryLoader(BaseNode):
    """ComfyUI node for loading multiple binary files from a directory with filtering and recursive search"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("directory_path"): ("STRING", {"default": "", "multiline": False}),
                t("file_filter"): ("STRING", {"default": "*.dci", "multiline": False}),
                t("include_subdirectories"): ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("BINARY_DATA_LIST", "STRING_LIST", "IMAGE", "STRING_LIST")
    RETURN_NAMES = (t("binary_data_list"), t("relative_paths"), t("image_list"), t("image_relative_paths"))
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Files')}"

    def _execute(self, **kwargs):
        """Load multiple binary files from directory with filtering and recursive search"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        directory_path = kwargs.get(t("directory_path")) if t("directory_path") in kwargs else kwargs.get("directory_path", "")
        file_filter = kwargs.get(t("file_filter")) if t("file_filter") in kwargs else kwargs.get("file_filter", "*.dci")
        include_subdirectories = kwargs.get(t("include_subdirectories")) if t("include_subdirectories") in kwargs else kwargs.get("include_subdirectories", True)

        return self._execute_impl(directory_path, file_filter, include_subdirectories)

    def _execute_impl(self, directory_path="", file_filter="*.dci", include_subdirectories=True):
        """Load multiple binary files from directory with filtering and recursive search"""

        # Validate directory path
        if not directory_path:
            print("错误：未提供目录路径")
            return ([], [], [], [])

        # Normalize the directory path
        try:
            normalized_path = os.path.normpath(directory_path.strip())
            print(f"正在扫描目录: {normalized_path}")
        except Exception as e:
            print(f"错误：目录路径规范化失败: {str(e)}")
            return ([], [], [], [])

        # Check if directory exists
        if not os.path.exists(normalized_path):
            print(f"错误：目录不存在: {normalized_path}")
            return ([], [], [], [])

        if not os.path.isdir(normalized_path):
            print(f"错误：路径不是目录: {normalized_path}")
            return ([], [], [], [])

        # Find matching files
        try:
            matching_files = self._find_matching_files(normalized_path, file_filter, include_subdirectories)
            print(f"找到 {len(matching_files)} 个匹配的文件")
        except Exception as e:
            print(f"错误：文件搜索失败: {str(e)}")
            return ([], [], [], [])

        # Load binary data and process images
        binary_data_list = []
        relative_paths = []
        image_list = []
        image_relative_paths = []
        successful_loads = 0
        successful_images = 0

        for file_path in matching_files:
            try:
                # Calculate relative path
                relative_path = os.path.relpath(file_path, normalized_path)

                # Load binary data
                binary_data = load_binary_data(file_path)

                if binary_data is not None:
                    binary_data_list.append(binary_data)
                    relative_paths.append(relative_path)
                    successful_loads += 1
                    print(f"  ✓ 加载成功: {relative_path} ({len(binary_data)} 字节)")

                    # Try to decode as image
                    image_tensor = self._try_decode_image(binary_data, relative_path)
                    if image_tensor is not None:
                        image_list.append(image_tensor)
                        image_relative_paths.append(relative_path)
                        successful_images += 1
                        print(f"    ✓ 图像解码成功: {relative_path}")
                else:
                    print(f"  ❌ 加载失败: {relative_path}")

            except Exception as e:
                print(f"  ❌ 加载异常: {relative_path} - {str(e)}")

        print(f"成功加载 {successful_loads}/{len(matching_files)} 个文件")
        print(f"成功解码 {successful_images} 个图像文件")
        print(f"总数据量: {sum(len(data) for data in binary_data_list)} 字节")

        # Convert image list to ComfyUI format or empty list
        if image_list:
            # Stack all images into a batch tensor
            images_tensor = torch.stack(image_list, dim=0)
            return (binary_data_list, relative_paths, images_tensor, image_relative_paths)
        else:
            return (binary_data_list, relative_paths, [], [])

    def _find_matching_files(self, directory_path, file_filter, include_subdirectories):
        """Find files matching the filter pattern using breadth-first search"""
        matching_files = []

        if include_subdirectories:
            # Use breadth-first search for recursive directory traversal
            queue = deque([directory_path])

            while queue:
                current_dir = queue.popleft()

                try:
                    # Get all items in current directory
                    items = os.listdir(current_dir)

                    # Sort items for consistent ordering
                    items.sort()

                    for item in items:
                        item_path = os.path.join(current_dir, item)

                        if os.path.isfile(item_path):
                            # Check if file matches filter
                            if self._matches_filter(item, file_filter):
                                matching_files.append(item_path)
                        elif os.path.isdir(item_path):
                            # Add subdirectory to queue for breadth-first traversal
                            queue.append(item_path)

                except PermissionError:
                    print(f"警告：无权限访问目录: {current_dir}")
                except Exception as e:
                    print(f"警告：扫描目录时出错: {current_dir} - {str(e)}")
        else:
            # Only search in the specified directory (non-recursive)
            try:
                items = os.listdir(directory_path)
                items.sort()

                for item in items:
                    item_path = os.path.join(directory_path, item)

                    if os.path.isfile(item_path):
                        if self._matches_filter(item, file_filter):
                            matching_files.append(item_path)

            except PermissionError:
                print(f"错误：无权限访问目录: {directory_path}")
            except Exception as e:
                print(f"错误：扫描目录时出错: {directory_path} - {str(e)}")

        # Sort final results for consistent ordering
        matching_files.sort()
        return matching_files

    def _matches_filter(self, filename, file_filter):
        """Check if filename matches the filter pattern"""
        try:
            # Support multiple patterns separated by semicolons or commas
            patterns = [pattern.strip() for pattern in file_filter.replace(';', ',').split(',')]

            for pattern in patterns:
                if pattern and fnmatch.fnmatch(filename, pattern):
                    return True
            return False

        except Exception as e:
            print(f"警告：过滤器模式匹配失败: {file_filter} - {str(e)}")
            return False

    def _is_image_file(self, filename):
        """Check if file is a supported image format"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.ico'}
        _, ext = os.path.splitext(filename.lower())
        return ext in image_extensions

    def _try_decode_image(self, binary_data, relative_path):
        """Try to decode binary data as an image and convert to ComfyUI format"""
        try:
            # Check if file extension suggests it's an image
            if not self._is_image_file(relative_path):
                return None

            # Try to open image with PIL
            image_stream = io.BytesIO(binary_data)
            pil_image = Image.open(image_stream)

            # Convert to RGB if necessary (handle RGBA, grayscale, etc.)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # Convert PIL image to numpy array
            image_array = np.array(pil_image)

            # Convert to ComfyUI format: (H, W, C) with values in [0, 1]
            image_array = image_array.astype(np.float32) / 255.0

            # Convert to PyTorch tensor
            image_tensor = torch.from_numpy(image_array)

            return image_tensor

        except Exception as e:
            # Not an image or failed to decode, silently ignore
            return None
