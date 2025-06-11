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
├── DCI File Saver
├── Directory Loader
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
**职责**: 构建符合图标规范的 DCI 文件，完全支持 DCI 规范中的图层系统

**目录结构规范**:
```
size/
└── state.tone/
    └── scale/
        └── priority.padding.palette.hue.saturation.brightness.red.green.blue.alpha.format
```

**图层系统设计**:
根据 DCI 规范，图层文件名包含完整的图层参数：
- **priority** (1-100): 图层优先级，数值越大绘制越靠上
- **padding** (0-100): 外边框值（整数），用于阴影效果等
- **palette** (-1,0,1,2,3): 调色板类型
  - -1: none (无调色板)
  - 0: foreground (前景色)
  - 1: background (背景色)
  - 2: highlight_foreground (高亮前景色)
  - 3: highlight (高亮色)
- **颜色调整参数** (-100 到 100): 精确控制图标颜色
  - hue: 色调调整
  - saturation: 饱和度调整
  - brightness: 亮度调整
  - red/green/blue: RGB分量调整
  - alpha: 透明度调整

**关键方法**:
- `add_icon_image()`: 添加图标图像（支持图层参数）
- `_add_to_structure()`: 构建目录结构
- `build()`: 生成最终 DCI 文件
- `_format_layer_filename()`: 格式化图层文件名

**图像处理流程**:
1. 验证参数 (状态、色调、格式、图层参数)
2. 计算实际尺寸 (size × scale)
3. 图像重采样 (Lanczos 算法)
4. 格式转换和压缩
5. 生成图层文件名 (包含所有图层参数)
6. 添加到目录结构

**图层文件名生成示例**:
```
# 基础图层: 1.0p.-1.0_0_0_0_0_0_0.webp
# 高优先级图层: 2.5p.1.10_20_30_0_0_0_0.png
# 调色板图层: 1.0p.2.0_0_0_50_-20_10_0.webp
```

### 1.2 DCI 读取模块 (dci_reader.py)

#### 1.2.1 DCIReader 类
**职责**: 读取和解析 DCI 文件，完全支持图层系统的解析

**解析流程**:
```
Binary Data → Header Validation → File Entries → Directory Structure → Image Extraction → Layer Parsing
```

**关键方法**:
- `read()`: 读取并解析 DCI 文件
- `_read_file_entry()`: 读取单个文件条目
- `_parse_directory_structure()`: 解析目录结构
- `get_icon_images()`: 提取所有图标图像
- `_parse_layer_filename()`: 解析图层文件名参数

**元数据提取**:
- 从路径解析: size, state, tone, scale
- 从文件名解析: priority, format, padding, palette, 颜色调整参数
- 图像属性: 尺寸、文件大小
- 图层属性: 优先级、外边框、调色板类型、颜色调整值

**图层文件名解析算法**:
```python
def _parse_layer_filename(self, filename: str) -> Dict:
    # 解析格式: priority.padding.palette.hue.saturation.brightness.red.green.blue.alpha.format
    parts = filename.split('.')

    if len(parts) >= 11:  # 完整图层信息
        return {
            'priority': safe_int(parts[0], 1),
            'padding': safe_float(parts[1], 0.0),
            'palette': safe_int(parts[2], -1),
            'hue': safe_int(parts[3], 0),
            'saturation': safe_int(parts[4], 0),
            'brightness': safe_int(parts[5], 0),
            'red': safe_int(parts[6], 0),
            'green': safe_int(parts[7], 0),
            'blue': safe_int(parts[8], 0),
            'alpha': safe_int(parts[9], 0),
            'format': parts[10],
            'palette_name': palette_names.get(palette, "unknown")
        }
```

**图层数据结构**:
解析后的图像数据包含完整的图层信息，便于后续处理和显示。

### 1.3 图像工具模块 (image_utils.py)

#### 1.3.1 图像转换函数

##### tensor_to_pil() 函数
**职责**: 将ComfyUI图像张量转换为PIL图像

**转换流程**:
1. 处理PyTorch张量和NumPy数组
2. 处理批次维度（4D张量取第一个）
3. 从0-1范围转换到0-255范围
4. 根据通道数创建对应的PIL图像模式

##### pil_to_tensor() 函数
**职责**: 将PIL图像转换为ComfyUI图像张量，**新增功能支持预览节点IMAGE输出**

**设计理念**:
- 为预览节点提供标准的ComfyUI IMAGE输出格式
- 处理各种PIL图像模式，确保兼容性
- 自动处理透明度，避免显示问题

**转换流程**:
1. **透明度处理**: RGBA图像自动合成到白色背景
2. **模式标准化**: 非RGB模式自动转换为RGB
3. **数值范围转换**: 从0-255范围转换到0-1范围
4. **张量格式化**: 转换为[1, H, W, C]格式的PyTorch张量

**技术实现**:
```python
def pil_to_tensor(pil_image):
    # 处理RGBA透明度
    if pil_image.mode == 'RGBA':
        rgb_image = Image.new('RGB', pil_image.size, (255, 255, 255))
        rgb_image.paste(pil_image, mask=pil_image.split()[-1])
        pil_image = rgb_image

    # 标准化为RGB模式
    elif pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')

    # 转换为张量
    img_array = np.array(pil_image).astype(np.float32) / 255.0
    tensor = torch.from_numpy(img_array).unsqueeze(0)  # 添加批次维度

    return tensor
```

**应用场景**:
- DCI预览节点的IMAGE输出
- DCI图像预览节点的IMAGE输出
- 批量图像处理的张量合并

#### 1.3.2 背景处理函数

##### create_checkerboard_background() 函数
**职责**: 创建棋盘格背景图案

##### apply_background() 函数
**职责**: 为透明图像应用背景色

#### 1.3.3 ComfyUI集成函数

##### pil_to_comfyui_format() 函数
**职责**: 将PIL图像转换为ComfyUI UI显示格式

**功能特性**:
- 自动处理透明度检测
- 生成唯一文件名
- 保存到临时目录
- 返回ComfyUI UI格式

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
        'scale': float,      # 缩放因子（支持小数）
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

#### BINARY_DATA 类型
```python
BINARY_DATA = bytes         # 直接的二进制数据内容，适用于所有二进制文件包括DCI文件
```

**说明**：
- `BINARY_DATA` 是统一的二进制数据类型，用于所有节点间的二进制数据传递
- 包含完整的文件二进制内容，可以是DCI文件、图像文件或其他任何二进制文件
- 不包含额外的元数据包装，保持数据的纯净性和通用性
- 所有二进制处理节点（DCIFileNode、DCIPreviewNode、BinaryFileLoader、BinaryFileSaver）都使用此类型

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
if output_directory:
    # 使用指定的输出目录，如果不存在则自动创建
    output_dir = output_directory
    ensure_directory(output_dir)
    final_path = os.path.join(output_dir, file_path)
else:
    # 使用 ComfyUI 输出目录
    output_dir = folder_paths.get_output_directory()
    final_path = os.path.join(output_dir, file_path)
```

##### DirectoryLoader 类
**职责**: 批量加载目录中的多个二进制文件，支持过滤条件和递归搜索功能

**设计理念**:
- 提供高效的批量文件加载能力
- 支持灵活的文件过滤和目录遍历
- 确保数据一致性和顺序稳定性
- 优化大量文件的处理性能

**输入参数**:
- `directory_path`: 要扫描的目录路径 (STRING)
- `file_filter`: 文件过滤模式，支持通配符 (STRING)，默认"*.dci"
- `include_subdirectories`: 是否包含子目录搜索 (BOOLEAN)，默认True

**输出数据**:
- `binary_data_list`: 加载文件的二进制数据列表 (BINARY_DATA_LIST)
- `relative_paths`: 相对文件路径列表 (STRING_LIST)

**核心算法设计**:

*广度优先遍历算法*:
```python
def _find_matching_files(self, directory_path, file_filter, include_subdirectories):
    matching_files = []

    if include_subdirectories:
        # 使用广度优先搜索确保一致的遍历顺序
        queue = deque([directory_path])

        while queue:
            current_dir = queue.popleft()
            items = sorted(os.listdir(current_dir))  # 确保顺序一致性

            for item in items:
                item_path = os.path.join(current_dir, item)
                if os.path.isfile(item_path):
                    if self._matches_filter(item, file_filter):
                        matching_files.append(item_path)
                elif os.path.isdir(item_path):
                    queue.append(item_path)  # 添加到队列末尾

    matching_files.sort()  # 最终排序确保一致性
    return matching_files
```

*通配符匹配算法*:
```python
def _matches_filter(self, filename, file_filter):
    # 支持多种模式，用逗号或分号分隔
    patterns = [pattern.strip() for pattern in file_filter.replace(';', ',').split(',')]

    for pattern in patterns:
        if pattern and fnmatch.fnmatch(filename, pattern):
            return True
    return False
```

**处理流程**:
1. **路径验证**: 验证目录路径的有效性和可访问性
2. **文件发现**: 使用广度优先算法遍历目录结构
3. **模式匹配**: 应用通配符过滤器筛选文件
4. **批量加载**: 逐个加载匹配的文件二进制内容
5. **路径计算**: 计算相对于根目录的相对路径
6. **数据同步**: 确保二进制数据列表和路径列表完全对应

**错误处理策略**:
- **权限错误**: 跳过无权限访问的目录，继续处理其他目录
- **文件读取错误**: 记录失败的文件，继续处理其他文件
- **路径错误**: 自动规范化路径，处理跨平台兼容性问题
- **内存管理**: 大文件分批处理，避免内存溢出

**性能优化**:
- **排序优化**: 使用自然排序确保文件顺序的直观性
- **内存效率**: 流式读取大文件，避免全部加载到内存
- **缓存机制**: 目录结构信息缓存，减少重复文件系统调用
- **并发安全**: 确保在多线程环境下的数据一致性

**使用场景**:
- **批量DCI文件分析**: 加载整个图标库进行批量分析
- **文件格式转换**: 批量转换目录中的文件格式
- **内容管理**: 扫描和管理大型文件集合
- **工作流自动化**: 在自动化流程中处理文件批次

**数据一致性保证**:
- 二进制数据列表和路径列表的索引完全对应
- 使用相同的排序算法确保顺序一致性
- 失败的文件不会在任何一个输出列表中出现
- 相对路径计算使用统一的基准目录

### 2.3 数据流转换

#### 节点间数据传递
```
# 主要工作流程
DCIImage → DCI_IMAGE_DATA → DCIFileNode → BINARY_DATA → DCIPreviewNode

# 二进制文件处理工作流程
BinaryFileLoader → BINARY_DATA → BinaryFileSaver

# 混合工作流程
BinaryFileLoader → BINARY_DATA → DCIPreviewNode (如果是DCI文件)
DCIFileNode → BINARY_DATA → BinaryFileSaver (保存DCI文件)
```

#### 数据类型注册
```python
# ComfyUI 自定义数据类型注册
NODE_CLASS_MAPPINGS = {
    "DCI_IMAGE_DATA": "DCI_IMAGE_DATA",
    "BINARY_DATA": "BINARY_DATA"
}
```

#### 数据类型兼容性
- `BINARY_DATA` 是通用的二进制数据类型，适用于任何二进制文件，包括DCI文件
- `DCI_IMAGE_DATA` 是专门的 DCI 图像数据类型，包含图像内容和元数据
- 所有节点使用统一的 `BINARY_DATA` 类型进行二进制数据传递，确保完全兼容

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

## 8. 发布与分发设计

### 8.1 ComfyUI Registry 发布

#### 8.1.1 发布配置
项目已配置完整的 ComfyUI Registry 发布支持：

**pyproject.toml 配置**:
```toml
[project]
name = "comfyui-dci"
description = "A comprehensive ComfyUI extension for creating, previewing, and analyzing DCI (DSG Combined Icons) format files."
version = "1.0.0"
license = { file = "LICENSE" }
dependencies = ["Pillow>=8.0.0", "numpy>=1.19.0"]

[tool.comfy]
PublisherId = ""  # 需要填入实际的发布者ID
DisplayName = "DCI Image Export Extension"
Icon = "https://raw.githubusercontent.com/your-username/comfyui-dci/master/resources/icon.svg"
```

**许可证文件**: MIT License，确保开源兼容性

**项目图标**: SVG格式图标，符合Registry要求

#### 8.1.2 自动化发布流程
**GitHub Actions 工作流**:
- 监听 `pyproject.toml` 文件变更
- 自动触发发布到 ComfyUI Registry
- 支持手动触发发布
- 使用安全的 API 密钥管理

**版本管理策略**:
- 遵循语义化版本规范 (SemVer)
- 主版本号：重大架构变更
- 次版本号：新功能添加
- 修订版本号：错误修复和小改进

#### 8.1.3 发布前检查清单
1. **代码质量**:
   - 所有测试通过
   - 代码风格一致
   - 文档完整更新

2. **功能验证**:
   - 所有节点正常工作
   - 示例工作流可执行
   - 错误处理正确

3. **兼容性测试**:
   - 多版本 ComfyUI 兼容
   - 依赖库版本兼容
   - 操作系统兼容性

### 8.2 分发策略

#### 8.2.1 多渠道分发
1. **ComfyUI Registry** (主要渠道):
   - 官方推荐安装方式
   - 自动更新支持
   - 用户发现性最佳

2. **GitHub Releases** (备用渠道):
   - 直接下载支持
   - 版本历史完整
   - 开发者友好

3. **ComfyUI Manager** (集成渠道):
   - 通过 Registry 自动集成
   - 一键安装体验
   - 依赖管理自动化

#### 8.2.2 安装方式设计
**优先级排序**:
1. ComfyUI Manager 一键安装 (推荐)
2. 自动安装脚本 (install.sh/install.bat)
3. 手动安装 (高级用户)

**安装脚本特性**:
- 自动检测 Python 环境
- 智能依赖安装
- 错误处理和回滚
- 跨平台兼容

### 8.3 用户支持设计

#### 8.3.1 文档体系
1. **README.md**: 快速入门和基本使用
2. **PUBLISHING.md**: 发布流程详细说明
3. **detailed-design.md**: 技术实现细节
4. **examples/**: 实际使用示例

#### 8.3.2 问题反馈机制
- GitHub Issues: 错误报告和功能请求
- 详细的错误信息输出
- 调试模式支持
- 社区支持渠道

#### 8.3.3 更新通知
- Registry 自动更新通知
- 版本变更日志
- 重要更新公告
- 兼容性说明

### 8.4 质量保证

#### 8.4.1 发布前测试
- 自动化测试套件
- 手动功能验证
- 性能基准测试
- 兼容性测试矩阵

#### 8.4.2 发布后监控
- 用户反馈收集
- 错误报告分析
- 使用统计分析
- 性能监控

#### 8.4.3 维护策略
- 定期安全更新
- 依赖库更新
- 功能改进迭代
- 社区贡献集成
