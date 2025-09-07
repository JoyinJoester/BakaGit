"""
工具函数模块

提供各种实用的工具函数。
"""

import os
import sys
import subprocess
import platform
from typing import Optional, List, Tuple
from pathlib import Path


def get_git_executable() -> Optional[str]:
    """
    获取Git可执行文件路径
    
    Returns:
        Optional[str]: Git可执行文件路径，如果未找到则返回None
    """
    try:
        # 尝试通过 which/where 命令查找
        if platform.system() == "Windows":
            result = subprocess.run(['where', 'git'], 
                                  capture_output=True, text=True, check=True)
        else:
            result = subprocess.run(['which', 'git'], 
                                  capture_output=True, text=True, check=True)
        
        git_path = result.stdout.strip().split('\n')[0]
        return git_path if git_path else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_git_installed() -> bool:
    """
    检查系统是否安装了Git
    
    Returns:
        bool: 是否安装了Git
    """
    return get_git_executable() is not None


def get_git_version() -> Optional[str]:
    """
    获取Git版本号
    
    Returns:
        Optional[str]: Git版本号，如果获取失败则返回None
    """
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, check=True)
        # 解析版本号，格式通常为 "git version 2.x.x"
        version_line = result.stdout.strip()
        if version_line.startswith('git version'):
            return version_line.split(' ')[2]
        return version_line
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        return None


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为人类可读的格式
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def is_valid_git_url(url: str) -> bool:
    """
    检查URL是否为有效的Git仓库URL
    
    Args:
        url: 要检查的URL
        
    Returns:
        bool: 是否为有效的Git URL
    """
    if not url:
        return False
    
    # 常见的Git URL模式
    git_patterns = [
        'https://github.com/',
        'https://gitlab.com/',
        'https://bitbucket.org/',
        'git@github.com:',
        'git@gitlab.com:',
        'git@bitbucket.org:',
        'https://git.',
        'git://',
        'ssh://git@',
    ]
    
    url_lower = url.lower()
    return any(pattern in url_lower for pattern in git_patterns) or url.endswith('.git')


def sanitize_branch_name(name: str) -> str:
    """
    清理分支名称，移除不允许的字符
    
    Args:
        name: 原始分支名称
        
    Returns:
        str: 清理后的分支名称
    """
    # 移除不允许的字符
    forbidden_chars = [' ', '~', '^', ':', '?', '*', '[', '\\', '..', '@{']
    sanitized = name
    
    for char in forbidden_chars:
        sanitized = sanitized.replace(char, '-')
    
    # 移除开头和结尾的点和斜杠
    sanitized = sanitized.strip('./').strip()
    
    # 确保不为空
    if not sanitized:
        sanitized = 'new-branch'
    
    return sanitized


def get_file_icon(file_path: str) -> str:
    """
    根据文件扩展名获取对应的图标名称
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 图标名称
    """
    if not file_path:
        return 'file'
    
    path = Path(file_path)
    
    if path.is_dir():
        return 'folder'
    
    extension = path.suffix.lower()
    
    # 图标映射
    icon_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'sass',
        '.less': 'less',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.txt': 'text',
        '.log': 'log',
        '.sql': 'database',
        '.db': 'database',
        '.sqlite': 'database',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.gif': 'image',
        '.svg': 'image',
        '.ico': 'image',
        '.pdf': 'pdf',
        '.doc': 'word',
        '.docx': 'word',
        '.xls': 'excel',
        '.xlsx': 'excel',
        '.ppt': 'powerpoint',
        '.pptx': 'powerpoint',
        '.zip': 'archive',
        '.rar': 'archive',
        '.7z': 'archive',
        '.tar': 'archive',
        '.gz': 'archive',
    }
    
    return icon_map.get(extension, 'file')


def open_file_in_system(file_path: str) -> bool:
    """
    使用系统默认程序打开文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否成功打开
    """
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', file_path], check=True)
        else:  # Linux and others
            subprocess.run(['xdg-open', file_path], check=True)
        return True
    except Exception as e:
        print(f"打开文件失败: {e}")
        return False


def open_folder_in_system(folder_path: str) -> bool:
    """
    使用系统文件管理器打开文件夹
    
    Args:
        folder_path: 文件夹路径
        
    Returns:
        bool: 是否成功打开
    """
    try:
        if platform.system() == "Windows":
            subprocess.run(['explorer', folder_path], check=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', folder_path], check=True)
        else:  # Linux and others
            subprocess.run(['xdg-open', folder_path], check=True)
        return True
    except Exception as e:
        print(f"打开文件夹失败: {e}")
        return False


def get_system_info() -> dict:
    """
    获取系统信息
    
    Returns:
        dict: 包含系统信息的字典
    """
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'architecture': platform.architecture()[0],
        'python_version': platform.python_version(),
        'git_version': get_git_version(),
        'git_installed': is_git_installed(),
    }


def validate_email(email: str) -> bool:
    """
    简单的邮箱格式验证
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否为有效邮箱格式
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    截断文本并添加省略号
    
    Args:
        text: 要截断的文本
        max_length: 最大长度
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def ensure_directory_exists(directory_path: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory_path: 目录路径
        
    Returns:
        bool: 是否成功确保目录存在
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {e}")
        return False
