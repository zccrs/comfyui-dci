import os
import tempfile
import tarfile
import subprocess
import fnmatch
from PIL import Image
import io
import torch
import numpy as np
from ..utils.i18n import t
from .base_node import BaseNode

class DebLoader(BaseNode):
    """ComfyUI node for loading files from Debian packages with file filtering"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("deb_file_path"): ("STRING", {"default": "", "multiline": False}),
                t("file_filter"): ("STRING", {"default": "*.dci", "multiline": False}),
            }
        }

    RETURN_TYPES = ("BINARY_DATA_LIST", "STRING_LIST", "IMAGE", "STRING_LIST")
    RETURN_NAMES = (t("binary_data_list"), t("relative_paths"), t("image_list"), t("image_relative_paths"))
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Files')}"

    def _execute(self, **kwargs):
        """Load files from Debian package with file filtering"""
        # Extract parameters with translation support
        deb_file_path = kwargs.get(t("deb_file_path")) if t("deb_file_path") in kwargs else kwargs.get("deb_file_path", "")
        file_filter = kwargs.get(t("file_filter")) if t("file_filter") in kwargs else kwargs.get("file_filter", "*.dci")

        return self._execute_impl(deb_file_path, file_filter)

    def _execute_impl(self, deb_file_path="", file_filter="*.dci"):
        """Load files from Debian package with file filtering"""

        try:
            # Validate deb file path
            if not deb_file_path:
                print("错误：未提供deb文件路径")
                return ([], [], None, None)

            normalized_path = os.path.normpath(deb_file_path.strip())
            if not os.path.exists(normalized_path):
                print(f"错误：deb文件不存在: {normalized_path}")
                return ([], [], None, None)

            if not os.path.isfile(normalized_path):
                print(f"错误：路径不是文件: {normalized_path}")
                return ([], [], None, None)

            print(f"正在解析deb文件: {normalized_path}")

            # Parse deb file to extract all files
            all_files = self._parse_deb_file(normalized_path)
            print(f"deb文件中找到 {len(all_files)} 个文件")

            if not all_files:
                print("警告：deb文件中未找到任何文件")
                return ([], [], None, None)

            # Filter files based on pattern
            matching_files = self._filter_files(all_files, file_filter)
            print(f"过滤后匹配 {len(matching_files)} 个文件")

            if not matching_files:
                print("警告：未找到匹配过滤条件的文件")
                return ([], [], None, None)

            # Extract binary data and process images
            binary_data_list = []
            relative_paths = []
            image_list = []
            image_relative_paths = []
            successful_loads = 0
            successful_images = 0

            for file_path, file_content in matching_files.items():
                try:
                    if file_content is not None:
                        binary_data_list.append(file_content)
                        relative_paths.append(file_path)
                        successful_loads += 1
                        print(f"  ✓ 提取成功: {file_path} ({len(file_content)} 字节)")

                        # Try to decode as image
                        image_tensor = self._try_decode_image(file_content, file_path)
                        if image_tensor is not None:
                            image_list.append(image_tensor)
                            image_relative_paths.append(file_path)
                            successful_images += 1
                            print(f"    ✓ 图像解码成功: {file_path}")
                    else:
                        print(f"  ❌ 提取失败: {file_path}")

                except Exception as e:
                    print(f"  ❌ 提取异常: {file_path} - {str(e)}")

            print(f"成功提取 {successful_loads}/{len(matching_files)} 个文件")
            print(f"成功解码 {successful_images} 个图像文件")
            print(f"总数据量: {sum(len(data) for data in binary_data_list)} 字节")

            # Convert image list to ComfyUI format or None
            if image_list:
                # Stack all images into a batch tensor
                images_tensor = torch.stack(image_list, dim=0)
                return (binary_data_list, relative_paths, images_tensor, image_relative_paths)
            else:
                return (binary_data_list, relative_paths, None, None)

        except Exception as e:
            print(f"错误：deb文件解析过程中发生异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return ([], [], None, None)

    def _parse_deb_file(self, deb_file_path):
        """Parse deb file to extract all files from control.tar.* and data.tar.*"""
        all_files = {}

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract deb package using ar
                extract_dir = os.path.join(temp_dir, "extract")
                os.makedirs(extract_dir)

                # Use ar to extract deb components
                result = subprocess.run(
                    ["ar", "x", deb_file_path],
                    cwd=extract_dir,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    print(f"错误：无法解压deb包: {result.stderr}")
                    return all_files

                # Parse control.tar.*
                control_files = [f for f in os.listdir(extract_dir) if f.startswith("control.tar")]
                if control_files:
                    control_tar = os.path.join(extract_dir, control_files[0])
                    control_file_dict = self._extract_tar_files(control_tar, "control")
                    all_files.update(control_file_dict)
                    print(f"从control.tar中提取 {len(control_file_dict)} 个文件")

                # Parse data.tar.*
                data_files_list = [f for f in os.listdir(extract_dir) if f.startswith("data.tar")]
                if data_files_list:
                    data_tar = os.path.join(extract_dir, data_files_list[0])
                    data_file_dict = self._extract_tar_files(data_tar, "data")
                    all_files.update(data_file_dict)
                    print(f"从data.tar中提取 {len(data_file_dict)} 个文件")

        except Exception as e:
            print(f"错误：解析deb文件失败: {str(e)}")

        return all_files

    def _extract_tar_files(self, tar_path, tar_type):
        """Extract all files from a tar archive"""
        files_dict = {}

        try:
            # Determine compression type and open accordingly
            if tar_path.endswith('.gz'):
                tar_file = tarfile.open(tar_path, 'r:gz')
            elif tar_path.endswith('.xz'):
                tar_file = tarfile.open(tar_path, 'r:xz')
            elif tar_path.endswith('.bz2'):
                tar_file = tarfile.open(tar_path, 'r:bz2')
            else:
                tar_file = tarfile.open(tar_path, 'r')

            with tar_file:
                for member in tar_file.getmembers():
                    if member.isfile():
                        try:
                            file_content = tar_file.extractfile(member).read()
                            # Use relative path without leading './'
                            clean_path = member.name.lstrip('./')
                            files_dict[clean_path] = file_content
                        except Exception as e:
                            print(f"警告：无法提取文件 {member.name}: {str(e)}")
                            files_dict[member.name.lstrip('./')] = None

        except Exception as e:
            print(f"错误：解析{tar_type}.tar失败: {str(e)}")

        return files_dict

    def _filter_files(self, all_files, file_filter):
        """Filter files based on the filter pattern"""
        matching_files = {}

        try:
            # Parse filter patterns
            patterns = [pattern.strip() for pattern in file_filter.replace(';', ',').split(',')]

            for file_path, file_content in all_files.items():
                # Get filename from path
                filename = os.path.basename(file_path)

                # Check if filename matches any pattern
                if self._matches_filter(filename, patterns):
                    matching_files[file_path] = file_content

        except Exception as e:
            print(f"错误：文件过滤失败: {str(e)}")

        return matching_files

    def _matches_filter(self, filename, patterns):
        """Check if filename matches any of the filter patterns"""
        try:
            for pattern in patterns:
                if pattern and fnmatch.fnmatch(filename, pattern):
                    return True
            return False

        except Exception as e:
            print(f"警告：过滤器模式匹配失败: {str(e)}")
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
