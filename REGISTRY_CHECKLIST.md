# ComfyUI Registry 发布检查清单

## ✅ 已完成的准备工作

### 1. 项目元数据和配置文件
- ✅ **pyproject.toml** - 完整的项目元数据配置
  - 项目名称：`comfyui-dci`
  - 版本：`1.0.0`
  - 依赖项：`Pillow>=8.0.0`, `numpy>=1.19.0`
  - 许可证：MIT License
  - 完整的项目描述和关键词
  - Python版本要求：>=3.8

- ✅ **LICENSE** - MIT许可证文件
- ✅ **requirements.txt** - Python依赖声明
- ✅ **README.md** - 详细的项目文档（已更新包含Registry安装说明）

### 2. 项目资源
- ✅ **resources/icon.svg** - 项目图标（64x64 SVG格式）
- ✅ **locales/** - 国际化支持文件
- ✅ **examples/** - 示例工作流

### 3. 自动化发布
- ✅ **.github/workflows/publish_action.yml** - GitHub Actions自动发布工作流
- ✅ **PUBLISHING.md** - 详细的发布指南文档

### 4. 文档更新
- ✅ **detailed-design.md** - 添加了发布与分发设计章节
- ✅ **README.md** - 添加了Registry安装说明

## 📋 需要手动完成的步骤

### 第一步：创建ComfyUI Registry账户
1. 访问 [Comfy Registry](https://registry.comfy.org/)
2. 创建发布者账户
3. 记录发布者ID（在个人资料页面 `@` 符号后面）

### 第二步：生成API密钥
1. 在Registry中为发布者创建API密钥
2. 安全保存API密钥

### 第三步：配置GitHub仓库
1. **更新仓库URL**：
   ```bash
   # 在pyproject.toml中替换所有的"your-username"为实际GitHub用户名
   sed -i 's/your-username/实际用户名/g' pyproject.toml
   ```

2. **设置GitHub Secret**：
   - 前往 GitHub 仓库的 Settings → Secrets and Variables → Actions
   - 创建名为 `REGISTRY_ACCESS_TOKEN` 的secret
   - 将API密钥作为值保存

### 第四步：更新发布者ID
在 `pyproject.toml` 文件中填入实际的发布者ID：
```toml
[tool.comfy]
PublisherId = "your-actual-publisher-id"  # 替换为实际的发布者ID
```

### 第五步：测试发布
1. **方式1 - 使用ComfyUI CLI**：
   ```bash
   pip install comfy-cli
   comfy node publish
   ```

2. **方式2 - 使用GitHub Actions**：
   - 提交并推送 `pyproject.toml` 的更改
   - 或在GitHub Actions页面手动触发工作流

## 🔍 发布前最终检查

### 代码质量检查
- [ ] 所有Python文件无语法错误
- [ ] 所有节点可正常加载
- [ ] 示例工作流可正常执行
- [ ] 错误处理机制正常工作

### 文档完整性检查
- [ ] README.md包含完整的安装和使用说明
- [ ] 所有节点都有详细的参数说明
- [ ] 示例文件完整且可执行

### 兼容性检查
- [ ] 与最新版ComfyUI兼容
- [ ] 依赖库版本兼容性确认
- [ ] 跨平台兼容性测试（Windows/Linux/Mac）

### 发布配置检查
- [ ] pyproject.toml中所有URL都是正确的
- [ ] 图标文件可正常访问
- [ ] GitHub Actions工作流配置正确
- [ ] API密钥已正确设置

## 📈 发布后验证

### 1. Registry验证
- [ ] 访问 `https://registry.comfy.org/your-publisher-id/comfyui-dci` 确认发布成功
- [ ] 检查扩展信息显示是否正确
- [ ] 验证图标和描述是否正常显示

### 2. 安装测试
- [ ] 通过ComfyUI Manager搜索并安装扩展
- [ ] 验证所有节点正常出现在节点菜单中
- [ ] 测试基本功能是否正常工作

### 3. 用户体验验证
- [ ] 安装过程是否顺畅
- [ ] 节点分类是否合理
- [ ] 错误信息是否友好
- [ ] 文档是否易于理解

## 🚀 版本管理

### 版本号规范
- **主版本号**：重大架构变更或不兼容更新
- **次版本号**：新功能添加
- **修订版本号**：错误修复和小改进

### 发布新版本流程
1. 更新 `pyproject.toml` 中的版本号
2. 更新 README.md 中的变更说明
3. 提交并推送更改
4. GitHub Actions自动触发发布
5. 验证新版本在Registry中的可用性

## 📞 支持和反馈

### 问题报告
- GitHub Issues：用于错误报告和功能请求
- 详细的错误日志和复现步骤

### 社区支持
- ComfyUI Discord社区
- GitHub Discussions
- 用户文档和FAQ

---

**注意**：完成上述所有步骤后，您的ComfyUI DCI扩展就可以成功发布到ComfyUI Registry，供全球用户安装和使用了！
