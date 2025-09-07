#!/usr/bin/env python3
"""
BakaGit 启动脚本

用于快速启动BakaGit应用程序的脚本。
"""

import os
import sys
from pathlib import Path

# 获取脚本目录
script_dir = Path(__file__).parent

# 添加src目录到Python路径
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

# 导入并运行主应用程序
if __name__ == "__main__":
    try:
        from bakagit.main import main
        sys.exit(main())
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖包:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"运行错误: {e}")
        sys.exit(1)
