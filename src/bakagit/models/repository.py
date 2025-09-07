"""
仓库数据模型

定义Git仓库的数据结构和相关操作。
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Repository:
    """Git仓库数据模型"""
    
    path: str
    name: str
    current_branch: str = ""
    remote_url: str = ""
    is_dirty: bool = False
    untracked_files: List[str] = None
    modified_files: List[str] = None
    staged_files: List[str] = None
    local_branches: List[str] = None
    remote_branches: List[str] = None
    last_commit_hash: str = ""
    last_commit_message: str = ""
    last_commit_author: str = ""
    last_commit_date: Optional[datetime] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.untracked_files is None:
            self.untracked_files = []
        if self.modified_files is None:
            self.modified_files = []
        if self.staged_files is None:
            self.staged_files = []
        if self.local_branches is None:
            self.local_branches = []
        if self.remote_branches is None:
            self.remote_branches = []
        
        # 如果没有提供名称，从路径中提取
        if not self.name:
            self.name = Path(self.path).name
    
    @property
    def has_changes(self) -> bool:
        """是否有未提交的更改"""
        return self.is_dirty or bool(self.untracked_files) or bool(self.staged_files)
    
    @property
    def total_files_changed(self) -> int:
        """总的更改文件数"""
        return len(self.untracked_files) + len(self.modified_files) + len(self.staged_files)
    
    @property
    def status_text(self) -> str:
        """状态文本描述"""
        if not self.has_changes:
            return "无更改"
        
        changes = []
        if self.untracked_files:
            changes.append(f"{len(self.untracked_files)}个新文件")
        if self.modified_files:
            changes.append(f"{len(self.modified_files)}个修改")
        if self.staged_files:
            changes.append(f"{len(self.staged_files)}个暂存")
        
        return ", ".join(changes)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'path': self.path,
            'name': self.name,
            'current_branch': self.current_branch,
            'remote_url': self.remote_url,
            'is_dirty': self.is_dirty,
            'untracked_files': self.untracked_files,
            'modified_files': self.modified_files,
            'staged_files': self.staged_files,
            'local_branches': self.local_branches,
            'remote_branches': self.remote_branches,
            'last_commit_hash': self.last_commit_hash,
            'last_commit_message': self.last_commit_message,
            'last_commit_author': self.last_commit_author,
            'last_commit_date': self.last_commit_date.isoformat() if self.last_commit_date else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Repository':
        """从字典创建实例"""
        # 处理日期时间
        last_commit_date = None
        if data.get('last_commit_date'):
            try:
                last_commit_date = datetime.fromisoformat(data['last_commit_date'])
            except (ValueError, TypeError):
                last_commit_date = None
        
        return cls(
            path=data['path'],
            name=data.get('name', ''),
            current_branch=data.get('current_branch', ''),
            remote_url=data.get('remote_url', ''),
            is_dirty=data.get('is_dirty', False),
            untracked_files=data.get('untracked_files', []),
            modified_files=data.get('modified_files', []),
            staged_files=data.get('staged_files', []),
            local_branches=data.get('local_branches', []),
            remote_branches=data.get('remote_branches', []),
            last_commit_hash=data.get('last_commit_hash', ''),
            last_commit_message=data.get('last_commit_message', ''),
            last_commit_author=data.get('last_commit_author', ''),
            last_commit_date=last_commit_date,
        )


@dataclass
class FileStatus:
    """文件状态数据模型"""
    
    path: str
    status: str  # 'untracked', 'modified', 'added', 'deleted', 'renamed'
    old_path: Optional[str] = None  # 重命名时的原路径
    
    @property
    def display_name(self) -> str:
        """显示名称"""
        return Path(self.path).name
    
    @property
    def status_text(self) -> str:
        """状态文本"""
        status_map = {
            'untracked': '新文件',
            'modified': '已修改',
            'added': '已添加',
            'deleted': '已删除',
            'renamed': '已重命名',
        }
        return status_map.get(self.status, self.status)
    
    @property
    def status_color(self) -> str:
        """状态颜色（CSS颜色值）"""
        color_map = {
            'untracked': '#4caf50',  # 绿色
            'modified': '#ff9800',   # 橙色
            'added': '#2196f3',      # 蓝色
            'deleted': '#f44336',    # 红色
            'renamed': '#9c27b0',    # 紫色
        }
        return color_map.get(self.status, '#757575')  # 默认灰色
