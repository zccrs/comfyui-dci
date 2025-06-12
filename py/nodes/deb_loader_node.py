import os
import fnmatch
import tempfile
import tarfile
import io
from PIL import Image
import torch
import numpy as np
from ..utils.file_utils import load_binary_data
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
                t("skip_symlinks"): ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("BINARY_DATA_LIST", "STRING_LIST", "IMAGE", "STRING_LIST", "STRING_LIST")
    RETURN_NAMES = (t("binary_data_list"), t("relative_paths"), t("image_list"), t("image_relative_paths"), t("skipped_files"))
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Files')}"

    def _execute(self, **kwargs):
        """Load files from deb package with filtering"""
        # Extract parameters with translation support
        # Try both translated and original parameter names for compatibility
        deb_file_path = kwargs.get(t("deb_file_path")) if t("deb_file_path") in kwargs else kwargs.get("deb_file_path", "")
        file_filter = kwargs.get(t("file_filter")) if t("file_filter") in kwargs else kwargs.get("file_filter", "*.dci")
        skip_symlinks = kwargs.get(t("skip_symlinks")) if t("skip_symlinks") in kwargs else kwargs.get("skip_symlinks", True)

        return self._execute_impl(deb_file_path, file_filter, skip_symlinks)

    def _execute_impl(self, deb_file_path="", file_filter="*.dci", skip_symlinks=True):
        """Load files from deb package with filtering"""

        # Validate deb file path
        if not deb_file_path:
            print("错误：未提供deb文件路径")
            return ([], [], [], [], [])

        # Normalize cross-platform path
        normalized_path = self._normalize_cross_platform_path(deb_file_path)

        # Check if file exists
        if not os.path.exists(normalized_path):
            print(f"错误：deb文件不存在: {normalized_path}")
            return ([], [], [], [], [])

        # Log file information
        file_size = os.path.getsize(normalized_path)
        print(f"正在解析deb文件: {normalized_path}")
        print(f"文件大小: {file_size:,} 字节 ({file_size / 1024:.1f} KB)")
        print(f"文件过滤器: {file_filter}")
        if skip_symlinks:
            print("跳过软链接: 启用")
        else:
            print("跳过软链接: 禁用")

        # Parse deb file and extract all files
        import time
        start_time = time.time()
        try:
            all_files, skipped_symlinks = self._parse_deb_file(normalized_path, skip_symlinks)
            parse_time = time.time() - start_time
            print(f"从deb包中提取 {len(all_files)} 个文件 (耗时: {parse_time:.2f}秒)")
            if skipped_symlinks:
                print(f"跳过 {len(skipped_symlinks)} 个软链接文件")
                for symlink in skipped_symlinks:
                    print(f"  ⏭️ {symlink}")
        except Exception as e:
            print(f"错误：解析deb文件失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return ([], [], [], [], [])

        # Filter files based on pattern
        filter_start_time = time.time()
        try:
            matching_files = self._filter_files(all_files, file_filter)
            filter_time = time.time() - filter_start_time
            print(f"过滤后匹配 {len(matching_files)} 个文件 (耗时: {filter_time:.3f}秒)")

            if len(matching_files) == 0:
                print("警告：没有文件匹配过滤条件")
                print("可用的文件列表:")
                for file_path in sorted(all_files.keys())[:10]:  # 只显示前10个
                    print(f"  {file_path}")
                if len(all_files) > 10:
                    print(f"  ... 还有 {len(all_files) - 10} 个文件")
        except Exception as e:
            print(f"错误：文件过滤失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return ([], [], [], [], [])

        # Process results
        binary_data_list = []
        relative_paths = []
        image_list = []
        image_relative_paths = []
        successful_loads = 0
        successful_images = 0
        total_bytes = 0

        process_start_time = time.time()
        for file_path, file_content in matching_files.items():
            try:
                if file_content is not None:
                    binary_data_list.append(file_content)
                    relative_paths.append(file_path)
                    successful_loads += 1
                    total_bytes += len(file_content)
                    print(f"  ✓ 加载成功: {file_path} ({len(file_content):,} 字节)")

                    # Try to decode as image
                    image_tensor = self._try_decode_image(file_content, file_path)
                    if image_tensor is not None:
                        image_list.append(image_tensor)
                        image_relative_paths.append(file_path)
                        successful_images += 1
                        shape = image_tensor.shape
                        print(f"    ✓ 图像解码成功: {file_path} (尺寸: {shape[1]}x{shape[0]}x{shape[2]})")
                else:
                    print(f"  ❌ 文件内容为空: {file_path}")

            except Exception as e:
                print(f"  ❌ 处理异常: {file_path} - {str(e)}")
                import traceback
                traceback.print_exc()

        process_time = time.time() - process_start_time
        total_time = time.time() - start_time

        # Summary statistics
        print(f"\n=== 处理结果摘要 ===")
        print(f"成功加载: {successful_loads}/{len(matching_files)} 个文件")
        print(f"成功解码: {successful_images} 个图像文件")
        print(f"总数据量: {total_bytes:,} 字节 ({total_bytes / 1024:.1f} KB)")
        print(f"处理时间: 解析 {parse_time:.2f}s + 过滤 {filter_time:.3f}s + 处理 {process_time:.3f}s = 总计 {total_time:.2f}s")

        if successful_loads > 0:
            avg_file_size = total_bytes / successful_loads
            print(f"平均文件大小: {avg_file_size:.0f} 字节")

        # Convert image list to ComfyUI format or empty list
        if image_list:
            # Stack all images into a batch tensor
            images_tensor = torch.stack(image_list, dim=0)
            print(f"图像批次张量形状: {images_tensor.shape}")
            return (binary_data_list, relative_paths, images_tensor, image_relative_paths, skipped_symlinks)
        else:
            return (binary_data_list, relative_paths, [], [], skipped_symlinks)

    def _normalize_cross_platform_path(self, path):
        """Normalize path for cross-platform compatibility"""
        try:
            # Handle Windows paths on Linux/Unix systems
            if os.name != 'nt' and ':' in path and '\\' in path:
                # This looks like a Windows path on a Unix system
                print(f"检测到Windows路径格式: {path}")

                # Extract filename from Windows path
                filename = os.path.basename(path.replace('\\', '/'))
                print(f"提取文件名: {filename}")

                # Search in common locations
                search_paths = [
                    '/tmp',
                    os.path.expanduser('~'),
                    os.getcwd(),
                    '/home',
                    '/var/tmp'
                ]

                for search_dir in search_paths:
                    if os.path.exists(search_dir):
                        candidate_path = os.path.join(search_dir, filename)
                        if os.path.exists(candidate_path):
                            print(f"找到文件: {candidate_path}")
                            return candidate_path

                # If not found, try the original path converted to Unix format
                unix_path = '/' + path.replace('\\', '/').replace(':', '')
                if os.path.exists(unix_path):
                    print(f"使用转换后的Unix路径: {unix_path}")
                    return unix_path

                print(f"警告：未找到对应文件，使用原始路径: {path}")
                return path
            else:
                # Normal path normalization
                return os.path.normpath(path.strip())

        except Exception as e:
            print(f"路径规范化失败: {str(e)}")
            return path

    def _parse_deb_file(self, deb_file_path, skip_symlinks=True):
        """Parse deb file and extract all files using pure Python implementation"""
        all_files = {}
        skipped_symlinks = []

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"创建临时目录: {temp_dir}")

                # Extract deb package using pure Python ar implementation
                extract_dir = os.path.join(temp_dir, "extract")
                os.makedirs(extract_dir)

                # Extract ar archive using pure Python
                print("开始解析ar归档...")
                if not self._extract_ar_archive_python(deb_file_path, extract_dir):
                    print("错误：无法解压deb包")
                    return all_files, skipped_symlinks

                # List extracted files
                extracted_files = os.listdir(extract_dir)
                print(f"ar归档解析完成，提取了 {len(extracted_files)} 个文件:")
                for filename in extracted_files:
                    file_path = os.path.join(extract_dir, filename)
                    file_size = os.path.getsize(file_path)
                    print(f"  {filename}: {file_size:,} 字节")

                # Parse control.tar.*
                control_files = [f for f in extracted_files if f.startswith("control.tar")]
                if control_files:
                    control_tar = os.path.join(extract_dir, control_files[0])
                    print(f"解析控制归档: {control_files[0]}")
                    control_file_dict, control_symlinks = self._extract_tar_files(control_tar, "control", skip_symlinks)
                    all_files.update(control_file_dict)
                    skipped_symlinks.extend(control_symlinks)
                    print(f"从control.tar中提取 {len(control_file_dict)} 个文件")
                    if control_symlinks:
                        print(f"从control.tar中跳过 {len(control_symlinks)} 个软链接")
                else:
                    print("警告：未找到control.tar文件")

                # Parse data.tar.*
                data_files_list = [f for f in extracted_files if f.startswith("data.tar")]
                if data_files_list:
                    data_tar = os.path.join(extract_dir, data_files_list[0])
                    print(f"解析数据归档: {data_files_list[0]}")
                    data_file_dict, data_symlinks = self._extract_tar_files(data_tar, "data", skip_symlinks)
                    all_files.update(data_file_dict)
                    skipped_symlinks.extend(data_symlinks)
                    print(f"从data.tar中提取 {len(data_file_dict)} 个文件")
                    if data_symlinks:
                        print(f"从data.tar中跳过 {len(data_symlinks)} 个软链接")
                else:
                    print("警告：未找到data.tar文件")

                print(f"deb包解析完成，总计提取 {len(all_files)} 个文件")

        except Exception as e:
            print(f"错误：解析deb文件失败: {str(e)}")
            import traceback
            traceback.print_exc()

        return all_files, skipped_symlinks

    def _extract_ar_archive_python(self, deb_file_path, extract_dir):
        """Extract ar archive using pure Python implementation"""
        try:
            print("使用纯Python实现解析ar归档...")
            file_count = 0
            total_extracted_size = 0

            with open(deb_file_path, 'rb') as f:
                # Read ar header
                magic = f.read(8)
                if magic != b'!<arch>\n':
                    print(f"错误：不是有效的ar归档文件，魔数: {magic}")
                    return False

                print("✓ ar归档魔数验证通过")

                while True:
                    # Read file header (60 bytes)
                    header_pos = f.tell()
                    header = f.read(60)
                    if len(header) < 60:
                        print(f"到达文件末尾，位置: {header_pos}")
                        break

                    # Parse header fields
                    filename_raw = header[0:16].decode('ascii')
                    date_field = header[16:28].decode('ascii').strip()
                    uid_field = header[28:34].decode('ascii').strip()
                    gid_field = header[34:40].decode('ascii').strip()
                    mode_field = header[40:48].decode('ascii').strip()
                    size_str = header[48:58].decode('ascii').strip()
                    end_marker = header[58:60]

                    # Clean filename
                    filename = filename_raw.strip().rstrip('/')

                    print(f"\n--- 解析文件头 #{file_count + 1} (位置: {header_pos}) ---")
                    print(f"原始文件名: '{filename_raw}' -> 清理后: '{filename}'")
                    print(f"日期: {date_field}, UID: {uid_field}, GID: {gid_field}")
                    print(f"权限: {mode_field}, 结束标记: {end_marker}")

                    if not size_str:
                        print("警告：文件大小字段为空，跳过")
                        break

                    try:
                        size = int(size_str)
                        print(f"文件大小: {size:,} 字节")
                    except ValueError:
                        print(f"错误：无效的文件大小: '{size_str}'")
                        break

                    # Read file content
                    content_pos = f.tell()
                    content = f.read(size)
                    if len(content) != size:
                        print(f"警告：读取的内容大小 ({len(content)}) 与预期不符 ({size})")

                    # Pad to even boundary
                    if size % 2 == 1:
                        padding = f.read(1)
                        print(f"读取填充字节: {padding}")

                    # Save file
                    if filename and not filename.startswith('/'):
                        output_path = os.path.join(extract_dir, filename)
                        try:
                            with open(output_path, 'wb') as out_f:
                                out_f.write(content)
                            file_count += 1
                            total_extracted_size += size
                            print(f"✓ 提取文件: {filename} ({size:,} 字节) -> {output_path}")
                        except Exception as e:
                            print(f"❌ 保存文件失败: {filename} - {str(e)}")
                    else:
                        print(f"⏭️ 跳过文件: '{filename}' (无效文件名)")

            print(f"\n=== ar归档解析完成 ===")
            print(f"提取文件数量: {file_count}")
            print(f"总提取大小: {total_extracted_size:,} 字节 ({total_extracted_size / 1024:.1f} KB)")
            return True

        except Exception as e:
            print(f"Python ar解析失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _extract_tar_files(self, tar_path, tar_type, skip_symlinks=True):
        """Extract all files from a tar archive"""
        files_dict = {}
        skipped_symlinks = []

        try:
            print(f"开始解析 {tar_type}.tar 文件: {tar_path}")

            # Determine compression type and open accordingly
            compression_type = "未压缩"
            if tar_path.endswith('.gz'):
                tar_file = tarfile.open(tar_path, 'r:gz')
                compression_type = "gzip"
            elif tar_path.endswith('.xz'):
                tar_file = tarfile.open(tar_path, 'r:xz')
                compression_type = "xz"
            elif tar_path.endswith('.bz2'):
                tar_file = tarfile.open(tar_path, 'r:bz2')
                compression_type = "bzip2"
            else:
                tar_file = tarfile.open(tar_path, 'r')

            print(f"压缩格式: {compression_type}")

            with tar_file:
                members = tar_file.getmembers()
                print(f"tar归档包含 {len(members)} 个条目")

                file_count = 0
                dir_count = 0
                symlink_count = 0
                hardlink_count = 0
                total_size = 0

                for i, member in enumerate(members):
                    print(f"\n--- 处理条目 #{i + 1}: {member.name} ---")
                    print(f"类型: ", end="")

                    if member.isfile():
                        print(f"普通文件 (大小: {member.size:,} 字节)")
                        file_count += 1
                        total_size += member.size
                    elif member.isdir():
                        print("目录")
                        dir_count += 1
                    elif member.islnk():
                        print(f"硬链接 -> {member.linkname}")
                        hardlink_count += 1
                    elif member.issym():
                        print(f"软链接 -> {member.linkname}")
                        symlink_count += 1
                    else:
                        print(f"其他类型 (tarfile类型: {member.type})")

                    print(f"权限: {oct(member.mode)}, UID: {member.uid}, GID: {member.gid}")
                    print(f"修改时间: {member.mtime}")

                    # Check if it's a symlink and should be skipped
                    if skip_symlinks and (member.islnk() or member.issym()):
                        clean_path = member.name.lstrip('./')
                        skipped_symlinks.append(clean_path)
                        if member.islnk():
                            print(f"  ⏭️ 跳过硬链接: {clean_path} -> {member.linkname}")
                        else:
                            print(f"  ⏭️ 跳过软链接: {clean_path} -> {member.linkname}")
                        continue

                    if member.isfile():
                        try:
                            print(f"  📄 开始提取文件内容...")
                            file_content = tar_file.extractfile(member).read()
                            # Use relative path without leading './'
                            clean_path = member.name.lstrip('./')
                            files_dict[clean_path] = file_content
                            print(f"  ✓ 提取成功: {clean_path} ({len(file_content):,} 字节)")
                        except Exception as e:
                            print(f"  ❌ 提取失败: {member.name} - {str(e)}")
                            files_dict[member.name.lstrip('./')] = None
                    else:
                        print(f"  ⏭️ 跳过非文件条目")

                print(f"\n=== {tar_type}.tar 解析完成 ===")
                print(f"总条目: {len(members)} (文件: {file_count}, 目录: {dir_count}, 软链接: {symlink_count}, 硬链接: {hardlink_count})")
                print(f"提取文件: {len(files_dict)} 个")
                print(f"跳过链接: {len(skipped_symlinks)} 个")
                print(f"总文件大小: {total_size:,} 字节 ({total_size / 1024:.1f} KB)")

        except Exception as e:
            print(f"错误：解析{tar_type}.tar失败: {str(e)}")
            import traceback
            traceback.print_exc()

        return files_dict, skipped_symlinks

    def _filter_files(self, all_files, file_filter):
        """Filter files based on the filter pattern"""
        matching_files = {}

        try:
            print(f"开始文件过滤，过滤器: '{file_filter}'")

            # Parse filter patterns
            patterns = [pattern.strip() for pattern in file_filter.replace(';', ',').split(',')]
            print(f"解析的过滤模式: {patterns}")

            matched_count = 0
            for file_path, file_content in all_files.items():
                # Get filename from path
                filename = os.path.basename(file_path)

                # Check if filename matches any pattern
                is_match = self._matches_filter(filename, patterns)

                if is_match:
                    matching_files[file_path] = file_content
                    matched_count += 1
                    print(f"  ✓ 匹配: {file_path} (文件名: {filename})")
                else:
                    print(f"  ❌ 不匹配: {file_path} (文件名: {filename})")

            print(f"过滤完成: {matched_count}/{len(all_files)} 个文件匹配")

        except Exception as e:
            print(f"错误：文件过滤失败: {str(e)}")
            import traceback
            traceback.print_exc()

        return matching_files

    def _matches_filter(self, filename, patterns):
        """Check if filename matches any of the filter patterns"""
        try:
            for pattern in patterns:
                if pattern and fnmatch.fnmatch(filename, pattern):
                    print(f"    ✓ 文件名 '{filename}' 匹配模式 '{pattern}'")
                    return True
            print(f"    ❌ 文件名 '{filename}' 不匹配任何模式 {patterns}")
            return False

        except Exception as e:
            print(f"警告：过滤器模式匹配失败: {str(e)}")
            return False

    def _is_image_file(self, filename):
        """Check if file is a supported image format"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.ico'}
        _, ext = os.path.splitext(filename.lower())
        is_image = ext in image_extensions
        print(f"    图像格式检查: {filename} -> 扩展名: {ext} -> 是图像: {is_image}")
        return is_image

    def _try_decode_image(self, binary_data, relative_path):
        """Try to decode binary data as an image and convert to ComfyUI format"""
        try:
            print(f"    🖼️ 尝试解码图像: {relative_path}")

            # Check if file extension suggests it's an image
            if not self._is_image_file(relative_path):
                print(f"    ⏭️ 跳过非图像文件: {relative_path}")
                return None

            print(f"    📊 图像数据大小: {len(binary_data):,} 字节")

            # Try to open image with PIL
            image_stream = io.BytesIO(binary_data)
            pil_image = Image.open(image_stream)

            original_mode = pil_image.mode
            original_size = pil_image.size
            print(f"    ✓ PIL图像加载成功: 模式={original_mode}, 尺寸={original_size}")

            # Convert to RGB if necessary (handle RGBA, grayscale, etc.)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
                print(f"    🔄 颜色模式转换: {original_mode} -> RGB")

            # Convert PIL image to numpy array
            image_array = np.array(pil_image)
            print(f"    📊 NumPy数组形状: {image_array.shape}, 数据类型: {image_array.dtype}")

            # Convert to ComfyUI format: (H, W, C) with values in [0, 1]
            image_array = image_array.astype(np.float32) / 255.0
            print(f"    🔄 数据类型转换: uint8 -> float32, 范围: [0, 255] -> [0, 1]")

            # Convert to PyTorch tensor
            image_tensor = torch.from_numpy(image_array)
            print(f"    ✓ PyTorch张量创建成功: 形状={image_tensor.shape}, 数据类型={image_tensor.dtype}")

            return image_tensor

        except Exception as e:
            # Not an image or failed to decode, silently ignore
            print(f"    ❌ 图像解码失败: {relative_path} - {str(e)}")
            return None
