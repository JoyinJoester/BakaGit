# BakaGit - 笨蛋都会用的Git图形化工具

## 项目简介

BakaGit 是一个专为简化 Git 操作而设计的图形化工具。无论你是 Git 新手还是经验丰富的开发者，BakaGit 都能让你的版本控制工作变得更加直观和高效。

### 🌟 主要特性

- **零学习成本**: 直观的图形界面，无需记忆复杂的 Git 命令
- **可视化操作**: 分支图、提交历史一目了然
- **智能提示**: 根据当前状态提供操作建议
- **错误恢复**: 提供撤销功能和错误修复指导
- **多语言支持**: 支持中文和英文界面
- **主题定制**: 浅色/深色主题随心切换

### 🚀 快速开始

#### 环境要求
- Python 3.9 或更高版本
- Git (已安装并配置)
- Windows/Linux/macOS

#### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/bakagit/bakagit.git
cd bakagit
```

2. 创建虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行应用
```bash
python src/bakagit/main.py
```

### 📁 项目结构

```
BakaGit/
├── src/bakagit/          # 主要源代码
│   ├── core/             # 核心功能模块
│   ├── gui/              # 图形界面
│   ├── models/           # 数据模型
│   └── resources/        # 资源文件
├── tests/                # 测试文件
├── docs/                 # 文档
└── requirements.txt      # 依赖清单
```

### 🛠️ 开发

#### 代码格式化
```bash
black src/ tests/
```

#### 代码检查
```bash
flake8 src/ tests/
```

#### 运行测试
```bash
pytest
```

### 📦 打包分发

```bash
pyinstaller --onefile --windowed src/bakagit/main.py
```

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

### 🙏 致谢

感谢所有为 BakaGit 项目做出贡献的开发者们！

---

**让 Git 变得简单，让版本控制不再是噩梦！** 🎉
