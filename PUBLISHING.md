# ComfyUI Registry Publishing Guide

本文档说明如何将ComfyUI DCI扩展发布到ComfyUI官方注册表。

## 发布前准备清单

### ✅ 已完成的准备工作

1. **项目元数据文件**
   - ✅ `pyproject.toml` - 包含完整的项目元数据
   - ✅ `LICENSE` - MIT许可证文件
   - ✅ `README.md` - 详细的项目文档
   - ✅ `requirements.txt` - 依赖列表

2. **图标和资源**
   - ✅ `resources/icon.svg` - 项目图标文件

3. **自动化发布**
   - ✅ `.github/workflows/publish_action.yml` - GitHub Actions工作流

### 📋 需要手动完成的步骤

#### 1. 创建ComfyUI Registry账户

1. 访问 [Comfy Registry](https://registry.comfy.org/)
2. 创建发布者账户
3. 记录您的发布者ID（在个人资料页面 `@` 符号后面）

#### 2. 生成API密钥

1. 在Registry中为您的发布者创建API密钥
2. 安全保存API密钥

#### 3. 配置GitHub仓库

1. **更新仓库URL**：
   - 在 `pyproject.toml` 中将 `your-username` 替换为实际的GitHub用户名
   - 更新所有GitHub相关的URL

2. **设置GitHub Secret**：
   - 前往 GitHub 仓库的 Settings → Secrets and Variables → Actions
   - 创建名为 `REGISTRY_ACCESS_TOKEN` 的secret
   - 将API密钥作为值保存

#### 4. 更新pyproject.toml

在 `pyproject.toml` 文件中填入您的发布者ID：

```toml
[tool.comfy]
PublisherId = "your-publisher-id"  # 替换为您的实际发布者ID
DisplayName = "DCI Image Export Extension"
Icon = "https://raw.githubusercontent.com/your-username/comfyui-dci/master/resources/icon.svg"
```

## 发布方式

### 方式1：使用ComfyUI CLI（手动发布）

1. 安装ComfyUI CLI：
```bash
pip install comfy-cli
```

2. 在项目根目录运行：
```bash
comfy node publish
```

3. 输入您的API密钥

### 方式2：使用GitHub Actions（自动发布）

1. 完成上述配置后，每次推送 `pyproject.toml` 文件的更改都会自动触发发布
2. 也可以在GitHub Actions页面手动触发发布

## 版本管理

- 每次发布新版本时，需要更新 `pyproject.toml` 中的 `version` 字段
- 版本号必须遵循语义化版本规范（如：1.0.0, 1.0.1, 1.1.0等）
- 推送版本更改后会自动触发发布流程

## 发布后验证

1. 访问 `https://registry.comfy.org/your-publisher-id/comfyui-dci` 查看发布状态
2. 在ComfyUI Manager中搜索您的扩展
3. 测试安装和功能是否正常

## 注意事项

- 发布者ID一旦创建不能更改，请谨慎选择
- API密钥具有发布权限，请妥善保管
- 确保所有文件路径和URL都是正确的
- 图标文件大小不应超过800x400像素

## 故障排除

如果发布失败，请检查：

1. 发布者ID是否正确填写
2. API密钥是否有效
3. GitHub仓库URL是否可访问
4. 图标文件是否存在且可访问
5. pyproject.toml格式是否正确

## 联系支持

如果遇到问题，可以：
- 查看ComfyUI官方文档
- 在ComfyUI Discord社区寻求帮助
- 提交GitHub Issue
