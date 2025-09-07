"""
BakaGit - 笨蛋都会用的Git图形化工具

一个简单易用的Git图形界面工具，让版本控制变得直观和高效。
"""

__version__ = "0.1.0"
__author__ = "BakaGit Team"
__email__ = "bakagit@example.com"
__description__ = "笨蛋都会用的Git图形化工具"

# 版本信息
VERSION_INFO = {
    "major": 0,
    "minor": 1,
    "patch": 0,
    "pre_release": "alpha",
}

def get_version():
    """获取版本号字符串"""
    return __version__

def get_version_info():
    """获取详细版本信息"""
    return VERSION_INFO.copy()
