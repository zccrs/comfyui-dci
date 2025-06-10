# ComfyUI DCI 图像导出扩展

一个全面的 ComfyUI 扩展，用于创建、预览和分析 DCI（DSG Combined Icons）格式文件。此扩展实现了完整的 DCI 规范，支持多状态图标、多色调、缩放因子和高级元数据分析。

## DCI 规范文档

本项目严格基于 **DCI（DSG Combined Icons）标准格式文档** 设计和实现。

### 官方规范文档
- **官方规范**：[Desktop Spec Group - 图标文件规范](https://desktopspec.org/unstable/%E5%9B%BE%E6%A0%87%E6%96%87%E4%BB%B6%E8%A7%84%E8%8C%83.html)
- **本地文档**：**[dci-specification.md](./dci-specification.md)**

### 文档特色

本项目的 `dci-specification.md` 文档基于官方规范并进行了实用性优化：

- 📋 **完整的 DCI 文件格式说明**：二进制结构、文件头、元数据格式
- 📝 **详细的图层文件命名规范**：优化后的命名格式和参数说明
- 🎨 **颜色调整算法说明**：精确的颜色计算公式和示例
- 💡 **实际应用示例**：完整的目录结构和文件名示例
- 🔍 **查找规则和回退机制**：图标资源的匹配和选择逻辑
- ⚡ **Alpha8格式深度解析**：基于 [dtkgui实现](https://github.com/linuxdeepin/dtkgui) 的技术细节

### 标准兼容性

本工具完全遵循 DCI 标准规范：
- ✅ **文件格式兼容**：生成的DCI文件完全符合官方二进制格式规范
- ✅ **目录结构标准**：严格按照 `<图标大小>/<图标状态>.<色调类型>/<缩放倍数>/<图层文件>` 结构
- ✅ **文件命名规范**：完整支持 `优先级.外边框p.调色板.色调_饱和度_亮度_红_绿_蓝_透明度.格式[.alpha8]` 格式
- ✅ **文件名省略规则**：支持DCI规范的文件名优化策略，默认值可省略（如`1.webp`）
- ✅ **图层系统支持**：完整实现优先级、外边框、调色板和颜色调整功能
- ✅ **Alpha8优化**：支持基于灰度格式的alpha通道存储优化
- ✅ **向后兼容**：同时支持简化文件名和完整文件名格式

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
- DCI_StructureNode (DCI Structure Preview)

#### Preview（预览）
- DCI_ImagePreview (DCI Image Preview)

#### DCI/Files（文件处理）
- DCI_BinaryFileLoader (Binary File Loader)
- DCI_BinaryFileSaver (Binary File Saver)



### 可用节点详细说明

#### 1. DCI Image（DCI 图像）
**节点类别**：`DCI/Export`
**功能描述**：创建单个 DCI 图像数据，输出元数据而不是直接创建文件，提供更灵活的工作流程。完全支持 DCI 规范中的图层系统，包括优先级、外边框、调色板和颜色调整功能。

**必需输入参数：**
- **`image`** (IMAGE)：ComfyUI 图像张量
- **`icon_size`** (INT)：图标尺寸（16-1024像素），默认256
- **`icon_state`** (COMBO)：图标状态（normal/disabled/hover/pressed），默认normal
- **`scale`** (FLOAT)：缩放因子（0.1-10.0），默认1.0，支持小数如1.25

**可选输入参数（高级设置，默认折叠）：**

*基础设置：*
- **`tone_type`** (COMBO)：色调类型（light/dark），默认light
- **`image_format`** (COMBO)：图像格式（webp/png/jpg），默认webp

*背景色设置：*
- **`background_color`** (COMBO)：背景色处理（transparent/white/black/custom），默认transparent
- **`custom_bg_r`** (INT)：自定义背景色红色分量（0-255），默认255
- **`custom_bg_g`** (INT)：自定义背景色绿色分量（0-255），默认255
- **`custom_bg_b`** (INT)：自定义背景色蓝色分量（0-255），默认255

*图层设置（符合 DCI 规范）：*
- **`layer_priority`** (INT)：图层优先级（1-100），默认1，数值越大绘制越靠上
- **`layer_padding`** (INT)：外边框值（0-100），默认0，用于阴影效果等
- **`palette_type`** (COMBO)：调色板类型（none/foreground/background/highlight_foreground/highlight），默认none

*颜色调整参数（-100 到 100）：*
- **`hue_adjustment`** (INT)：色调调整，默认0
- **`saturation_adjustment`** (INT)：饱和度调整，默认0
- **`brightness_adjustment`** (INT)：亮度调整，默认0
- **`red_adjustment`** (INT)：红色分量调整，默认0
- **`green_adjustment`** (INT)：绿色分量调整，默认0
- **`blue_adjustment`** (INT)：蓝色分量调整，默认0
- **`alpha_adjustment`** (INT)：透明度调整，默认0

**输出：**
- **`dci_image_data`** (DCI_IMAGE_DATA)：包含路径、内容、元数据和图层信息的字典数据

**背景色处理说明：**
- **transparent**：保持原始透明度（仅PNG和WebP支持）
- **white**：将透明背景替换为白色
- **black**：将透明背景替换为黑色
- **custom**：使用自定义RGB颜色作为背景

**图层系统说明：**
- **图层优先级**：控制图层绘制顺序，数值越大越靠上层
- **外边框**：为图标添加外围不被控件覆盖的区域，常用于阴影效果
- **调色板**：定义图标的颜色填充方式，支持前景色、背景色、高亮色等
- **颜色调整**：精确控制图标的色调、饱和度、亮度和RGBA分量
- **文件命名**：自动按照DCI规范生成图层文件名，格式为 `优先级.外边框p.调色板.色调_饱和度_亮度_红_绿_蓝_透明度.格式`
- **文件名省略**：支持DCI规范的优化策略，当参数为默认值时可省略（如简化为`1.webp`）
- **向后兼容**：同时支持完整文件名和简化文件名格式，确保与真实DCI文件兼容

#### 2. DCI File（DCI 文件）
**节点类别**：`DCI/Export`
**功能描述**：接收多个 DCI Image 输出并组合成完整的 DCI 文件，专注于生成二进制数据。如需保存文件，请使用 Binary File Saver 节点。

**可选输入参数：**
- **`dci_image_1` 到 `dci_image_12`** (DCI_IMAGE_DATA)：最多12个DCI图像数据

**输出：**
- **`dci_binary_data`** (BINARY_DATA)：DCI文件的二进制数据

#### 3. DCI Preview（DCI 预览）
**节点类别**：`DCI/Preview`
**功能描述**：直接在节点内显示 DCI 文件内容的可视化预览和详细元数据信息。专门用于预览 DCI 二进制数据，现支持将Light和Dark相关内容分开显示。

**必需输入参数：**
- **`dci_binary_data`** (BINARY_DATA)：DCI 文件的二进制数据

**可选输入参数：**
- **`light_background_color`** (COMBO)：Light主题预览背景色，默认light_gray
- **`dark_background_color`** (COMBO)：Dark主题预览背景色，默认dark_gray
- **`text_font_size`** (INT)：文本字号大小（8-50像素），默认18，同时控制预览图像中的字体大小和文本摘要的格式

**背景颜色选项：**
支持20种预设颜色，包括：
- **基础色**：light_gray、dark_gray、white、black
- **特殊背景**：transparent、checkerboard
- **彩色选项**：blue、green、red、yellow、cyan、magenta、orange、purple、pink、brown、navy、teal、olive、maroon

**节点内预览功能：**
- **双列布局**：Light主题图标在左列，Dark主题图标在右列
- **独立背景设置**：Light和Dark主题可设置不同的背景颜色
- **丰富背景色选项**：每种主题支持20种预设背景色，包括特殊的透明和棋盘格背景
- **自适应文本格式**：根据字体大小调整文本显示格式，较大字体使用更紧凑的布局
- **文件路径分组显示**：Light、Dark和其他色调图标的路径分别显示
- **预览图像标签**：每个图标下方显示详细信息，包括：
  - **文件路径**（第一行）：显示DCI内部的完整路径（如：64/normal.light/1.0.0.0.0.0.0.0.0.0.png）
  - 图标尺寸、状态、缩放因子
  - 文件大小
  - **注意**：不显示色调(tone)字段，因为已按Light/Dark分列显示；不显示格式(format)字段，因为文件名已包含格式信息
- **详细元数据显示**：在节点内显示全面的文件信息，包括：
  - 图标尺寸、状态、色调、缩放因子
  - 图像格式、文件大小、实际尺寸
  - 完整的DCI内部路径和文件名
  - 每个图像的优先级和详细属性
  - 统计汇总信息和文件路径列表

**输出：**
- 无输出（所有预览内容直接在节点内显示）

**注意**：此节点专门用于处理二进制数据输入。不需要手动设置列数，默认将Light和Dark内容分开显示在两列，Light主题图标固定在左侧列，Dark主题图标固定在右侧列。文本格式会根据字体大小自动调整，提供最佳阅读体验。背景颜色选择简化为预设选项，移除了自定义RGB设置以提供更好的用户体验。

#### 4. DCI Image Preview（DCI 图像预览）
**节点类别**：`Preview`
**功能描述**：专门用于预览单个 DCI 图像数据，提供简洁的图像预览功能。

**必需输入参数：**
- **`dci_image_data`** (DCI_IMAGE_DATA)：DCI 图像数据

**可选输入参数：**
- **`preview_background`** (COMBO)：预览背景类型（transparent/white/black/checkerboard），默认checkerboard

**节点功能特性：**
- **图像预览**：直接在节点界面中显示处理后的图像
- **智能背景显示**：支持透明、白色、黑色和棋盘格背景，便于查看透明图像
- **简洁界面**：专注于图像显示，不显示复杂的调试信息

**输出：**
- 无输出（图像预览直接在节点内显示）

**使用场景：**
- 快速预览DCI图像的最终效果
- 验证图像背景处理效果
- 检查图像质量和显示效果
- 在工作流程中进行图像效果确认

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

#### 7. DCI Structure Preview（DCI 结构预览）
**节点类别**：`DCI/Preview`
**功能描述**：以树状结构详细展示DCI文件的内部组织结构和元信息，专门用于分析和调试DCI文件内容。

**必需输入参数：**
- **`dci_binary_data`** (BINARY_DATA)：DCI 文件的二进制数据

**可选输入参数：**
- **`show_file_details`** (BOOLEAN)：是否显示文件详细信息，默认True
- **`show_layer_metadata`** (BOOLEAN)：是否显示图层元数据，默认True
- **`show_file_sizes`** (BOOLEAN)：是否显示文件大小，默认True
- **`compact_mode`** (BOOLEAN)：是否使用紧凑模式，默认False

**节点功能特性：**

*统计信息显示：*
- **文件概览**：总图像数量、总文件大小
- **尺寸分布**：各种图标尺寸的数量统计
- **状态分布**：normal、hover、pressed、disabled状态的分布
- **色调分布**：light、dark色调的分布情况
- **格式统计**：webp、png、jpg等格式的使用情况
- **缩放比例**：1x、2x、3x等缩放比例的分布

*树状结构展示：*
```
DCI File Structure:
├─ (Size/State.Tone/Scale/Layer)
├── 64
│   ├── normal.light
│   │   └── 1
│   │       └── 1.webp (588B)
│   │             📊 优先级: 1
│   └── hover.light
│       └── 1
│           └── 2.5p.0.10_20_30_-10_15_-5_25.png (774B)
│                 📊 优先级: 2
│                 📐 外边框: 5px
│                 🎨 调色板: 前景色
│                 🌈 颜色调整: 色调+10%, 饱和度+20%, 亮度+30%
└── 128
    └── normal.light
        ├── 1
        │   └── 1.webp (650B)
        ├── 2
        │   └── 1.webp (1.2KB)
        └── 3
            └── 1.webp (1.7KB)
```

*智能元数据解析：*
- **图层优先级**：解析文件名中的优先级信息
- **外边框设置**：识别外边框像素值（如5p表示5像素外边框）
- **调色板类型**：解析调色板设置（无调色板、前景色、背景色、高亮前景色、高亮色）
- **颜色调整参数**：详细解析色调、饱和度、亮度、RGB、透明度调整
- **Alpha8格式识别**：特别标识用于调色板优化的Alpha8格式文件
- **文件名省略支持**：正确解析DCI规范中的简化文件名格式

*显示选项控制：*
- **紧凑模式**：隐藏详细的图层元数据，只显示文件结构
- **文件大小显示**：可选择是否显示每个文件的大小信息
- **图层元数据**：可选择是否显示详细的图层属性解析
- **人性化格式**：文件大小自动格式化为B、KB、MB单位

**输出：**
- 无输出（所有结构信息直接在节点内以文本形式显示）

**使用场景：**
- **DCI文件分析**：深入了解DCI文件的内部结构和组织方式
- **调试和验证**：验证DCI文件是否按照预期的结构生成
- **规范学习**：通过实际文件了解DCI规范的实现细节
- **文件对比**：比较不同DCI文件的结构差异
- **元数据检查**：验证图层文件名中的元数据是否正确设置
- **性能分析**：查看文件大小分布，优化DCI文件结构

**技术特性：**
- **完整DCI规范支持**：支持DCI 1.1规范的所有特性
- **智能文件名解析**：按照DCI规范解析复杂的图层文件名
- **省略格式兼容**：支持简化文件名和完整文件名格式
- **自然排序**：按照自然顺序排列文件和目录
- **Unicode支持**：正确处理UTF-8编码的文件名
- **错误容错**：对格式不正确的文件名提供友好的错误处理

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

1. **预览单个 DCI 图像**：
   - 使用 `DCI Image Preview` 节点快速查看单个 DCI 图像的最终效果
   - 验证背景色处理效果和图像质量
   - 检查图像的视觉效果

2. **工作流程验证**：
   - 在DCI图像创建后立即预览结果
   - 验证图像处理效果是否符合预期
   - 检查不同背景下的图像显示效果

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

### 预览工作流程
```
LoadImage → DCI Image → DCI Image Preview
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
