# 节点连接问题修复说明

## 问题描述

在之前的版本中，DCI Preview 和 Binary File Saver 节点无法接收 DCI File 节点输出的二进制数据，连线时连不上去。

## 问题原因

数据类型不匹配导致的连接问题：

- **DCIFileNode** 输出类型：`DCI_BINARY_DATA`
- **DCIPreviewNode** 期望输入类型：`BINARY_DATA`
- **BinaryFileSaver** 期望输入类型：`BINARY_DATA`

ComfyUI 的类型系统不允许不同类型之间直接连接，因此出现了连线失败的问题。

## 修复方案

### 1. 统一数据类型

将所有二进制数据相关节点统一使用 `BINARY_DATA` 类型：

```python
# 修复前
DCIFileNode.RETURN_TYPES = ("DCI_BINARY_DATA",)

# 修复后
DCIFileNode.RETURN_TYPES = ("BINARY_DATA",)
```

### 2. 简化类型系统

移除不必要的 `DCI_BINARY_DATA` 类型，只保留两个核心数据类型：

- `DCI_IMAGE_DATA`：用于单个DCI图像数据传递
- `BINARY_DATA`：用于所有二进制数据传递（包括DCI文件）

### 3. 更新节点兼容性

现在所有节点都可以正确连接：

```
✅ DCIFileNode → DCIPreviewNode
✅ DCIFileNode → BinaryFileSaver
✅ BinaryFileLoader → DCIPreviewNode
✅ BinaryFileLoader → BinaryFileSaver
```

## 修复验证

### 类型兼容性测试

```bash
python tests/test_node_connectivity.py
```

测试结果：
```
...
----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

### 工作流验证

现在支持以下完整工作流：

1. **DCI创建和预览**：
   ```
   DCIImage → DCIFileNode → DCIPreviewNode
   ```

2. **DCI创建和保存**：
   ```
   DCIImage → DCIFileNode → BinaryFileSaver
   ```

3. **DCI加载和预览**：
   ```
   BinaryFileLoader → DCIPreviewNode
   ```

## 影响范围

### 代码变更
- `py/nodes.py`：修改DCIFileNode输出类型
- `__init__.py`：移除DCI_BINARY_DATA类型注册
- `tests/`：更新相关测试文件

### 文档更新
- `README.md`：更新节点类型说明
- `detailed-design.md`：更新数据结构设计
- `preliminary-design.md`：更新数据流设计

### 向后兼容性
- ✅ 现有的DCI图像创建功能完全兼容
- ✅ 现有的二进制文件处理功能完全兼容
- ✅ 所有节点功能保持不变，只是连接性得到改善

## 使用建议

1. **更新ComfyUI工作流**：如果你有使用旧版本创建的工作流，可能需要重新连接节点
2. **测试连接**：确认所有节点都能正确连接
3. **验证功能**：测试完整的DCI创建、预览和保存流程

## 技术细节

### BINARY_DATA类型说明

```python
BINARY_DATA = bytes  # 直接的二进制数据内容
```

- 适用于所有二进制文件，包括DCI文件
- 不包含额外的元数据包装，保持数据纯净性
- 所有二进制处理节点都使用此统一类型
- 确保最大的兼容性和灵活性

### 数据流优化

修复后的数据流更加简洁高效：

```
输入图像 → DCI图像数据 → DCI文件二进制 → 预览/保存
   ↓           ↓            ↓           ↓
 IMAGE → DCI_IMAGE_DATA → BINARY_DATA → 显示/文件
```

这个修复确保了所有DCI相关节点都能正确连接和协作，提供了完整的DCI文件处理工作流。
