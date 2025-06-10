# ComfyUI DCI Image Exporter Extension - 概要设计

## 1. 项目概述

### 1.1 项目目标
ComfyUI DCI Image Exporter Extension 是一个专为 ComfyUI 设计的扩展插件，旨在提供完整的 DCI (DSG Combined Icons) 格式支持，包括图像导出、文件预览和元数据分析功能。

### 1.2 核心功能
- **DCI 格式导出**: 将图像转换为符合桌面规范的 DCI 格式
- **多状态图标支持**: 支持 normal、hover、pressed、disabled 四种状态
- **多色调支持**: 支持 light 和 dark 两种色调
- **多缩放因子**: 支持小数缩放如 1x、1.25x、1.5x、2x 等多种缩放比例
- **格式兼容性**: 支持 WebP、PNG、JPEG 三种图像格式
- **可视化预览**: 提供 DCI 文件内容的网格化预览
- **元数据分析**: 深度分析 DCI 文件结构和内容
- **二进制文件处理**: 专用的二进制文件加载、保存和上传功能
- **统一节点分组**: 所有节点统一归类在"DCI"分组下，提高可发现性

## 2. 系统架构

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                    ComfyUI Framework                        │
├─────────────────────────────────────────────────────────────┤
│                  ComfyUI DCI Extension                      │
├─────────────────┬─────────────────┬─────────────────┬───────┤
│   Export Layer  │  Preview Layer  │ Analysis Layer  │Binary │
├─────────────────┼─────────────────┼─────────────────┼───────┤
│  DCI Format     │  DCI Reader     │ Metadata        │File   │
│  Builder        │  Preview Gen    │ Extractor       │I/O    │
└─────────────────┴─────────────────┴─────────────────┴───────┘

目录结构映射：
py/                 - 核心实现层
├── dci_format.py   - DCI Format Builder
├── dci_reader.py   - DCI Reader & Preview Gen
└── nodes.py        - ComfyUI节点接口层

locales/            - 国际化支持
resources/          - 静态资源
tools/              - 开发工具
tests/              - 测试套件
examples/           - 示例工作流
web_version/        - Web组件（预留）
```

### 2.2 模块划分

#### 2.2.1 导出模块 (Export Module)

##### 传统导出节点
- **DCIImageExporter**: 基础单状态图标导出
- **DCIImageExporterAdvanced**: 高级多状态图标导出
- **DCIIconBuilder**: DCI 文件构建器
- **DCIFile**: DCI 文件格式实现

##### 重构导出节点（推荐）
- **DCIImage**: 单个图像数据创建，输出结构化数据
- **DCIFileNode**: 多图像组合，生成二进制数据流
- **数据流架构**: 支持节点间二进制数据传递

#### 2.2.2 预览模块 (Preview Module)

##### 文件预览节点
- **DCIAnalysisNode**: DCI 文件内容分析和文本输出
- **DCIFileLoader**: DCI 文件加载器

##### 二进制预览节点（新增）
- **DCIPreviewFromBinary**: 从二进制数据创建预览
- **DCIReader**: DCI 文件读取和解析
- **DCIPreviewGenerator**: 预览图像生成器

#### 2.2.3 分析模块 (Analysis Module)
- **DCIMetadataExtractor**: 元数据提取和过滤
- **Directory Structure Analyzer**: 目录结构分析
- **File Content Inspector**: 文件内容检查

#### 2.2.4 二进制文件处理模块 (Binary File I/O Module)
- **BinaryFileLoader**: 二进制文件加载器
- **BinaryFileSaver**: 二进制文件保存器
- **Binary Data Structure**: 统一的二进制数据结构

## 3. 数据流设计

### 3.1 传统导出流程
```
Input Image → Tensor Conversion → PIL Image → Resize & Scale →
Format Conversion → DCI Builder → Directory Structure → DCI File
```

### 3.2 重构导出流程（推荐）
```
Input Image → DCIImage Node → DCI_IMAGE_DATA → DCIFileNode → BINARY_DATA
                                    ↓
Multiple Images → Multiple DCIImage Nodes → Multiple DCI_IMAGE_DATA → DCIFileNode
```

### 3.3 预览流程

#### 文件预览流程
```
DCI File → DCI Reader → Image Extraction → Grid Layout →
Preview Generation → Metadata Summary → Output Display
```

#### 二进制预览流程（新增）
```
BINARY_DATA → Binary Parser → Image Extraction → Grid Layout →
Preview Generation → Metadata Summary → Output Display
```

### 3.4 分析流程
```
DCI File → Structure Parsing → Metadata Extraction →
Filtering & Sorting → Detailed Analysis → Report Generation
```

### 3.5 数据流优势

#### 重构架构优势
- **模块化**: 每个节点职责单一，易于组合
- **灵活性**: 支持复杂的多图像工作流程
- **内存效率**: 二进制数据流减少文件I/O操作
- **可扩展性**: 易于添加新的处理节点

## 4. 接口设计

### 4.1 ComfyUI 节点接口
- **输入类型**: IMAGE, STRING, INT, BOOLEAN
- **输出类型**: IMAGE, STRING
- **参数验证**: 类型检查、范围验证、格式验证
- **错误处理**: 异常捕获、错误信息返回
- **节点分组**: 统一使用 "DCI" 分类，提高用户体验

### 4.2 节点分组策略
- **统一分组**: 所有 DCI 相关节点归类在 "DCI" 分组下
- **命名规范**: 使用清晰的节点显示名称
- **分类逻辑**: 按功能分为导出、预览、分析、文件处理四类
- **兼容性**: 双重注册机制确保与不同版本 ComfyUI 兼容

### 4.3 内部模块接口
- **DCIFile API**: 文件添加、目录创建、写入操作
- **DCIReader API**: 文件读取、结构解析、图像提取
- **Builder Pattern**: 渐进式构建 DCI 文件

## 5. 技术选型

### 5.1 核心依赖
- **PIL (Pillow)**: 图像处理和格式转换
- **PyTorch**: ComfyUI 张量处理
- **NumPy**: 数值计算和数组操作

### 5.2 文件格式
- **DCI 格式**: 自定义二进制格式，符合桌面规范
- **图像格式**: WebP (默认)、PNG、JPEG
- **编码方式**: UTF-8 文本编码，小端序二进制

## 6. 性能考虑

### 6.1 内存管理
- **流式处理**: 大文件分块读取
- **缓存策略**: 图像数据按需加载
- **资源释放**: 及时释放 PIL 图像对象

### 6.2 处理效率
- **批量操作**: 多图像并行处理
- **格式优化**: WebP 压缩优化
- **缩放算法**: Lanczos 重采样算法

## 7. 扩展性设计

### 7.1 格式扩展
- **新图像格式**: 模块化格式支持
- **新状态类型**: 可配置状态定义
- **新色调模式**: 动态色调支持

### 7.2 功能扩展
- **批量处理**: 多文件批量导出
- **模板系统**: 预定义配置模板
- **插件机制**: 第三方功能集成

## 8. 质量保证

### 8.1 测试策略
- **单元测试**: 核心功能模块测试
- **集成测试**: 端到端工作流测试
- **性能测试**: 大文件处理性能测试

### 8.2 错误处理
- **输入验证**: 参数类型和范围检查
- **异常处理**: 优雅的错误恢复
- **日志记录**: 详细的操作日志

## 9. 部署和维护

### 9.1 安装部署
- **依赖管理**: requirements.txt 依赖声明
- **自动安装**: ComfyUI 插件自动发现
- **版本兼容**: 向后兼容性保证

### 9.2 文档维护
- **API 文档**: 详细的接口说明
- **使用示例**: 完整的工作流示例
- **更新日志**: 版本变更记录
