# BakaGit 开发文档

## 项目概述

BakaGit 是一个基于 Python 和 PyQt6 开发的 Git 图形化工具，旨在让 Git 操作变得简单直观。

## 架构设计

### 技术栈
- **编程语言**: Python 3.9+
- **GUI框架**: PyQt6
- **Git操作**: GitPython
- **配置管理**: YAML + JSON
- **打包工具**: PyInstaller

### 模块结构

```
src/bakagit/
├── __init__.py          # 包初始化
├── main.py              # 应用程序入口
├── core/                # 核心功能模块
│   ├── git_manager.py   # Git操作管理
│   ├── config.py        # 配置管理
│   └── utils.py         # 工具函数
├── gui/                 # 图形界面模块
│   ├── main_window.py   # 主窗口
│   ├── widgets/         # 自定义组件
│   └── dialogs/         # 对话框
├── models/              # 数据模型
│   ├── repository.py    # 仓库模型
│   └── commit.py        # 提交模型
└── resources/           # 资源文件
    ├── icons/           # 图标
    ├── themes/          # 主题
    └── translations/    # 翻译文件
```

## 核心组件

### GitManager (git_manager.py)
负责所有Git操作的核心类：
- 仓库管理（加载、初始化、克隆）
- 文件操作（添加、提交、状态查询）
- 分支管理（创建、切换、合并）
- 远程操作（推送、拉取、同步）

### ConfigManager (config.py)
应用程序配置管理：
- 用户偏好设置
- 最近访问的仓库
- Git配置信息
- 界面设置（主题、语言等）

### MainWindow (main_window.py)
主要的用户界面：
- 仓库列表显示
- 文件状态管理
- 提交历史查看
- 分支可视化

### 数据模型 (models/)
定义核心数据结构：
- Repository: 仓库信息
- Commit: 提交记录
- Branch: 分支信息
- FileStatus: 文件状态

## 开发指南

### 环境设置

1. **克隆项目**
```bash
git clone <repository-url>
cd BakaGit
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行应用**
```bash
python run.py
# 或者
python src/bakagit/main.py
```

### 代码规范

- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 遵循 PEP 8 规范
- 添加类型注解

### 测试

运行测试：
```bash
python -m pytest tests/
# 或者
python tests/test_basic.py
```

### 添加新功能

1. **核心功能**: 在 `core/` 目录下添加模块
2. **UI组件**: 在 `gui/widgets/` 或 `gui/dialogs/` 下添加
3. **数据模型**: 在 `models/` 目录下定义新的数据结构
4. **测试**: 在 `tests/` 目录下添加对应的测试文件

## 用户界面设计

### 主窗口布局

```
┌─────────────────────────────────────────┐
│ 菜单栏 [文件] [编辑] [视图] [工具] [帮助]  │
├─────────────────────────────────────────┤
│ 工具栏 [克隆] [拉取] [推送] [提交] [分支]  │
├─────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────────────────────┐ │
│ │ 仓库列表 │ │ 主工作区（选项卡）        │ │
│ │         │ │ - 文件状态              │ │
│ │         │ │ - 提交历史              │ │
│ │         │ │ - 分支管理              │ │
│ └─────────┘ └─────────────────────────┘ │
├─────────────────────────────────────────┤
│ 状态栏: 当前分支 | 远程状态 | 操作提示     │
└─────────────────────────────────────────┘
```

### 主要功能区域

1. **仓库列表**: 显示最近访问的Git仓库
2. **文件状态**: 工作区、暂存区文件管理
3. **提交历史**: 可视化的提交记录
4. **分支管理**: 分支创建、切换、合并
5. **工具栏**: 常用操作快捷按钮

## 部署和分发

### 打包为可执行文件

使用 PyInstaller 打包：
```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/bakagit/main.py
```

### 创建安装包

Windows:
```bash
# 使用 Inno Setup 或 NSIS 创建安装程序
```

macOS:
```bash
# 创建 .app 包
# 使用 create-dmg 创建 DMG 文件
```

Linux:
```bash
# 创建 AppImage 或 DEB/RPM 包
```

## 配置文件

### 应用配置 (config.yaml)
```yaml
ui:
  theme: light
  language: zh_CN
  font_size: 12
  window_size: [1200, 800]

git:
  default_author_name: ""
  default_author_email: ""
  auto_fetch: true
```

### 最近仓库 (recent_repos.json)
```json
[
  "/path/to/repo1",
  "/path/to/repo2"
]
```

## 扩展和插件

BakaGit 设计时考虑了扩展性：

1. **主题系统**: 支持自定义CSS主题
2. **语言包**: 支持多语言国际化
3. **插件接口**: 预留插件扩展接口
4. **自定义工具**: 集成外部Git工具

## 故障排除

### 常见问题

1. **Git未安装**: 确保系统已安装Git并在PATH中
2. **依赖缺失**: 运行 `pip install -r requirements.txt`
3. **权限问题**: 确保对Git仓库有读写权限
4. **编码问题**: 确保文件编码为UTF-8

### 调试模式

启用调试模式：
```bash
export BAKAGIT_DEBUG=1
python src/bakagit/main.py
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT License - 详见 LICENSE 文件

## 联系方式

- 项目主页: https://github.com/bakagit/bakagit
- 问题反馈: https://github.com/bakagit/bakagit/issues
- 邮箱: bakagit@example.com
