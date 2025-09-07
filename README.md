# 🚀 BakaGit - 笨蛋都会用的Git图形化工具

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.9.1-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#)

> 一个专为Git初学者设计的简单易用的图形化Git管理工具，让复杂的Git操作变得简单直观！

## ✨ 主要特性

### 🎨 **美观的界面设计**
- 🌙 专业的深色主题，保护眼睛
- 📱 现代化的Material Design风格界面
- 🎯 直观的操作布局，降低学习成本

### 🔧 **完整的Git功能**
- 📁 **仓库管理**：打开、初始化、克隆仓库
- 🔄 **文件操作**：暂存、取消暂存、查看diff
- 💾 **提交管理**：智能提交界面，支持提交历史浏览
- 🌿 **分支操作**：创建、切换、合并、删除分支
- 🏷️ **标签管理**：创建、查看、推送、删除标签
- 🌐 **远程操作**：推送、拉取、获取、远程仓库管理

### ⚙️ **智能配置**
- 🛠️ **Git配置**：用户信息、全局设置、仓库配置
- 🎯 **一键设置**：快速设置GitHub等远程仓库
- 🔧 **灵活配置**：支持多种Git工作流

### 💡 **贴心功能**
- 📊 实时状态显示
- 🔍 详细的操作日志
- ⚡ 快捷键支持
- 🛡️ 安全的操作确认

## 📸 界面预览

### 主界面
![主界面](docs/images/main-interface.png)

### 分支管理
![分支管理](docs/images/branch-management.png)

### 远程操作
![远程操作](docs/images/remote-operations.png)

## 🚀 快速开始

### 📋 系统要求
- **操作系统**：Windows 10/11, macOS 10.14+, Linux
- **Python**：3.8 或更高版本
- **内存**：最低 512MB RAM
- **存储**：约 50MB 磁盘空间

### 📦 安装方法

#### 方法一：直接运行（推荐）
```bash
# 1. 克隆仓库
git clone https://github.com/JoyinJoester/BakaGit.git
cd BakaGit

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
python -m src.bakagit.main
```

#### 方法二：开发安装
```bash
# 克隆仓库
git clone https://github.com/JoyinJoester/BakaGit.git
cd BakaGit

# 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行程序
python -m src.bakagit.main
```

### 🎯 快速使用

1. **首次使用**：
   - 启动BakaGit
   - 使用 `工具` → `Git配置` 设置用户信息
   - 通过 `文件` → `打开仓库` 打开现有项目

2. **设置远程仓库**：
   - 使用 `工具` → `设置远程仓库` 
   - 输入GitHub仓库地址
   - 一键完成配置

3. **日常操作**：
   - 在 `📄 文件状态` 标签页管理文件
   - 在 `✍️ 增强提交` 标签页提交代码
   - 在 `🌐 远程操作` 标签页同步代码

## 📖 详细功能说明

### 🔧 工具菜单功能

#### Git配置
- **用户信息**：设置姓名和邮箱
- **全局设置**：编辑器、合并工具、别名配置
- **仓库设置**：当前仓库特定配置

#### 初始化仓库
- 选择目录位置
- 自动创建README.md、.gitignore、LICENSE文件
- 支持初始提交

#### 设置远程仓库
- 一键设置GitHub/GitLab等远程仓库
- 自动配置推送地址
- 支持立即推送当前分支

### 📁 文件管理

#### 文件状态标签页
- 📊 **实时状态**：显示修改、新增、删除的文件
- 🔄 **批量操作**：全选、批量暂存/取消暂存
- 👁️ **差异查看**：双击文件查看详细变更

#### 暂存区管理
- ➕ 暂存选中文件
- ➖ 取消暂存文件
- 🔍 查看暂存内容

### ✍️ 提交管理

#### 增强提交界面
- 📝 智能提交信息编辑器
- 📋 提交模板和常用信息
- 🔍 暂存文件预览
- ✅ 一键提交

#### 提交历史
- 📚 完整的提交记录
- 🔍 提交信息搜索
- 📊 图形化分支显示
- 📄 提交详情查看

### 🌿 分支管理

#### 分支操作
- ➕ **创建分支**：基于当前分支或指定提交
- 🔄 **切换分支**：安全的分支切换
- 🔀 **合并分支**：智能合并策略
- ❌ **删除分支**：本地和远程分支删除

#### 分支视图
- 🌳 分支关系图
- 📊 分支状态显示
- 🏷️ 当前分支标识

### 🏷️ 标签管理

#### 标签操作
- 🏷️ **创建标签**：轻量标签和注释标签
- 📤 **推送标签**：推送到远程仓库
- 👁️ **查看标签**：标签详情和关联提交
- ❌ **删除标签**：本地和远程标签删除

### 🌐 远程操作

#### 远程仓库管理
- ➕ **添加远程**：支持多个远程仓库
- ❌ **删除远程**：清理无用远程仓库
- 🔍 **查看远程**：远程仓库信息和URL

#### 同步操作
- 📤 **推送（Push）**：推送本地更改到远程
- 📥 **拉取（Pull）**：从远程获取并合并更改
- 📡 **获取（Fetch）**：仅获取远程更改，不合并

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+O` | 打开仓库 |
| `Ctrl+Shift+N` | 初始化仓库 |
| `F5` | 刷新仓库状态 |
| `Ctrl+A` | 暂存所有文件 |
| `Ctrl+M` | 显示提交页面 |
| `Ctrl+P` | 推送到远程 |
| `Ctrl+L` | 从远程拉取 |
| `Ctrl+B` | 创建分支 |
| `Ctrl+T` | 创建标签 |
| `Ctrl+1` | 文件状态标签页 |
| `Ctrl+2` | 增强提交标签页 |
| `Ctrl+3` | 提交历史标签页 |
| `Ctrl+4` | 分支管理标签页 |
| `Ctrl+5` | 远程操作标签页 |
| `Ctrl+6` | 标签管理标签页 |
| `Ctrl+,` | 打开设置 |
| `F1` | 显示快捷键帮助 |
| `Ctrl+Q` | 退出程序 |

## 🛠️ 开发说明

### 🏗️ 项目结构
```
BakaGit/
├── src/bakagit/           # 主要源代码
│   ├── core/              # 核心功能模块
│   │   ├── git_manager.py # Git操作管理
│   │   └── config.py      # 配置管理
│   ├── gui/               # 用户界面
│   │   ├── main_window.py # 主窗口
│   │   └── dialogs/       # 对话框
│   └── main.py            # 程序入口
├── tests/                 # 测试文件
├── docs/                  # 文档
├── requirements.txt       # 依赖清单
└── README.md              # 项目说明
```

### 🔧 技术栈
- **GUI框架**：PyQt6 6.9.1
- **Git操作**：GitPython 3.1.45
- **配置管理**：PyYAML
- **Python版本**：3.8+

### 🧪 运行测试
```bash
# 运行基础测试
python tests/test_basic.py

# 测试主窗口
python debug_main_window.py

# 测试远程功能
python test_add_remote.py
```

### 🔍 代码风格
- 使用Python PEP 8编码规范
- 详细的注释和文档字符串
- 模块化设计，易于扩展

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 🐛 报告问题
- 在[Issues](https://github.com/JoyinJoester/BakaGit/issues)页面报告bug
- 请详细描述问题和复现步骤
- 包含您的操作系统和Python版本信息

### 💡 功能建议
- 在Issues中提出新功能建议
- 描述功能的使用场景和价值
- 欢迎提供设计草图或原型

### 📝 代码贡献
1. Fork这个仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建Pull Request

## 📋 更新日志

### v0.1.0 (2025-01-07)
- 🎉 首次发布
- ✨ 完整的Git图形化操作界面
- 🎨 深色主题和现代化设计
- 🔧 Git配置和远程仓库管理
- 📱 响应式布局和多标签页设计

## 🔗 相关链接

- 📚 [用户手册](docs/user-guide.md)
- 🔧 [开发文档](docs/development.md)
- 🐛 [问题反馈](https://github.com/JoyinJoester/BakaGit/issues)
- 💬 [讨论区](https://github.com/JoyinJoester/BakaGit/discussions)

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 查看 LICENSE 文件了解详情。

## 🙏 致谢

- 感谢 [PyQt6](https://pypi.org/project/PyQt6/) 提供优秀的GUI框架
- 感谢 [GitPython](https://github.com/gitpython-developers/GitPython) 提供Git操作支持
- 感谢所有贡献者和用户的支持

---

<div align="center">

**如果这个项目对您有帮助，请给一个 ⭐Star⭐ 支持一下！**

[🏠 主页](https://github.com/JoyinJoester/BakaGit) | 
[📖 文档](docs/) | 
[🐛 反馈](https://github.com/JoyinJoester/BakaGit/issues) | 
[💬 讨论](https://github.com/JoyinJoester/BakaGit/discussions)

Made with ❤️ by [JoyinJoester](https://github.com/JoyinJoester)

</div>
