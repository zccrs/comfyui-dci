import os
import tempfile
import shutil
import tarfile
import gzip
import fnmatch
import re
import struct
import time
from collections import deque
from datetime import datetime
from ..utils.file_utils import load_binary_data, ensure_directory
from ..utils.i18n import t
from .base_node import BaseNode

class DebPackager(BaseNode):
    """ComfyUI node for creating Debian packages with file filtering and directory scanning"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                t("local_directory"): ("STRING", {"default": "", "multiline": False}),
                t("file_filter"): ("STRING", {"default": "*.dci", "multiline": False}),
                t("include_subdirectories"): ("BOOLEAN", {"default": True}),
                t("install_target_path"): ("STRING", {"default": "/usr/share/dsg/icons", "multiline": False}),
                t("output_directory"): ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                t("base_deb_path"): ("STRING", {"default": "", "multiline": False}),
                t("package_name"): ("STRING", {"default": "", "multiline": False}),
                t("package_version"): ("STRING", {"default": "", "multiline": False}),
                t("maintainer_name"): ("STRING", {"default": "", "multiline": False}),
                t("maintainer_email"): ("STRING", {"default": "", "multiline": False}),
                t("package_description"): ("STRING", {"default": "", "multiline": True}),
                t("symlink_csv_path"): ("STRING", {"default": "", "multiline": False}),
                t("file_permissions"): ("STRING", {"default": "644", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING_LIST")
    RETURN_NAMES = (t("saved_deb_path"), t("file_list"))
    FUNCTION = "execute"
    CATEGORY = f"DCI/{t('Files')}"
    OUTPUT_NODE = True

    def _execute(self, **kwargs):
        """Create Debian package with file filtering and directory scanning"""
        # Extract parameters with translation support
        local_directory = kwargs.get(t("local_directory")) if t("local_directory") in kwargs else kwargs.get("local_directory", "")
        file_filter = kwargs.get(t("file_filter")) if t("file_filter") in kwargs else kwargs.get("file_filter", "*.dci")
        include_subdirectories = kwargs.get(t("include_subdirectories")) if t("include_subdirectories") in kwargs else kwargs.get("include_subdirectories", True)
        install_target_path = kwargs.get(t("install_target_path")) if t("install_target_path") in kwargs else kwargs.get("install_target_path", "/usr/share/dsg/icons")
        output_directory = kwargs.get(t("output_directory")) if t("output_directory") in kwargs else kwargs.get("output_directory", "")

        base_deb_path = kwargs.get(t("base_deb_path")) if t("base_deb_path") in kwargs else kwargs.get("base_deb_path", "")
        package_name = kwargs.get(t("package_name")) if t("package_name") in kwargs else kwargs.get("package_name", "")
        package_version = kwargs.get(t("package_version")) if t("package_version") in kwargs else kwargs.get("package_version", "")
        maintainer_name = kwargs.get(t("maintainer_name")) if t("maintainer_name") in kwargs else kwargs.get("maintainer_name", "")
        maintainer_email = kwargs.get(t("maintainer_email")) if t("maintainer_email") in kwargs else kwargs.get("maintainer_email", "")
        package_description = kwargs.get(t("package_description")) if t("package_description") in kwargs else kwargs.get("package_description", "")
        symlink_csv_path = kwargs.get(t("symlink_csv_path")) if t("symlink_csv_path") in kwargs else kwargs.get("symlink_csv_path", "")
        file_permissions = kwargs.get(t("file_permissions")) if t("file_permissions") in kwargs else kwargs.get("file_permissions", "644")

        return self._execute_impl(
            local_directory, file_filter, include_subdirectories, install_target_path, output_directory,
            base_deb_path, package_name, package_version,
            maintainer_name, maintainer_email, package_description, symlink_csv_path, file_permissions
        )

    def _execute_impl(self, local_directory="", file_filter="*.dci", include_subdirectories=True,
                     install_target_path="/usr/share/dsg/icons", output_directory="",
                     base_deb_path="", package_name="", package_version="",
                     maintainer_name="", maintainer_email="", package_description="", symlink_csv_path="", file_permissions="644"):
        """Create Debian package with file filtering and directory scanning"""

        try:
            # Validate local directory
            if not local_directory:
                print("错误：未提供本地目录路径")
                return ("错误：未提供本地目录路径", [])

            normalized_path = os.path.normpath(local_directory.strip())
            if not os.path.exists(normalized_path):
                print(f"错误：本地目录不存在: {normalized_path}")
                return (f"错误：本地目录不存在: {normalized_path}", [])

            if not os.path.isdir(normalized_path):
                print(f"错误：路径不是目录: {normalized_path}")
                return (f"错误：路径不是目录: {normalized_path}", [])

            # Validate and prepare output directory
            if not output_directory:
                # Default to ComfyUI output directory
                output_directory = os.path.join(os.getcwd(), "output")

            output_directory = os.path.normpath(output_directory.strip())
            if not os.path.exists(output_directory):
                try:
                    os.makedirs(output_directory, exist_ok=True)
                    print(f"创建输出目录: {output_directory}")
                except Exception as e:
                    error_msg = f"错误：无法创建输出目录 {output_directory}: {str(e)}"
                    print(error_msg)
                    return (error_msg, [])

            # Find matching files
            matching_files = self._find_matching_files(normalized_path, file_filter, include_subdirectories)
            print(f"找到 {len(matching_files)} 个匹配的文件")

            if not matching_files:
                print("警告：未找到匹配的文件")
                return ("警告：未找到匹配的文件", [])

            # Parse symlink CSV if provided
            symlink_mappings = {}
            if symlink_csv_path and os.path.exists(symlink_csv_path):
                print(f"解析软链接表格: {symlink_csv_path}")
                symlink_mappings = self._parse_symlink_csv(symlink_csv_path)
                print(f"软链接映射: {len(symlink_mappings)} 项")

            # Parse base deb if provided to get control info
            base_control_info = {}
            if base_deb_path and os.path.exists(base_deb_path):
                print(f"解析基础deb包: {base_deb_path}")
                base_control_info, _ = self._parse_base_deb(base_deb_path)
                print(f"基础包控制信息: {len(base_control_info)} 项")

            # Prepare package metadata with version auto-increment
            pkg_info = self._prepare_package_info(
                base_control_info, package_name, package_version,
                maintainer_name, maintainer_email, package_description
            )

            # Generate deb filename
            deb_filename = f"{pkg_info['Package']}_{pkg_info['Version']}_all.deb"
            deb_output_path = os.path.join(output_directory, deb_filename)

            # Create temporary working directory
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"创建临时工作目录: {temp_dir}")

                # Create deb package
                success, file_list = self._create_deb_package(
                    temp_dir, matching_files, normalized_path, install_target_path,
                    pkg_info, deb_output_path, symlink_mappings, file_permissions
                )

                if success:
                    print(f"成功创建deb包: {deb_output_path}")
                    print(f"包含文件: {len(file_list)} 个")
                    return (deb_output_path, file_list)
                else:
                    error_msg = "错误：deb包创建失败"
                    print(error_msg)
                    return (error_msg, [])

        except Exception as e:
            error_msg = f"错误：deb打包过程中发生异常: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return (error_msg, [])

    def _find_matching_files(self, directory_path, file_filter, include_subdirectories):
        """Find files matching the filter pattern using breadth-first search"""
        matching_files = []

        if include_subdirectories:
            # Use breadth-first search for recursive directory traversal
            queue = deque([directory_path])

            while queue:
                current_dir = queue.popleft()

                try:
                    items = os.listdir(current_dir)
                    items.sort()

                    for item in items:
                        item_path = os.path.join(current_dir, item)

                        if os.path.isfile(item_path):
                            if self._matches_filter(item, file_filter):
                                matching_files.append(item_path)
                        elif os.path.isdir(item_path):
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

        matching_files.sort()
        return matching_files

    def _matches_filter(self, filename, file_filter):
        """Check if filename matches the filter pattern"""
        try:
            patterns = [pattern.strip() for pattern in file_filter.replace(';', ',').split(',')]

            for pattern in patterns:
                if pattern and fnmatch.fnmatch(filename, pattern):
                    return True
            return False

        except Exception as e:
            print(f"警告：过滤器模式匹配失败: {file_filter} - {str(e)}")
            return False

    def _create_ar_archive_python(self, archive_path, files, working_dir):
        """Create ar archive using pure Python implementation"""
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

    def _parse_base_deb(self, deb_path):
        """Parse base deb package to extract control info using pure Python"""
        control_info = {}
        data_files = {}  # Not used anymore, but kept for compatibility

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract deb package using pure Python ar implementation
                extract_dir = os.path.join(temp_dir, "extract")
                os.makedirs(extract_dir)

                # Use pure Python ar extraction
                if not self._extract_ar_archive_python(deb_path, extract_dir):
                    print("错误：无法解压基础deb包")
                    return control_info, data_files

                # Parse control.tar.*
                control_files = [f for f in os.listdir(extract_dir) if f.startswith("control.tar")]
                if control_files:
                    control_tar = os.path.join(extract_dir, control_files[0])
                    control_info = self._parse_control_tar(control_tar)

        except Exception as e:
            print(f"错误：解析基础deb包失败: {str(e)}")

        return control_info, data_files

    def _extract_ar_archive_python(self, deb_file_path, extract_dir):
        """Extract ar archive using pure Python implementation"""
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

    def _parse_control_tar(self, control_tar_path):
        """Parse control.tar.* to extract control file content"""
        control_info = {}

        try:
            # Determine compression type and open accordingly
            if control_tar_path.endswith('.gz'):
                tar_file = tarfile.open(control_tar_path, 'r:gz')
            elif control_tar_path.endswith('.xz'):
                tar_file = tarfile.open(control_tar_path, 'r:xz')
            elif control_tar_path.endswith('.bz2'):
                tar_file = tarfile.open(control_tar_path, 'r:bz2')
            else:
                tar_file = tarfile.open(control_tar_path, 'r')

            with tar_file:
                try:
                    control_member = tar_file.getmember('./control')
                    control_content = tar_file.extractfile(control_member).read().decode('utf-8')
                    control_info = self._parse_control_content(control_content)
                except KeyError:
                    print("警告：control文件不存在于control.tar中")

        except Exception as e:
            print(f"警告：解析control.tar失败: {str(e)}")

        return control_info

    def _parse_control_content(self, control_content):
        """Parse control file content to extract package metadata"""
        control_info = {}

        for line in control_content.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                control_info[key.strip()] = value.strip()

        return control_info

    def _increment_version(self, version):
        """Increment the last number in a version string"""
        if not version:
            return "1.0.0"

        # Match version pattern like 1.2.3, 1.2.3-4, 1.2.3+build1, etc.
        # We want to increment the last numeric part
        version_pattern = r'^(.*)(\d+)(.*)$'
        match = re.search(version_pattern, version)

        if match:
            prefix = match.group(1)
            number = int(match.group(2))
            suffix = match.group(3)

            # Increment the number
            new_number = number + 1
            new_version = f"{prefix}{new_number}{suffix}"
            print(f"版本号递增: {version} -> {new_version}")
            return new_version
        else:
            # If no number found, append .1
            new_version = f"{version}.1"
            print(f"版本号递增: {version} -> {new_version}")
            return new_version

    def _prepare_package_info(self, base_control_info, package_name, package_version,
                            maintainer_name, maintainer_email, package_description):
        """Prepare package metadata, using base info as fallback"""
        pkg_info = {}

        # Use provided values or fallback to base info or defaults
        pkg_info['Package'] = package_name or base_control_info.get('Package', 'dci-icons')

        # Handle version with auto-increment
        if package_version:
            pkg_info['Version'] = package_version
        elif base_control_info.get('Version'):
            # Auto-increment base version
            pkg_info['Version'] = self._increment_version(base_control_info.get('Version'))
        else:
            pkg_info['Version'] = '1.0.0'

        # Handle maintainer field
        if maintainer_name and maintainer_email:
            pkg_info['Maintainer'] = f"{maintainer_name} <{maintainer_email}>"
        elif maintainer_name:
            pkg_info['Maintainer'] = maintainer_name
        else:
            pkg_info['Maintainer'] = base_control_info.get('Maintainer', 'Unknown <unknown@example.com>')

        pkg_info['Description'] = package_description or base_control_info.get('Description', 'DCI Icons Package')

        # Copy other fields from base control info
        for key, value in base_control_info.items():
            if key not in pkg_info:
                pkg_info[key] = value

        # Set default values for required fields if not present
        if 'Architecture' not in pkg_info:
            pkg_info['Architecture'] = 'all'
        if 'Priority' not in pkg_info:
            pkg_info['Priority'] = 'optional'
        if 'Section' not in pkg_info:
            pkg_info['Section'] = 'graphics'

        return pkg_info

    def _create_deb_package(self, temp_dir, matching_files, source_dir, install_target_path,
                          pkg_info, output_deb_path, symlink_mappings=None, file_permissions="644"):
        """Create the actual deb package and save to specified path"""
        try:
            # Create package structure
            pkg_dir = os.path.join(temp_dir, "package")
            control_dir = os.path.join(pkg_dir, "DEBIAN")
            data_dir = os.path.join(pkg_dir, "data")

            os.makedirs(control_dir)
            os.makedirs(data_dir)

            # Create control file
            control_file_path = os.path.join(control_dir, "control")
            self._create_control_file(control_file_path, pkg_info)

            # Copy matching files to target location
            target_base = os.path.join(data_dir, install_target_path.lstrip('/'))
            os.makedirs(target_base, exist_ok=True)

            file_list = []
            symlink_info = []  # Store symlink information for tar creation

            for file_path in matching_files:
                relative_path = os.path.relpath(file_path, source_dir)
                target_file_path = os.path.join(target_base, relative_path)
                target_file_dir = os.path.dirname(target_file_path)

                if target_file_dir:
                    os.makedirs(target_file_dir, exist_ok=True)

                shutil.copy2(file_path, target_file_path)

                # Add to file list
                deb_internal_path = os.path.join(install_target_path, relative_path).replace('\\', '/')
                file_list.append(deb_internal_path)

                # Collect symlink information if mappings exist
                if symlink_mappings:
                    symlinks_created = self._collect_symlink_info(
                        file_path, relative_path, install_target_path, symlink_mappings
                    )
                    symlink_info.extend(symlinks_created)
                    file_list.extend([info['deb_path'] for info in symlinks_created])

            # Create control.tar.gz
            control_tar_path = os.path.join(temp_dir, "control.tar.gz")
            self._create_control_tar(control_tar_path, control_dir)

            # Parse file permissions
            try:
                file_mode = int(file_permissions, 8) if file_permissions else 0o644
                print(f"设置文件权限: {oct(file_mode)} ({file_permissions})")
            except ValueError:
                print(f"警告：无效的权限值 '{file_permissions}'，使用默认值 644")
                file_mode = 0o644

            # Create data.tar.gz with symlinks
            data_tar_path = os.path.join(temp_dir, "data.tar.gz")
            self._create_data_tar_with_symlinks(data_tar_path, data_dir, symlink_info, file_mode)

            # Create debian-binary
            debian_binary_path = os.path.join(temp_dir, "debian-binary")
            with open(debian_binary_path, 'w') as f:
                f.write("2.0\n")

            # Create final deb package using pure Python ar implementation
            temp_deb_path = os.path.join(temp_dir, "package.deb")

            # Use pure Python implementation
            success = self._create_ar_archive_python(
                temp_deb_path,
                ["debian-binary", "control.tar.gz", "data.tar.gz"],
                temp_dir
            )
            if not success:
                return False, []

            # Copy the created deb file to output location
            shutil.copy2(temp_deb_path, output_deb_path)

            # Add control files to file list
            control_files = ["./control"]
            if os.path.exists(os.path.join(control_dir, "postinst")):
                control_files.append("./postinst")
            if os.path.exists(os.path.join(control_dir, "prerm")):
                control_files.append("./prerm")
            if os.path.exists(os.path.join(control_dir, "postrm")):
                control_files.append("./postrm")

            # Combine control and data file lists
            all_files = control_files + file_list

            return True, all_files

        except Exception as e:
            print(f"错误：创建deb包失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, []

    def _create_control_file(self, control_file_path, pkg_info):
        """Create the control file with package metadata"""
        with open(control_file_path, 'w') as f:
            for key, value in pkg_info.items():
                f.write(f"{key}: {value}\n")

    def _create_control_tar(self, tar_path, control_dir):
        """Create control.tar.gz from control directory"""
        with tarfile.open(tar_path, 'w:gz') as tar:
            for item in os.listdir(control_dir):
                item_path = os.path.join(control_dir, item)
                tar.add(item_path, arcname=f"./{item}")

    def _create_data_tar(self, tar_path, data_dir):
        """Create data.tar.gz from data directory"""
        with tarfile.open(tar_path, 'w:gz') as tar:
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, data_dir)
                    tar.add(file_path, arcname=f"./{arcname}")

    def _create_data_tar_with_symlinks(self, tar_path, data_dir, symlink_info, file_mode=0o644):
        """Create data.tar.gz from data directory with symlinks"""
        with tarfile.open(tar_path, 'w:gz') as tar:
            # Add regular files with custom permissions
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, data_dir)

                    # Create TarInfo with custom permissions
                    tarinfo = tar.gettarinfo(file_path, arcname=f"./{arcname}")
                    tarinfo.mode = file_mode
                    tarinfo.uid = 0
                    tarinfo.gid = 0

                    # Add file with custom tarinfo
                    with open(file_path, 'rb') as f:
                        tar.addfile(tarinfo, f)

            # Add symlinks using tarfile API
            for symlink in symlink_info:
                try:
                    # Create a TarInfo object for the symlink
                    tarinfo = tarfile.TarInfo(name=f"./{symlink['arcname']}")
                    tarinfo.type = tarfile.SYMTYPE  # Symbolic link
                    tarinfo.linkname = symlink['target']  # Target of the symlink
                    tarinfo.size = 0
                    tarinfo.mode = file_mode  # Standard symlink permissions
                    tarinfo.uid = 0
                    tarinfo.gid = 0
                    tarinfo.mtime = int(time.time())

                    # Add the symlink to the tar archive
                    tar.addfile(tarinfo)

                    print(f"    ✓ 在tar中创建软链接: {symlink['name']} -> {symlink['target']}")

                except Exception as e:
                    print(f"    ❌ 在tar中创建软链接失败 {symlink['name']}: {str(e)}")

    def _parse_symlink_csv(self, csv_path):
        """Parse CSV file for symlink mappings"""
        import csv
        symlink_mappings = {}

        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                # 尝试自动检测分隔符
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                reader = csv.reader(csvfile, delimiter=delimiter)

                for row_num, row in enumerate(reader, 1):
                    if len(row) < 2:
                        continue

                    source_name = row[0].strip()
                    target_names_str = row[1].strip()

                    if not source_name or not target_names_str:
                        continue

                    # 解析目标名称，可能包含换行符分隔的多个名称
                    target_names = []
                    for name in target_names_str.split('\n'):
                        name = name.strip()
                        if name:
                            target_names.append(name)

                    if target_names:
                        symlink_mappings[source_name] = target_names
                        print(f"  映射: {source_name} -> {target_names}")

        except Exception as e:
            print(f"警告：解析CSV文件失败: {str(e)}")
            return {}

        return symlink_mappings

    def _collect_symlink_info(self, original_file_path, relative_path, install_target_path, symlink_mappings):
        """Collect symlink information for a file based on mappings"""
        symlinks_info = []

        # 获取文件名（不含扩展名）和扩展名
        filename = os.path.basename(original_file_path)
        name_without_ext, ext = os.path.splitext(filename)

        # 检查是否有完全匹配的映射
        if name_without_ext in symlink_mappings:
            target_names = symlink_mappings[name_without_ext]
            print(f"  为文件 {filename} 准备软链接 (完全匹配: {name_without_ext})")

            # 为每个目标名称收集软链接信息
            for target_name in target_names:
                try:
                    # 构建软链接文件名
                    symlink_filename = f"{target_name}{ext}"

                    # 计算软链接的相对路径（与源文件在同一目录）
                    symlink_relative_path = os.path.join(os.path.dirname(relative_path), symlink_filename)

                    # 计算在tar归档中的路径
                    symlink_arcname = symlink_relative_path.replace('\\', '/')

                    # 软链接目标直接使用文件名（同一目录下）
                    target_relative = filename

                    # 添加到软链接信息列表
                    symlink_info = {
                        'name': symlink_filename,
                        'arcname': symlink_arcname,
                        'target': target_relative,
                        'deb_path': os.path.join(install_target_path, symlink_relative_path).replace('\\', '/')
                    }
                    symlinks_info.append(symlink_info)

                    print(f"    ✓ 准备软链接: {symlink_filename} -> {target_relative}")

                except Exception as e:
                    print(f"    ❌ 准备软链接失败 {target_name}{ext}: {str(e)}")

        return symlinks_info
