# ComfyUI DCI Image Exporter Extension - 详细设计

## 1. 项目架构与目录结构

### 1.1 目录结构设计

项目采用模块化的目录结构，遵循ComfyUI扩展的最佳实践和ComfyUI-Easy-Use等成功扩展的组织方式：

```
comfyui-dci/
├── py/                    # 核心Python实现模块
│   ├── __init__.py       # 模块初始化和导出声明
│   ├── dci_format.py     # DCI格式实现和构建器
│   ├── dci_reader.py     # DCI文件读取和解析器
│   └── nodes.py          # ComfyUI节点定义和实现
├── locales/              # 国际化和本地化支持
│   ├── en.json           # 英文本地化文件
│   └── zh-CN.json        # 中文本地化文件
├── resources/            # 静态资源和模板文件
│   └── README.md         # 资源目录说明
├── tools/                # 开发和维护工具
│   ├── commit_helper.py  # Git提交助手
│   └── README.md         # 工具目录说明
├── tests/                # 测试套件
│   ├── test_*.py         # 各种功能测试文件
│   └── README.md         # 测试说明文档
├── examples/             # 示例工作流和使用案例
│   ├── example_*.json    # ComfyUI工作流示例文件
│   └── README.md         # 示例说明文档
├── web_version/          # Web组件（预留扩展）
│   └── README.md         # Web组件说明
├── __init__.py           # 扩展入口点和节点注册
├── install.sh            # Linux/Mac自动安装脚本
├── install.bat           # Windows自动安装脚本
├── README.md             # 项目主文档
├── requirements.txt      # Python依赖声明
├── preliminary-design.md # 概要设计文档
└── detailed-design.md    # 详细设计文档（本文件）
```

### 1.2 目录结构优势

这种结构设计提供了以下优势：

**模块化分离**：
- `py/` 目录包含所有核心Python实现，便于代码管理
- `locales/` 支持国际化，提升用户体验
- `resources/` 集中管理静态资源
- `tools/` 包含开发工具，提高开发效率

**易于维护**：
- 每个目录有明确的职责和边界
- 相关文件集中存放，便于查找和修改
- 文档与代码分离，便于维护

**可扩展性**：
- `web_version/` 为未来Web功能预留空间
- 模块化设计便于添加新功能
- 标准化结构便于团队协作

**标准化**：
- 遵循ComfyUI生态系统的惯例
- 参考成功扩展的最佳实践
- 便于用户理解和使用

## 2. 节点分组设计

### 1.1 统一分组策略
为了提高用户体验和节点的可发现性，所有 DCI 扩展节点都统一归类在 **"DCI"** 分组下。这种设计参考了 ComfyUI-Easy-Use 等成功扩展的做法。

**设计原则**:
- 统一性：所有相关节点集中在一个分组下
- 可发现性：用户可以轻松找到所有 DCI 相关功能
- 一致性：避免节点分散在不同的系统分类中

**实现方式**:
```python
# 在每个节点类中设置统一的 CATEGORY
class DCIImageExporter:
    CATEGORY = "DCI"

class DCIPreviewNode:
    CATEGORY = "DCI"

# 所有节点都使用相同的分类
```

**节点分组结构**:
```
DCI/
├── DCI Image Exporter
├── DCI Image Exporter (Advanced)
├── DCI Preview

├── DCI Metadata Extractor
├── DCI Image
├── DCI File
├── DCI Preview (Binary)
├── Binary File Loader
├── Binary File Saver
└── Binary File Uploader
```

### 1.2 节点注册机制
为确保节点能正确加载和显示，实现了双重注册机制：

**主注册文件 (__init__.py)**:
```python
NODE_CLASS_MAPPINGS = {
    "DCIImageExporter": DCIImageExporter,
    "DCIImageExporterAdvanced": DCIImageExporterAdvanced,
    # ... 其他节点
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIImageExporter": "DCI Image Exporter",
    "DCIImageExporterAdvanced": "DCI Image Exporter (Advanced)",
    # ... 其他节点
}
```

**节点文件内注册 (nodes.py)**:
```python
# 在文件末尾重复定义，确保兼容性
NODE_CLASS_MAPPINGS = { ... }
NODE_DISPLAY_NAME_MAPPINGS = { ... }
```

这种双重注册确保了与不同版本的 ComfyUI 和其他扩展的兼容性。

## 2. 模块详细设计

### 1.1 DCI 文件格式模块 (dci_format.py)

#### 1.1.1 DCIFile 类
**职责**: 实现 DCI 文件格式的底层操作

**核心属性**:
```python
MAGIC = b'DCI\x00'  # 魔数标识
VERSION = 1         # 格式版本
FILE_TYPE_FILE = 1  # 文件类型
FILE_TYPE_DIRECTORY = 2  # 目录类型
```

**关键方法**:
- `add_file(name, content, file_type)`: 添加文件到 DCI 归档
- `add_directory(name, files)`: 添加目录及其文件
- `write(output_path)`: 写入 DCI 文件到磁盘
- `_natural_sort_key(text)`: 自然排序算法

**文件结构**:
```
DCI Header (8 bytes):
├── Magic (4 bytes): 'DCI\0'
├── Version (1 byte): 1
└── File Count (3 bytes): 文件数量

File Entry (72+ bytes):
├── File Type (1 byte): 文件类型
├── File Name (63 bytes): 文件名 (null-terminated)
├── Content Size (8 bytes): 内容大小
└── Content (variable): 文件内容
```

#### 1.1.2 DCIIconBuilder 类
**职责**: 构建符合图标规范的 DCI 文件

**目录结构规范**:
```
size/
└── state.tone/
    └── scale/
        └── priority.padding.palette.hue.saturation.brightness.red.green.blue.alpha.format
```

**关键方法**:
- `add_icon_image()`: 添加图标图像
- `_add_to_structure()`: 构建目录结构
- `build()`: 生成最终 DCI 文件

**图像处理流程**:
1. 验证参数 (状态、色调、格式)
2. 计算实际尺寸 (size × scale)
3. 图像重采样 (Lanczos 算法)
4. 格式转换和压缩
5. 添加到目录结构

### 1.2 DCI 读取模块 (dci_reader.py)

#### 1.2.1 DCIReader 类
**职责**: 读取和解析 DCI 文件

**解析流程**:
```
Binary Data → Header Validation → File Entries → Directory Structure → Image Extraction
```

**关键方法**:
- `read()`: 读取并解析 DCI 文件
- `_read_file_entry()`: 读取单个文件条目
- `_parse_directory_structure()`: 解析目录结构
- `get_icon_images()`: 提取所有图标图像

**元数据提取**:
- 从路径解析: size, state, tone, scale
- 从文件名解析: priority, format
- 图像属性: 尺寸、文件大小

#### 1.2.2 DCIPreviewGenerator 类
**职责**: 生成 DCI 文件的可视化预览

**预览生成算法**:
1. 计算网格布局 (行数、列数)
2. 确定单元格尺寸
3. 创建画布
4. 绘制图像和标签
5. 返回合成图像

**标签信息**:
- 状态和色调 (state.tone)
- 缩放因子 (scale)
- 图像格式 (format)
- 文件大小

### 1.3 ComfyUI 节点模块 (nodes.py)

#### 1.3.1 传统节点（向后兼容）

##### DCIImageExporter 类
**职责**: 基础 DCI 导出功能

**输入参数**:
- `image`: ComfyUI 图像张量
- `filename`: 输出文件名
- `icon_size`: 图标尺寸 (16-1024)
- `icon_state`: 图标状态
- `tone_type`: 色调类型
- `image_format`: 图像格式
- `scale_factors`: 缩放因子列表
- `output_directory`: 输出目录

**处理流程**:
1. 张量转换为 PIL 图像
2. 解析缩放因子
3. 确定输出路径
4. 创建 DCIIconBuilder
5. 添加图像到构建器
6. 生成 DCI 文件

##### DCIImageExporterAdvanced 类
**职责**: 高级多状态 DCI 导出

**扩展功能**:
- 支持多个状态图像输入
- 支持多色调组合
- 批量处理多种状态

**状态处理逻辑**:
```python
state_images = {
    'normal': normal_image or base_image,
    'disabled': disabled_image,
    'hover': hover_image,
    'pressed': pressed_image
}
```

##### DCIPreviewNode 类
**职责**: DCI 文件预览功能

**预览参数**:
- `dci_file_path`: DCI 文件路径
- `grid_columns`: 网格列数 (1-10)
- `show_metadata`: 显示元数据标签

**输出内容**:
- `preview_image`: 网格预览图像
- `metadata_summary`: 元数据摘要文本

##### DCIFileLoader 类
**职责**: DCI 文件加载器

**功能**:
- 自动搜索 DCI 文件
- 路径验证和规范化

##### DCIMetadataExtractor 类
**职责**: 元数据提取和分析

**过滤功能**:
- 按状态过滤 (all/normal/disabled/hover/pressed)
- 按色调过滤 (all/light/dark)
- 按缩放因子过滤

**输出报告**:
- `detailed_metadata`: 详细元数据
- `directory_structure`: 目录结构
- `file_list`: 文件列表

#### 1.3.2 重构节点（推荐使用）

##### DCIImage 类
**职责**: 创建单个 DCI 图像数据，输出元数据而不是直接创建文件

**设计理念**:
- 模块化设计，提供更灵活的工作流程
- 输出结构化数据而非文件，支持节点间数据传递
- 支持复杂的多图像组合场景

**输入参数**:
- `image`: ComfyUI 图像张量
- `icon_size`: 图标尺寸 (16-1024)
- `icon_state`: 图标状态 (normal/disabled/hover/pressed)
- `tone_type`: 色调类型 (light/dark)
- `scale`: 缩放因子 (1-10)
- `image_format`: 图像格式 (webp/png/jpg)

**输出数据结构**:
```python
DCI_IMAGE_DATA = {
    'path': str,           # 目录路径
    'filename': str,       # 文件名
    'content': bytes,      # 图像二进制数据
    'metadata': {          # 元数据
        'size': int,
        'state': str,
        'tone': str,
        'scale': int,
        'format': str,
        'file_size': int,
        'image_dimensions': tuple
    }
}
```

**处理流程**:
1. 张量转换为 PIL 图像
2. 图像缩放和格式转换
3. 生成目录路径和文件名
4. 创建元数据结构
5. 返回结构化数据

##### DCIFileNode 类
**职责**: 接收多个 DCI Image 输出并组合成完整的 DCI 文件

**设计理念**:
- 支持最多12个图像输入的灵活组合
- 输出二进制数据流，支持进一步处理
- 可选文件保存功能

**输入参数**:
- `dci_image_1` 到 `dci_image_12`: DCI图像数据 (可选)
- `filename`: 文件名
- `save_to_file`: 是否保存到文件
- `output_directory`: 输出目录

**输出数据结构**:
```python
DCI_BINARY_DATA = {
    'data': bytes,         # DCI文件二进制数据
    'metadata': {          # 文件元数据
        'file_count': int,
        'total_size': int,
        'images': list,    # 图像元数据列表
        'directory_structure': dict
    }
}
```

**处理流程**:
1. 收集所有输入的 DCI 图像数据
2. 按目录结构组织文件
3. 创建 DCI 文件对象
4. 生成二进制数据
5. 可选保存到文件
6. 返回二进制数据和路径

##### DCIPreviewFromBinary 类
**职责**: 从二进制 DCI 数据创建可视化预览

**设计理念**:
- 与 DCIFileNode 配合使用
- 支持内存中的 DCI 数据预览
- 无需文件系统操作

**输入参数**:
- `dci_binary_data`: DCI文件的二进制数据
- `grid_columns`: 网格列数 (1-10)
- `show_metadata`: 显示元数据

**处理流程**:
1. 从二进制数据解析 DCI 结构
2. 提取图像和元数据
3. 生成网格预览
4. 创建元数据摘要
5. 返回预览图像和摘要

## 2. 数据结构设计

### 2.1 传统数据结构

#### 图像元数据结构
```python
ImageMetadata = {
    'image': PIL.Image,      # PIL 图像对象
    'size': int,             # 图标尺寸
    'state': str,            # 图标状态
    'tone': str,             # 色调类型
    'scale': int,            # 缩放因子
    'format': str,           # 图像格式
    'priority': int,         # 优先级
    'path': str,             # 目录路径
    'filename': str,         # 文件名
    'file_size': int         # 文件大小
}
```

#### 目录结构
```python
DirectoryStructure = {
    'size_dir': {
        'state.tone_dir': {
            'scale_dir': {
                'filename': bytes  # 图像数据
            }
        }
    }
}
```

### 2.2 重构节点数据结构

#### DCI_IMAGE_DATA 类型
```python
DCI_IMAGE_DATA = {
    'path': str,             # 目录路径 (如: "256/normal.dark/2")
    'filename': str,         # 文件名 (如: "0.0.0.0.0.0.0.0.0.0.webp")
    'content': bytes,        # 图像二进制数据
    'metadata': {            # 详细元数据
        'size': int,         # 图标尺寸
        'state': str,        # 图标状态
        'tone': str,         # 色调类型
        'scale': int,        # 缩放因子
        'format': str,       # 图像格式
        'file_size': int,    # 文件大小
        'image_dimensions': tuple,  # 图像尺寸 (width, height)
        'priority': int,     # 优先级
        'padding': int,      # 填充
        'palette': int,      # 调色板
        'hue': int,          # 色相
        'saturation': int,   # 饱和度
        'brightness': int,   # 亮度
        'red': int,          # 红色分量
        'green': int,        # 绿色分量
        'blue': int,         # 蓝色分量
        'alpha': int         # 透明度
    }
}
```

#### DCI_BINARY_DATA 类型
```python
DCI_BINARY_DATA = {
    'data': bytes,           # 完整的DCI文件二进制数据
    'metadata': {            # 文件级元数据
        'file_count': int,   # 文件总数
        'total_size': int,   # 总文件大小
        'magic': bytes,      # 魔数标识
        'version': int,      # 格式版本
        'images': [          # 图像元数据列表
            {
                'path': str,
                'filename': str,
                'size': int,
                'state': str,
                'tone': str,
                'scale': int,
                'format': str,
                'file_size': int,
                'image_dimensions': tuple
            }
        ],
        'directory_structure': {  # 目录结构映射
            'size_dirs': list,    # 尺寸目录列表
            'state_tone_dirs': list,  # 状态.色调目录列表
            'scale_dirs': list,   # 缩放目录列表
            'supported_formats': list,  # 支持的格式列表
            'statistics': {       # 统计信息
                'total_images': int,
                'unique_sizes': int,
                'unique_states': int,
                'unique_tones': int,
                'unique_scales': int,
                'format_distribution': dict
            }
        }
    }
}
```

#### BINARY_DATA 类型
```python
BINARY_DATA = bytes         # 直接的二进制数据内容，不包含元数据包装
```

#### 1.3.3 二进制文件处理节点（新增）

##### BinaryFileLoader 类
**职责**: 从文件系统加载二进制文件，专为处理 DCI 图标文件等二进制数据设计

**设计理念**:
- 提供通用的二进制文件加载能力
- 支持任意二进制文件格式，特别优化 DCI 文件
- 输出结构化的二进制数据，便于后续节点处理
- 支持通过其他节点输入文件路径，提供更灵活的工作流程

**输入参数**:
- `file_path`: 要加载的文件路径 (STRING, 可选)，可通过其他节点输入或手动输入，默认空字符串

**输出数据**:
- `binary_data`: 文件的二进制内容 (BINARY_DATA)
- `file_path`: 加载文件的完整路径 (STRING)

**处理流程**:
1. 验证文件路径的有效性和可读性
2. 读取文件的二进制内容
3. 直接返回二进制数据，不进行任何包装或元数据添加
4. 返回文件路径用于后续处理

**错误处理**:
- 文件不存在或无法读取时返回错误信息
- 文件过大时提供警告但继续处理
- 权限不足时提供明确的错误提示

##### BinaryFileSaver 类
**职责**: 将二进制数据保存到文件系统，支持自定义输出路径和目录

**设计理念**:
- 提供灵活的文件保存功能
- 支持自定义输出目录和文件名
- 与 ComfyUI 的文件系统集成

**输入参数**:
- `binary_data`: 要保存的二进制数据 (BINARY_DATA)
- `file_path`: 目标文件路径 (STRING)
- `output_directory`: 输出目录，可选 (STRING)

**输出数据**:
- `saved_path`: 实际保存的文件路径 (STRING)

**处理流程**:
1. 验证输入的二进制数据结构
2. 确定最终的输出路径
   - 如果指定了 output_directory，使用该目录
   - 否则使用 ComfyUI 的默认输出目录
3. 创建必要的目录结构
4. 写入二进制数据到文件
5. 验证写入的文件完整性
6. 返回实际保存的文件路径

**路径处理逻辑**:
```python
if output_directory and os.path.exists(output_directory):
    final_path = os.path.join(output_directory, file_path)
else:
    # 使用 ComfyUI 输出目录
    output_dir = folder_paths.get_output_directory()
    final_path = os.path.join(output_dir, file_path)
```

##### BinaryFileUploader 类
**职责**: 通过 ComfyUI 界面上传二进制文件，提供直观的文件选择体验

**设计理念**:
- 利用 ComfyUI 原生的文件上传机制
- 提供简洁直观的用户界面
- 与 ComfyUI 的文件处理系统无缝集成

**输入参数**:
- `upload`: 文件上传控件，必需 (UPLOAD)

**输出数据**:
- `binary_data`: 上传文件的二进制数据 (BINARY_DATA)
- `file_path`: 上传文件的完整路径 (STRING)

**处理流程**:
1. 接收用户通过界面上传的文件
2. 验证上传文件的有效性
3. 获取文件路径和基本信息
4. 读取文件的二进制内容
5. 返回文件数据和路径信息

**上传处理算法**:
```python
def upload_binary_file(self, upload):
    # 验证上传对象
    if not upload or not hasattr(upload, 'name'):
        return (None, "")

    # 获取文件路径
    file_path = upload.name

    # 读取二进制内容
    with open(file_path, 'rb') as f:
        content = f.read()

    return (content, file_path)
```

**使用说明**:
- 点击上传按钮选择要上传的文件
- 支持任意二进制文件格式
- 自动读取文件内容并输出二进制数据
- 在控制台显示上传文件的信息

### 2.3 数据流转换

#### 节点间数据传递
```
# 主要工作流程
DCIImage → DCI_IMAGE_DATA → DCIFileNode → DCI_BINARY_DATA → DCIPreviewFromBinary

# 二进制文件处理工作流程
BinaryFileLoader → BINARY_DATA → BinaryFileSaver
BinaryFileUploader → BINARY_DATA → BinaryFileSaver

# 混合工作流程
BinaryFileLoader → BINARY_DATA → DCIPreviewFromBinary (如果是DCI文件)
DCIFileNode → DCI_BINARY_DATA → BinaryFileSaver (保存DCI文件)
```

#### 数据类型注册
```python
# ComfyUI 自定义数据类型注册
NODE_CLASS_MAPPINGS = {
    "DCI_IMAGE_DATA": "DCI_IMAGE_DATA",
    "DCI_BINARY_DATA": "DCI_BINARY_DATA",
    "BINARY_DATA": "BINARY_DATA"
}
```

#### 数据类型兼容性
- `BINARY_DATA` 是通用的二进制数据类型，适用于任何二进制文件
- `DCI_BINARY_DATA` 是专门的 DCI 文件数据类型，包含 DCI 特定的元数据
- 两种类型可以通过适配器模式进行转换

## 3. 算法设计

### 3.1 图像缩放算法
**算法**: Lanczos 重采样
**优势**: 高质量缩放，保持图像细节
**实现**: `PIL.Image.resize(size, Image.Resampling.LANCZOS)`

### 3.2 自然排序算法
**目的**: 文件名按自然顺序排序 (1, 2, 10 而不是 1, 10, 2)
**实现**:
```python
def _natural_sort_key(text):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    return [convert(c) for c in re.split('([0-9]+)', text)]
```

### 3.3 网格布局算法
**计算公式**:
```python
total_images = len(images)
grid_rows = (total_images + grid_cols - 1) // grid_cols
canvas_width = grid_cols * cell_size
canvas_height = grid_rows * cell_size
```

## 4. 错误处理设计

### 4.1 输入验证
- **文件路径验证**: 检查文件存在性和可读性
- **参数范围验证**: 尺寸、缩放因子范围检查
- **格式验证**: 支持的图像格式检查

### 4.2 异常处理策略
```python
try:
    # 核心操作
    result = process_operation()
    return success_result
except SpecificException as e:
    # 特定异常处理
    log_error(e)
    return error_result
except Exception as e:
    # 通用异常处理
    log_unexpected_error(e)
    return default_error_result
```

### 4.3 错误恢复机制
- **部分失败处理**: 单个图像失败不影响整体处理
- **默认值回退**: 参数错误时使用默认值
- **优雅降级**: 功能不可用时提供基础功能

## 5. 性能优化设计

### 5.1 内存优化
- **流式处理**: 大文件分块读取，避免全部加载到内存
- **及时释放**: PIL 图像对象使用后立即释放
- **缓存策略**: 重复使用的数据进行缓存

### 5.2 处理效率优化
- **批量操作**: 多个缩放因子一次性处理
- **格式选择**: 默认使用 WebP 格式，平衡质量和大小
- **并行处理**: 独立操作可并行执行

### 5.3 文件 I/O 优化
- **缓冲写入**: 使用缓冲区减少磁盘写入次数
- **压缩优化**: 根据图像内容选择最佳压缩参数

## 6. 测试设计

### 6.1 单元测试覆盖
- **DCIFile 类**: 文件创建、写入、读取
- **DCIIconBuilder 类**: 图像添加、结构构建
- **DCIReader 类**: 文件解析、图像提取
- **节点类**: 参数验证、输出正确性

### 6.2 集成测试场景
- **完整导出流程**: 图像输入到 DCI 文件输出
- **预览生成流程**: DCI 文件到预览图像
- **元数据分析流程**: DCI 文件到分析报告

### 6.3 性能测试指标
- **大文件处理**: 测试 100MB+ DCI 文件处理能力
- **批量处理**: 测试多状态、多缩放因子处理性能
- **内存使用**: 监控内存峰值和泄漏

## 7. 扩展接口设计

### 7.1 格式扩展接口
```python
class FormatHandler:
    def save_image(self, image: PIL.Image, output: BytesIO, **kwargs):
        """保存图像到指定格式"""
        pass

    def get_extension(self) -> str:
        """获取文件扩展名"""
        pass
```

### 7.2 状态扩展接口
```python
class StateProcessor:
    def process_state(self, image: PIL.Image, state: str) -> PIL.Image:
        """处理特定状态的图像效果"""
        pass
```

### 7.3 预览扩展接口
```python
class PreviewRenderer:
    def render_cell(self, image: PIL.Image, metadata: dict) -> PIL.Image:
        """渲染单个预览单元格"""
        pass
```
