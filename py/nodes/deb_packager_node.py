import os
import tempfile
import shutil
import tarfile
import gzip
import subprocess
import fnmatch
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
            },
            "optional": {
                t("base_deb_path"): ("STRING", {"default": "", "multiline": False}),
                t("preserve_base_files"): ("BOOLEAN", {"default": True}),
                t("package_name"): ("STRING", {"default": "", "multiline": False}),
                t("package_version"): ("STRING", {"default": "", "multiline": False}),
                t("maintainer_name"): ("STRING", {"default": "", "multiline": False}),
                t("maintainer_email"): ("STRING", {"default": "", "multiline": False}),
                t("package_description"): ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("BINARY_DATA", "STRING_LIST")
    RETURN_NAMES = (t("deb_binary_data"), t("file_list"))
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

        base_deb_path = kwargs.get(t("base_deb_path")) if t("base_deb_path") in kwargs else kwargs.get("base_deb_path", "")
        preserve_base_files = kwargs.get(t("preserve_base_files")) if t("preserve_base_files") in kwargs else kwargs.get("preserve_base_files", True)
        package_name = kwargs.get(t("package_name")) if t("package_name") in kwargs else kwargs.get("package_name", "")
        package_version = kwargs.get(t("package_version")) if t("package_version") in kwargs else kwargs.get("package_version", "")
        maintainer_name = kwargs.get(t("maintainer_name")) if t("maintainer_name") in kwargs else kwargs.get("maintainer_name", "")
        maintainer_email = kwargs.get(t("maintainer_email")) if t("maintainer_email") in kwargs else kwargs.get("maintainer_email", "")
        package_description = kwargs.get(t("package_description")) if t("package_description") in kwargs else kwargs.get("package_description", "")

        return self._execute_impl(
            local_directory, file_filter, include_subdirectories, install_target_path,
            base_deb_path, preserve_base_files, package_name, package_version,
            maintainer_name, maintainer_email, package_description
        )

    def _execute_impl(self, local_directory="", file_filter="*.dci", include_subdirectories=True,
                     install_target_path="/usr/share/dsg/icons", base_deb_path="", preserve_base_files=True,
                     package_name="", package_version="", maintainer_name="", maintainer_email="",
                     package_description=""):
        """Create Debian package with file filtering and directory scanning"""

        try:
            # Validate local directory
            if not local_directory:
                print("错误：未提供本地目录路径")
                return (None, [])

            normalized_path = os.path.normpath(local_directory.strip())
            if not os.path.exists(normalized_path):
                print(f"错误：本地目录不存在: {normalized_path}")
                return (None, [])

            if not os.path.isdir(normalized_path):
                print(f"错误：路径不是目录: {normalized_path}")
                return (None, [])

            # Find matching files
            matching_files = self._find_matching_files(normalized_path, file_filter, include_subdirectories)
            print(f"找到 {len(matching_files)} 个匹配的文件")

            if not matching_files:
                print("警告：未找到匹配的文件")
                return (None, [])

            # Parse base deb if provided
            base_control_info = {}
            base_data_files = {}

            if base_deb_path and os.path.exists(base_deb_path):
                print(f"解析基础deb包: {base_deb_path}")
                base_control_info, base_data_files = self._parse_base_deb(base_deb_path)
                print(f"基础包控制信息: {len(base_control_info)} 项")
                print(f"基础包数据文件: {len(base_data_files)} 个")

            # Prepare package metadata
            pkg_info = self._prepare_package_info(
                base_control_info, package_name, package_version,
                maintainer_name, maintainer_email, package_description
            )

            # Create temporary working directory
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"创建临时工作目录: {temp_dir}")

                # Create deb package structure
                deb_binary_data, file_list = self._create_deb_package(
                    temp_dir, matching_files, normalized_path, install_target_path,
                    base_data_files if preserve_base_files else {}, pkg_info
                )

                if deb_binary_data:
                    print(f"成功创建deb包，大小: {len(deb_binary_data)} 字节")
                    print(f"包含文件: {len(file_list)} 个")
                    return (deb_binary_data, file_list)
                else:
                    print("错误：deb包创建失败")
                    return (None, [])

        except Exception as e:
            print(f"错误：deb打包过程中发生异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return (None, [])

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

    def _parse_base_deb(self, deb_path):
        """Parse base deb package to extract control info and data files"""
        control_info = {}
        data_files = {}

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract deb package using ar
                extract_dir = os.path.join(temp_dir, "extract")
                os.makedirs(extract_dir)

                # Use ar to extract deb components
                result = subprocess.run(
                    ["ar", "x", deb_path],
                    cwd=extract_dir,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    print(f"警告：无法解压deb包: {result.stderr}")
                    return control_info, data_files

                # Parse control.tar.*
                control_files = [f for f in os.listdir(extract_dir) if f.startswith("control.tar")]
                if control_files:
                    control_tar = os.path.join(extract_dir, control_files[0])
                    control_info = self._parse_control_tar(control_tar)

                # Parse data.tar.*
                data_files_list = [f for f in os.listdir(extract_dir) if f.startswith("data.tar")]
                if data_files_list:
                    data_tar = os.path.join(extract_dir, data_files_list[0])
                    data_files = self._parse_data_tar(data_tar)

        except Exception as e:
            print(f"警告：解析基础deb包失败: {str(e)}")

        return control_info, data_files

    def _parse_control_tar(self, control_tar_path):
        """Parse control.tar.* to extract package metadata"""
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
                # Extract control file
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

    def _parse_data_tar(self, data_tar_path):
        """Parse data.tar.* to extract file list and contents"""
        data_files = {}

        try:
            # Determine compression type and open accordingly
            if data_tar_path.endswith('.gz'):
                tar_file = tarfile.open(data_tar_path, 'r:gz')
            elif data_tar_path.endswith('.xz'):
                tar_file = tarfile.open(data_tar_path, 'r:xz')
            elif data_tar_path.endswith('.bz2'):
                tar_file = tarfile.open(data_tar_path, 'r:bz2')
            else:
                tar_file = tarfile.open(data_tar_path, 'r')

            with tar_file:
                for member in tar_file.getmembers():
                    if member.isfile():
                        try:
                            file_content = tar_file.extractfile(member).read()
                            data_files[member.name] = file_content
                        except Exception as e:
                            print(f"警告：无法提取文件 {member.name}: {str(e)}")

        except Exception as e:
            print(f"警告：解析data.tar失败: {str(e)}")

        return data_files

    def _prepare_package_info(self, base_control_info, package_name, package_version,
                            maintainer_name, maintainer_email, package_description):
        """Prepare package metadata, using base info as fallback"""
        pkg_info = {}

        # Use provided values or fallback to base info or defaults
        pkg_info['Package'] = package_name or base_control_info.get('Package', 'dci-icons')
        pkg_info['Version'] = package_version or base_control_info.get('Version', '1.0.0')

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
                          base_data_files, pkg_info):
        """Create the actual deb package"""
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

            # Copy base data files if preserving
            file_list = []
            for file_path, file_content in base_data_files.items():
                target_path = os.path.join(data_dir, file_path.lstrip('./'))
                target_dir = os.path.dirname(target_path)
                if target_dir:
                    os.makedirs(target_dir, exist_ok=True)

                with open(target_path, 'wb') as f:
                    f.write(file_content)
                file_list.append(file_path)

            # Copy matching files to target location
            target_base = os.path.join(data_dir, install_target_path.lstrip('/'))
            os.makedirs(target_base, exist_ok=True)

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

            # Create control.tar.gz
            control_tar_path = os.path.join(temp_dir, "control.tar.gz")
            self._create_control_tar(control_tar_path, control_dir)

            # Create data.tar.gz
            data_tar_path = os.path.join(temp_dir, "data.tar.gz")
            self._create_data_tar(data_tar_path, data_dir)

            # Create debian-binary
            debian_binary_path = os.path.join(temp_dir, "debian-binary")
            with open(debian_binary_path, 'w') as f:
                f.write("2.0\n")

            # Create final deb package using ar
            deb_path = os.path.join(temp_dir, "package.deb")
            result = subprocess.run([
                "ar", "r", deb_path,
                "debian-binary", "control.tar.gz", "data.tar.gz"
            ], cwd=temp_dir, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"错误：创建deb包失败: {result.stderr}")
                return None, []

            # Read the created deb file
            with open(deb_path, 'rb') as f:
                deb_binary_data = f.read()

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

            return deb_binary_data, all_files

        except Exception as e:
            print(f"错误：创建deb包失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, []

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
