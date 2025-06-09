# ComfyUI DCI 图像导出扩展

一个全面的 ComfyUI 扩展，用于创建、预览和分析 DCI（DSG Combined Icons）格式文件。此扩展实现了完整的 DCI 规范，支持多状态图标、多色调、缩放因子和高级元数据分析。

## 项目状态

- ✅ **完整的 DCI 格式实现**：完全支持 DCI 文件创建和读取
- ✅ **多状态图标支持**：正常、悬停、按下、禁用状态
- ✅ **多色调支持**：浅色和深色调变体
- ✅ **高级预览系统**：基于网格的可视化与元数据覆盖
- ✅ **模块化节点架构**：重构为更灵活的组合式节点
- ✅ **二进制数据流**：支持节点间二进制数据传递
- ✅ **二进制文件处理**：专用的二进制文件加载和保存节点
- ✅ **生产就绪**：通过示例工作流程全面测试

## 目录结构

```
comfyui-dci/
├── py/                          # 核心Python模块
│   ├── __init__.py             # 模块初始化
│   ├── dci_format.py           # DCI格式实现
│   ├── dci_reader.py           # DCI文件读取器
│   └── nodes.py                # ComfyUI节点定义
├── locales/                     # 国际化文件
├── resources/                   # 静态资源
├── tools/                       # 开发工具
├── tests/                       # 测试文件
├── examples/                    # 示例工作流
├── web_version/                 # Web组件（预留）
├── __init__.py                  # 扩展入口点
├── README.md                    # 项目文档
├── requirements.txt             # Python依赖
├── install.sh                   # Linux/Mac安装脚本
├── install.bat                  # Windows安装脚本
├── preliminary-design.md        # 概要设计
└── detailed-design.md           # 详细设计
```

## 功能特性

### 导出功能
- **DCI 图像创建**：将单个图像转换为 DCI 图像数据，支持自定义参数
- **DCI 文件组合**：将多个 DCI 图像组合成完整的 DCI 文件
- **多种缩放因子**：支持小数缩放如 1x、1.25x、1.5x、2x 等自定义缩放组合
- **格式支持**：WebP、PNG 和 JPEG 格式
- **色调支持**：浅色和深色调变体
- **可自定义图标尺寸**：从 16x16 到 1024x1024 像素

### 预览功能
- **可视化预览**：生成 DCI 文件中所有图像的网格预览
- **元数据显示**：显示每个图像的全面元数据，包括尺寸、状态、色调、缩放、格式
- **节点内显示**：直接在节点界面中显示预览内容

### 二进制文件处理功能
- **文件加载**：从文件系统加载任意二进制文件，专为 DCI 图标文件优化
- **文件保存**：将二进制数据保存到指定位置，支持自定义输出目录
- **数据结构化**：提供统一的二进制数据结构，包含内容、元数据和路径信息

## 安装

### 自动安装（推荐）

1. 将此仓库克隆到您的 ComfyUI 自定义节点目录：
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/comfyui-dci.git
```

2. 运行安装脚本：

**Linux/Mac:**
```bash
cd comfyui-dci
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
cd comfyui-dci
install.bat
```

### 手动安装

1. 克隆仓库（同上）

2. 手动安装依赖项：
```bash
cd comfyui-dci
pip install -r requirements.txt
```

3. 重启 ComfyUI

4. 安装完成后，所有 DCI 节点将出现在 ComfyUI 节点菜单的 **"DCI"** 分类下

## ComfyUI 节点详细说明

本扩展提供了 5 个 ComfyUI 节点，所有节点都统一归类在 **"DCI"** 分组下，并按功能分为三个子分类：

### 节点分组

#### DCI/Export（导出）
- DCI_Image (DCI Image)
- DCI_FileNode (DCI File)

#### DCI/Preview（预览）
- DCI_PreviewNode (DCI Preview)

#### DCI/Debug（调试）
- DCI_ImageDebug (DCI Image Debug)

#### DCI/Files（文件处理）
- DCI_BinaryFileLoader (Binary File Loader)
- DCI_BinaryFileSaver (Binary File Saver)

### 可用节点详细说明

#### 1. DCI Image（DCI 图像）
**节点类别**：`DCI/Export`
**功能描述**：创建单个 DCI 图像数据，输出元数据而不是直接创建文件，提供更灵活的工作流程。

**必需输入参数：**
- **`image`** (IMAGE)：ComfyUI 图像张量
- **`icon_size`** (INT)：图标尺寸（16-1024像素），默认256
- **`icon_state`** (COMBO)：图标状态（normal/disabled/hover/pressed），默认normal
- **`tone_type`** (COMBO)：色调类型（light/dark），默认dark
- **`scale`** (FLOAT)：缩放因子（0.1-10.0），默认1.0，支持小数如1.25
- **`image_format`** (COMBO)：图像格式（webp/png/jpg），默认webp

**可选输入参数：**
- **`background_color`** (COMBO)：背景色处理（transparent/white/black/custom），默认transparent
- **`custom_bg_r`** (INT)：自定义背景色红色分量（0-255），默认255
- **`custom_bg_g`** (INT)：自定义背景色绿色分量（0-255），默认255
- **`custom_bg_b`** (INT)：自定义背景色蓝色分量（0-255），默认255

**输出：**
- **`dci_image_data`** (DCI_IMAGE_DATA)：包含路径、内容、元数据的字典数据

**背景色处理说明：**
- **transparent**：保持原始透明度（仅PNG和WebP支持）
- **white**：将透明背景替换为白色
- **black**：将透明背景替换为黑色
- **custom**：使用自定义RGB颜色作为背景

#### 2. DCI File（DCI 文件）
**节点类别**：`DCI/Export`
**功能描述**：接收多个 DCI Image 输出并组合成完整的 DCI 文件，专注于生成二进制数据。如需保存文件，请使用 Binary File Saver 节点。

**可选输入参数：**
- **`dci_image_1` 到 `dci_image_12`** (DCI_IMAGE_DATA)：最多12个DCI图像数据

**输出：**
- **`dci_binary_data`** (BINARY_DATA)：DCI文件的二进制数据

#### 3. DCI Preview（DCI 预览）
**节点类别**：`DCI/Preview`
**功能描述**：直接在节点内显示 DCI 文件内容的可视化网格预览和详细元数据信息。专门用于预览 DCI 二进制数据。

**必需输入参数：**
- **`dci_binary_data`** (BINARY_DATA)：DCI 文件的二进制数据

**可选输入参数：**
- **`grid_columns`** (INT)：网格列数（1-10），默认1（单列显示）
- **`background_color`** (COMBO)：预览背景色（light_gray/dark_gray/white/black/blue/green/red/custom），默认light_gray
- **`custom_bg_r`** (INT)：自定义背景色红色分量（0-255），默认240
- **`custom_bg_g`** (INT)：自定义背景色绿色分量（0-255），默认240
- **`custom_bg_b`** (INT)：自定义背景色蓝色分量（0-255），默认240
- **`text_font_size`** (INT)：文本字号大小（8-24像素），默认12
- **`show_file_paths`** (BOOLEAN)：是否显示文件路径列表，默认True

**节点内预览功能：**
- **图像网格预览**：直接在节点界面中显示所有图像的网格布局，图像居左对齐
- **智能背景色设置**：支持多种预设背景色和自定义RGB颜色
- **可调节文本字号**：支持8-24像素的字号设置，便于在不同分辨率下查看
- **文件路径显示控制**：可选择是否显示完整的DCI文件路径列表（如 /235/normal.light/1/1.0.0.0.0.0.0.0.0.0.webp）
- **详细元数据显示**：在节点内显示全面的文件信息，包括：
  - 图标尺寸、状态、色调、缩放因子
  - 图像格式、文件大小、实际尺寸
  - 完整的DCI内部路径和文件名
  - 每个图像的优先级和详细属性
  - 统计汇总信息和文件路径列表

**输出：**
- 无输出（所有预览内容直接在节点内显示）

**注意**：此节点不再接受 `dci_file_path` 参数，专门用于处理二进制数据输入。默认使用单列布局以便更好地查看详细信息。

#### 4. DCI Image Debug（DCI 图像调试）
**节点类别**：`DCI/Debug`
**功能描述**：专门用于调试和预览单个 DCI 图像数据的详细信息，提供全面的元数据分析和可视化预览。

**必需输入参数：**
- **`dci_image_data`** (DCI_IMAGE_DATA)：DCI 图像数据

**可选输入参数：**
- **`show_metadata`** (BOOLEAN)：是否显示元数据信息，默认True
- **`show_binary_info`** (BOOLEAN)：是否显示二进制数据信息，默认True
- **`preview_background`** (COMBO)：预览背景类型（transparent/white/black/checkerboard），默认checkerboard

**节点内调试功能：**
- **图像预览**：直接在节点界面中显示处理后的图像
- **智能背景显示**：支持透明、白色、黑色和棋盘格背景，便于查看透明图像
- **详细元数据分析**：显示完整的DCI图像信息，包括：
  - DCI路径、图标尺寸、状态、色调、缩放因子
  - 图像格式、实际尺寸、背景处理方式
  - 二进制数据大小、数据类型、十六进制预览
  - PIL图像信息（尺寸、颜色模式、格式）
  - 数据完整性验证状态
- **二进制数据分析**：显示文件大小、数据类型和前16字节的十六进制预览
- **验证状态检查**：自动检查DCI图像数据的完整性和有效性

**输出：**
- 无输出（所有调试信息直接在节点内显示）

**使用场景：**
- 调试DCI图像创建过程中的问题
- 验证图像数据的正确性和完整性
- 分析背景色处理效果
- 检查二进制数据的生成结果

#### 5. Binary File Loader（二进制文件加载器）
**节点类别**：`DCI/Files`
**功能描述**：从文件系统加载二进制文件，专为处理 DCI 图标文件等二进制数据设计。

**可选输入参数：**
- **`file_path`** (STRING)：要加载的文件路径，默认空字符串

**输出：**
- **`binary_data`** (BINARY_DATA)：文件的二进制内容（bytes 类型）
- **`file_path`** (STRING)：加载文件的完整路径

#### 6. Binary File Saver（二进制文件保存器）
**节点类别**：`DCI/Files`
**功能描述**：将二进制数据保存到文件系统，支持自定义输出路径和目录。

**必需输入参数：**
- **`binary_data`** (BINARY_DATA)：要保存的二进制数据
- **`file_name`** (STRING)：目标文件名，默认"binary_file"

**可选输入参数：**
- **`output_directory`** (STRING)：输出目录，默认使用 ComfyUI 输出目录

**输出：**
- **`saved_path`** (STRING)：实际保存的文件路径

## 使用示例

### 推荐的新工作流程（使用重构节点）

1. **创建 DCI 图像**：
   - 使用 `DCI Image` 节点将 ComfyUI 图像转换为 DCI 图像数据
   - 设置图标尺寸、状态、色调、缩放因子和格式
   - 可以创建多个不同状态和缩放的图像

2. **组合 DCI 文件**：
   - 使用 `DCI File` 节点将多个 DCI 图像组合成完整的 DCI 文件二进制数据
   - 支持最多12个图像输入的灵活组合

3. **预览 DCI 内容**：
   - 使用 `DCI Preview` 节点直接在节点内查看 DCI 文件的内容和元数据
   - 自动显示图像网格和详细的元数据信息

4. **保存 DCI 文件**：
   - 使用 `Binary File Saver` 节点将 DCI 二进制数据保存到磁盘

### 文件操作工作流程

1. **加载现有 DCI 文件**：
   - 使用 `Binary File Loader` 加载现有的 DCI 文件

2. **预览和分析**：
   - 将加载的二进制数据连接到 `DCI Preview` 节点进行预览

### 调试工作流程

1. **调试单个 DCI 图像**：
   - 使用 `DCI Image Debug` 节点检查单个 DCI 图像的详细信息
   - 验证背景色处理效果和图像质量
   - 分析二进制数据的生成结果

2. **问题排查**：
   - 当图像背景出现问题时，使用调试节点检查背景色处理设置
   - 验证图像数据的完整性和格式正确性
   - 检查DCI路径和元数据的生成结果

### 高级用法

- **多状态图标**：为不同的交互状态（normal、hover、pressed、disabled）创建不同的图像
- **多色调支持**：为浅色和深色主题创建不同的色调变体
- **多缩放因子**：为不同的显示密度创建多种尺寸
- **批量处理**：一次性创建包含多个图像的完整 DCI 文件
- **背景色处理**：使用新的背景色选项解决透明图像的显示问题

## 工作流程示例

### 基础工作流程
```
LoadImage → DCI Image → DCI File → DCI Preview
```

### 多图像工作流程
```
LoadImage (normal) → DCI Image (normal) ──┐
LoadImage (hover)  → DCI Image (hover)  ──┼─→ DCI File ──→ Binary File Saver
LoadImage (pressed)→ DCI Image (pressed)──┘           └─→ DCI Preview
```

### 文件处理工作流程
```
Binary File Loader → DCI Preview
                  └→ Binary File Saver
```

### 调试工作流程
```
LoadImage → DCI Image → DCI Image Debug
                     └→ DCI File → DCI Preview
```

## DCI 格式规范

此扩展根据桌面规范实现 DCI 格式：
- **魔术头**："DCI\0"
- **版本**：1
- **目录结构**：`size/state.tone/scale/layer.format`
- **支持的状态**：normal、disabled、hover、pressed
- **支持的色调**：light、dark
- **支持的格式**：WebP、PNG、JPEG

## 技术细节

### DCI 文件格式实现
扩展实现了完整的 DCI 规范：

**二进制结构**：
```
DCI 头部（8 字节）：
├── 魔术（4 字节）：'DCI\0'
├── 版本（1 字节）：1
└── 文件计数（3 字节）：文件数量

文件条目（每个文件 72+ 字节）：
├── 文件类型（1 字节）：1=文件，2=目录
├── 文件名（63 字节）：以空字符结尾的 UTF-8
├── 内容大小（8 字节）：小端序 uint64
└── 内容（可变）：文件数据或目录内容
```

**目录结构**：
```
size/                    # 图标尺寸（16、32、64、128、256、512、1024）
└── state.tone/          # state: normal|disabled|hover|pressed
    └── scale/           # 缩放因子（1、1.25、1.5、2 等，支持小数）
        └── layer.format # priority.padding.palette.hue.saturation.brightness.red.green.blue.alpha.format
```

## 依赖项

- **Pillow**：图像处理和操作
- **NumPy**：ComfyUI 张量转换的数组操作
- **PyTorch**：ComfyUI 张量兼容性

## 故障排除

如果在 ComfyUI 中看不到 DCI 节点：

1. 确保已正确安装所有依赖项
2. 重启 ComfyUI
3. 检查 ComfyUI 控制台是否有错误信息
4. 确保扩展文件夹位于正确的 `custom_nodes` 目录中

## 贡献

欢迎贡献！请提交 Pull Request 或创建 Issue 来报告问题或建议新功能。

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
