# ComfyUI DCI Image Exporter Extension - 详细设计

## 1. 模块详细设计

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

#### 1.3.1 DCIImageExporter 类
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

#### 1.3.2 DCIImageExporterAdvanced 类
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

#### 1.3.3 DCIPreviewNode 类
**职责**: DCI 文件预览功能

**预览参数**:
- `dci_file_path`: DCI 文件路径
- `grid_columns`: 网格列数 (1-10)
- `show_metadata`: 显示元数据标签

**输出内容**:
- `preview_image`: 网格预览图像
- `metadata_summary`: 元数据摘要文本

#### 1.3.4 DCIMetadataExtractor 类
**职责**: 元数据提取和分析

**过滤功能**:
- 按状态过滤 (all/normal/disabled/hover/pressed)
- 按色调过滤 (all/light/dark)
- 按缩放因子过滤

**输出报告**:
- `detailed_metadata`: 详细元数据
- `directory_structure`: 目录结构
- `file_list`: 文件列表

## 2. 数据结构设计

### 2.1 图像元数据结构
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

### 2.2 目录结构
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
