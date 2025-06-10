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
- ✅ **完整中文本地化**：所有界面元素完全支持中文显示
- ✅ **增强错误处理**：详细的错误报告和调试信息
- ✅ **棋盘格背景支持**：透明图像预览的棋盘格背景
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

### 国际化支持
- **完整中文界面**：所有节点名称、参数名、输出名均支持中文显示
- **双语支持**：支持中文和英文界面切换
- **本地化翻译**：所有用户界面元素都经过专业翻译
- **颜色名称翻译**：20种颜色名称完全本地化（浅灰色、蓝色、红色等）
- **选项值翻译**：所有下拉选项和默认值都支持中文显示

### 错误处理与调试
- **详细错误报告**：在界面上直接显示详细的错误信息和解决建议
- **可视化错误预览**：DCI预览节点在出错时生成包含错误信息的红色预览图
- **分析节点调试**：DCI分析节点输出详细的错误日志和数据状态
- **参数兼容性**：同时支持翻译后和原始参数名，确保向后兼容

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

本扩展提供了 8 个 ComfyUI 节点，所有节点都统一归类在 **"DCI"** 分组下，并按功能分为三个子分类：

### 节点分组

#### DCI/Export（导出）
- DCI_Image (DCI Image) - 完整功能的DCI图像创建节点
- DCI_SampleImage (DCI Sample Image) - 简化的DCI图像创建节点
- DCI_FileNode (DCI File)

#### DCI/Preview（预览）
- DCI_PreviewNode (DCI Preview)
- DCI_ImagePreview (DCI Image Preview)

#### DCI/Analysis（分析）
- DCI_Analysis (DCI Analysis)

#### DCI/Files（文件处理）
- DCI_BinaryFileLoader (Binary File Loader)
- DCI_BinaryFileSaver (Binary File Saver)
- DCI_FileSaver (DCI File Saver)



### 可用节点详细说明

#### 1. DCI Image（DCI 图像）
**节点类别**：`DCI/Export`
**功能描述**：创建单个 DCI 图像数据，输出元数据而不是直接创建文件，提供更灵活的工作流程。完全支持 DCI 规范中的图层系统，包括优先级、外边框、调色板和颜色调整功能。

**必需输入参数：**
- **`image`** (IMAGE)：ComfyUI 图像张量
- **`icon_size`** (INT)：图标尺寸（16-1024像素），默认256
- **`icon_state`** (COMBO)：图标状态（normal/disabled/hover/pressed），默认normal
- **`scale`** (FLOAT)：缩放因子（0.1-10.0），默认1.0，支持小数如1.25

**可选输入参数（高级设置）：**

*基础设置：*
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

#### 2. DCI Sample Image（DCI 简单图像）
**节点类别**：`DCI/Export`
**功能描述**：创建简化的 DCI 图像数据，只包含最基本的参数设置，适合大多数常见使用场景。相比完整的 DCI Image 节点，此节点界面更简洁，参数更少。

**必需输入参数：**
- **`image`** (IMAGE)：ComfyUI 图像张量
- **`icon_size`** (INT)：图标尺寸（16-1024像素），默认256
- **`icon_state`** (COMBO)：图标状态（normal/disabled/hover/pressed），默认normal
- **`scale`** (FLOAT)：缩放因子（0.1-10.0），默认1.0，支持小数如1.25
- **`tone_type`** (COMBO)：色调类型（light/dark），默认light
- **`image_format`** (COMBO)：图像格式（webp/png/jpg），默认webp

**输出：**
- **`dci_image_data`** (DCI_IMAGE_DATA)：包含路径、内容、元数据的字典数据

**节点特点：**
- **简化界面**：只显示最常用的5个基本参数，界面简洁易用
- **默认设置**：所有高级参数使用合理的默认值（优先级1、无外边框、无调色板、无颜色调整）
- **透明背景**：默认保持图像原始透明度，适合大多数图标制作场景
- **快速创建**：适合快速创建标准DCI图像，无需复杂配置

**使用场景：**
- 快速创建标准图标，无需复杂的图层设置
- 批量处理多个图标文件
- 初学者或不需要高级功能的用户
- 简单的图标转换和格式化工作

#### 3. DCI File（DCI 文件）
**节点类别**：`DCI/Export`
**功能描述**：接收多个 DCI Image 输出并组合成完整的 DCI 文件，专注于生成二进制数据。如需保存文件，请使用 Binary File Saver 节点。

**可选输入参数：**
- **`dci_image_1` 到 `dci_image_12`** (DCI_IMAGE_DATA)：最多12个DCI图像数据

**输出：**
- **`dci_binary_data`** (BINARY_DATA)：DCI文件的二进制数据

#### 4. DCI Preview（DCI 预览）
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
- **图标边框显示**：每个图标周围自动绘制细线边框，清晰显示图标的实际范围和尺寸
  - **智能边框颜色**：根据背景颜色亮度自动选择对比色边框（浅色背景用深色边框，深色背景用浅色边框）
  - **精确范围指示**：边框紧贴图标边缘，准确显示图标的像素边界
  - **多背景适配**：在所有背景颜色下都能清晰显示边框效果
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

#### 5. DCI Image Preview（DCI 图像预览）
**节点类别**：`DCI/Preview`
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

#### 6. Binary File Loader（二进制文件加载器）
**节点类别**：`DCI/Files`
**功能描述**：从文件系统加载二进制文件，专为处理 DCI 图标文件等二进制数据设计。

**可选输入参数：**
- **`file_path`** (STRING)：要加载的文件路径，默认空字符串

**输出：**
- **`binary_data`** (BINARY_DATA)：文件的二进制内容（bytes 类型）
- **`file_path`** (STRING)：加载文件的完整路径

#### 7. Binary File Saver（二进制文件保存器）
**节点类别**：`DCI/Files`
**功能描述**：将二进制数据保存到文件系统，支持自定义输出路径和目录。

**必需输入参数：**
- **`binary_data`** (BINARY_DATA)：要保存的二进制数据
- **`file_name`** (STRING)：目标文件名，默认"binary_file"

**可选输入参数：**
- **`output_directory`** (STRING)：输出目录，默认使用 ComfyUI 输出目录

**输出：**
- **`saved_path`** (STRING)：实际保存的文件路径

#### 8. DCI File Saver（DCI 文件保存器）
**节点类别**：`DCI/Files`
**功能描述**：专门用于保存DCI文件的高级文件保存器，具有智能文件名解析、前缀后缀支持和跨平台路径处理功能。

**必需输入参数：**
- **`binary_data`** (BINARY_DATA)：要保存的DCI二进制数据
- **`input_filename`** (STRING)：输入文件名或路径，默认"icon.png"

**可选输入参数：**
- **`output_directory`** (STRING)：输出目录，默认使用 ComfyUI 输出目录
- **`filename_prefix`** (STRING)：文件名前缀，默认空字符串
- **`filename_suffix`** (STRING)：文件名后缀，默认空字符串

**输出：**
- **`saved_filename`** (STRING)：保存后的文件名（不含路径）
- **`saved_full_path`** (STRING)：保存后的完整文件路径

**智能文件名解析功能：**

*路径处理：*
- **跨平台兼容**：自动处理Windows（`\`）和Linux（`/`）路径分隔符
- **路径提取**：从完整路径中自动提取文件名部分
- **示例**：`/home/user/icon.png` → `icon.dci`，`C:\Users\test\image.webp` → `image.dci`

*扩展名处理：*
- **智能替换**：自动识别并移除常见图像扩展名（webp、png、jpg、jpeg、apng、gif、bmp、tiff、tif）
- **大小写不敏感**：支持大写和小写扩展名（如PNG、jpg、JPEG等）
- **DCI扩展名**：自动添加`.dci`扩展名
- **示例**：`a.png` → `a.dci`，`icon.WEBP` → `icon.dci`

*前缀后缀功能：*
- **灵活命名**：支持为文件名添加自定义前缀和后缀
- **示例**：输入`a.png`，前缀`prefix-`，后缀`-suffix` → `prefix-a-suffix.dci`
- **空值处理**：前缀或后缀为空时自动忽略

*特殊情况处理：*
- **空输入**：输入为空时使用默认文件名`icon.dci`
- **纯路径**：输入只是路径分隔符时使用默认文件名
- **无扩展名**：没有扩展名的文件名直接添加`.dci`扩展名
- **非图像扩展名**：保留非图像扩展名，如`file.txt` → `file.txt.dci`

**使用场景：**
- **批量DCI文件保存**：根据原始图像文件名自动生成对应的DCI文件名
- **工作流程自动化**：在图像处理工作流中自动保存DCI文件
- **文件名标准化**：统一DCI文件的命名规范，添加项目前缀或版本后缀
- **跨平台开发**：在不同操作系统间保持一致的文件名处理逻辑

**技术特性：**
- **路径安全**：自动处理路径分隔符，避免跨平台兼容性问题
- **文件名清理**：确保生成的文件名符合文件系统要求
- **错误处理**：对无效输入提供友好的默认处理
- **双输出设计**：同时提供文件名和完整路径，满足不同使用需求

#### 9. DCI Analysis（DCI 分析）
**节点类别**：`DCI/Analysis`
**功能描述**：以树状结构详细分析DCI文件的内部组织结构和元信息，输出文本格式的分析结果，专门用于分析和调试DCI文件内容。

**必需输入参数：**
- **`dci_binary_data`** (BINARY_DATA)：DCI 文件的二进制数据

**节点功能特性：**

*树状结构展示：*
```
└── 32
    └── normal.dark
        └── 1
            └── 1.0.0.0.0.0.0.0.0.0.png
                    [缩放: 1x]
                    [优先级: 1]
                    [调色板: 前景色]
```

*智能路径解析：*
- **目录结构解析**：正确解析DCI文件内部的目录结构（size/state.tone/scale）
- **文件名分离**：智能处理DCIReader返回的独立path和filename字段
- **路径组件识别**：准确识别尺寸、状态.色调、缩放因子等路径组件
- **兼容性处理**：适配DCIReader的数据结构，确保正确的树形结构生成

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
- **`analysis_text`** (STRING)：包含完整分析结果的文本字符串

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

### 预览系统优化

#### 动态文本宽度计算
DCI Preview 节点现在支持智能的文本宽度计算，解决了长文件路径显示不全的问题：

**主要改进**：
- **动态宽度计算**：根据实际文本内容计算所需的最大宽度，而不是固定使用图像尺寸
- **文本换行支持**：当文本仍然过长时，自动进行智能换行处理
- **路径优化显示**：特别优化了长文件路径的显示效果
- **字体测量**：使用实际字体进行精确的文本宽度测量
- **自适应布局**：预览网格的单元格宽度自动适应文本内容需求

**技术实现**：
```python
# 计算所需的最大文本宽度
max_text_width = self._calculate_max_text_width(sorted_images)

# 单元格宽度同时考虑图像和文本需求
cell_width = max(max_image_size + margin * 2, max_text_width + margin * 2)

# 智能文本换行处理
wrapped_lines = self._wrap_text(line, text_width, font, draw)
```

**用户体验提升**：
- ✅ 长文件路径完整显示，不再被截断
- ✅ 自动换行保持可读性
- ✅ 预览网格自动调整尺寸
- ✅ 保持原有的视觉布局和美观性

#### 节点界面优化
DCI Image 节点现在采用更清晰的参数组织方式，提升用户体验：

**主要改进**：
- **核心参数前置**：将最常用的参数（icon_size、icon_state、scale、tone_type）放在必需参数区域
- **高级参数分组**：所有高级选项使用 `adv_` 前缀标识，便于识别和管理
- **简化界面**：默认情况下只显示核心参数，减少界面复杂度
- **逻辑分组**：高级参数按功能分为背景色设置、图层设置、颜色调整三个逻辑组

**参数组织结构**：
```
必需参数：
├── image (图像输入)
├── icon_size (图标尺寸)
├── icon_state (图标状态)
├── scale (缩放因子)
└── tone_type (色调类型)

可选参数：
├── image_format (图像格式)
└── 高级设置 (adv_ 前缀)
    ├── 背景色设置
    ├── 图层属性
    └── 颜色调整
```

**使用建议**：
- 🎯 **新用户**：只需关注必需参数和 image_format，即可创建基本的DCI图像
- 🎯 **高级用户**：使用 adv_ 前缀参数进行精细控制和专业定制
- 🎯 **批量处理**：核心参数的简化使得批量创建图标更加高效

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

### 已知问题和修复

#### DCIAnalysis 节点输出为空（已修复）
**问题描述**：DCIAnalysis 节点在某些情况下可能输出空字符串，无法显示DCI文件的树形结构。

**原因**：节点期望的路径格式与DCIReader实际返回的数据结构不匹配。DCIReader将目录路径和文件名分别存储在`path`和`filename`字段中，而不是组合在一起。

**修复方案**：
- 更新路径解析逻辑，正确处理独立的`path`和`filename`字段
- 调整路径组件解析，期望3个部分（size/state.tone/scale）而不是4个
- 确保与DCIReader的数据结构完全兼容

**修复状态**：✅ 已在最新版本中修复

**验证方法**：
```python
# 测试DCIAnalysis节点是否正常工作
from py.nodes.structure_node import DCIAnalysis
analysis_node = DCIAnalysis()
result = analysis_node._execute(dci_binary_data)
# 应该返回包含树形结构的非空字符串
```

## 贡献

欢迎贡献！请提交 Pull Request 或创建 Issue 来报告问题或建议新功能。

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
