# 🎯 BakaGit - 笨蛋都会用的Git图形化工具

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.9.1-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

一个简单易用、功能完整的Git图形界面工具，专为初学者设计，让Git操作变得直观而高效。界面采用现代化深色主题，提供丰富的功能和良好的用户体验。

## ✨ 功能特性

### 🚀 核心功能
- **📁 仓库管理** - 打开现有仓库、克隆远程仓库、初始化新仓库
- **📝 文件操作** - 可视化文件状态管理，支持暂存、取消暂存、恢复文件
- **💾 智能提交** - 增强的提交界面，支持文件选择和提交历史查看
- **🌿 分支管理** - 创建、切换、删除分支，查看分支列表
- **🌐 远程操作** - 推送、拉取代码，管理远程仓库连接
- **🏷️ 标签管理** - 创建、删除、推送Git标签
- **⚙️ Git配置** - 配置用户信息、全局设置等

### 🎨 界面特色
- **🌙 深色主题** - 统一的深色界面设计，减少眼部疲劳
- **📊 实时状态** - 详细的状态栏信息，显示分支、文件状态等
- **🔧 工具菜单** - 便捷的Git配置和仓库设置功能
- **📱 多标签页** - 文件状态、提交、分支、远程操作等功能分区
- **⌨️ 快捷键** - 丰富的键盘快捷键支持

## 🖼️ 界面预览

### 主要功能标签页
- **📄 文件状态** - 查看工作区和暂存区文件变更
- **📝 增强提交** - 选择文件并执行提交操作
- **📚 提交历史** - 浏览完整的提交记录
- **🌿 分支管理** - 可视化分支操作
- **🌐 远程操作** - 管理远程仓库和同步代码
- **🏷️ 标签管理** - Git标签的完整管理

### 工具菜单功能
- **Git配置...** - 配置用户信息和Git设置
- **初始化仓库...** - 创建新的Git仓库
- **设置远程仓库...** - 配置GitHub等远程仓库地址
- **清理仓库** - 清理未跟踪的文件

## 🚀 快速开始

### 系统要求
- **Python**: 3.8 或更高版本
- **Git**: 需要安装Git并可在命令行使用
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

### 安装和运行

#### 1. 克隆项目
```bash
git clone https://github.com/JoyinJoester/BakaGit.git
cd BakaGit
```

#### 2. 安装依赖
```bash
pip install -r requirements_minimal.txt
```

或者手动安装核心依赖：
```bash
pip install PyQt6==6.9.1 GitPython==3.1.45 PyYAML==6.0.2
```

#### 3. 启动应用
```bash
python -m src.bakagit.main
```

或使用便捷脚本：
```bash
python run.py
```

### 验证安装
```bash
python -c "import PyQt6.QtWidgets; import git; import yaml; print('✅ 所有依赖安装成功')"
```

## 📖 使用指南

### 基本操作流程

#### 1. 打开或创建仓库
- **打开现有仓库**: `文件` → `打开仓库`，选择包含.git文件夹的目录
- **克隆远程仓库**: `文件` → `克隆仓库`，输入GitHub等远程仓库地址
- **初始化新仓库**: `工具` → `初始化仓库...`，在指定目录创建新仓库

#### 2. 设置远程仓库（推荐）
- 使用 `工具` → `设置远程仓库...`
- 输入GitHub仓库地址（如：`https://github.com/用户名/仓库名.git`）
- 设置完成后，所有推送操作都会推送到指定仓库

#### 3. 文件操作
- 在"文件状态"标签页查看修改的文件
- 选择文件后点击"暂存文件"添加到暂存区
- 在"增强提交"标签页输入提交信息并提交

#### 4. 同步代码
- 使用工具栏的推送按钮将代码推送到远程仓库
- 使用拉取按钮从远程仓库获取最新代码

### 主要功能说明

#### Git配置
- `工具` → `Git配置...` 打开配置对话框
- 配置用户名、邮箱等基本信息
- 设置编辑器、合并工具等高级选项

#### 分支管理
- 在"分支管理"标签页查看所有分支
- 使用右键菜单进行分支操作
- 支持创建、切换、删除分支

#### 远程操作
- 在"远程操作"标签页管理远程仓库
- 添加、删除远程仓库连接
- 推送、拉取、获取远程更新

### 快捷键
- `Ctrl+O` - 打开仓库
- `Ctrl+Shift+C` - 克隆仓库
- `F5` - 刷新状态
- `Ctrl+1` - 文件状态标签页
- `Ctrl+2` - 增强提交标签页
- `Ctrl+3` - 提交历史标签页
- `Ctrl+4` - 分支管理标签页
- `Ctrl+5` - 远程操作标签页
- `Ctrl+6` - 标签管理标签页

## 🏗️ 项目结构

```
BakaGit/
├── src/bakagit/                    # 主要源代码
│   ├── __init__.py                # 包信息
│   ├── main.py                    # 应用程序入口和主题样式
│   ├── core/                      # 核心功能模块
│   │   ├── git_manager.py         # Git操作封装
│   │   └── config.py              # 配置管理
│   └── gui/                       # 图形界面模块
│       ├── main_window.py         # 主窗口实现
│       └── dialogs/               # 对话框
│           ├── git_config_dialog.py      # Git配置对话框
│           └── init_repository_dialog.py # 仓库初始化对话框
├── requirements_minimal.txt       # 最小依赖列表
├── run.py                         # 便捷启动脚本
└── README.md                     # 项目说明文档
```

## 🔧 开发和测试

### 测试功能
```bash
# 测试主窗口创建
python debug_main_window.py

# 测试菜单功能
python check_menus.py

# 测试远程仓库功能
python test_add_remote.py
```

### 依赖说明
- **PyQt6 6.9.1**: 图形界面框架
- **GitPython 3.1.45**: Git操作库
- **PyYAML 6.0.2**: 配置文件解析

## 🌟 特色功能

### 智能远程仓库设置
- 一键设置GitHub等远程仓库地址
- 自动配置推送目标
- 支持立即推送当前分支

### 完整的Git配置管理
- 图形化的Git配置界面
- 支持用户信息、全局设置、仓库设置
- 三个标签页的完整配置选项

### 现代化深色主题
- 统一的深色界面设计
- 完美的颜色对比度
- 专门优化的状态栏样式

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🌟 致谢

- [PyQt6](https://pypi.org/project/PyQt6/) - 强大的Python GUI框架
- [GitPython](https://gitpython.readthedocs.io/) - Python Git库
- [PyYAML](https://pyyaml.org/) - YAML解析器

---

**让Git操作变得简单直观，这就是BakaGit的使命！** 🚀

> 如果这个项目对您有帮助，请给它一个 ⭐ Star！
