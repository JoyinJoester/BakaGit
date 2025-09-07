"""
提交数据模型

定义Git提交的数据结构和相关操作。
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Commit:
    """Git提交数据模型"""
    
    hash: str
    message: str
    author_name: str
    author_email: str
    date: datetime
    parent_hashes: List[str] = None
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    
    def __post_init__(self):
        """初始化后处理"""
        if self.parent_hashes is None:
            self.parent_hashes = []
    
    @property
    def short_hash(self) -> str:
        """短哈希值（前8位）"""
        return self.hash[:8] if self.hash else ""
    
    @property
    def author(self) -> str:
        """作者信息"""
        if self.author_email:
            return f"{self.author_name} <{self.author_email}>"
        return self.author_name
    
    @property
    def formatted_date(self) -> str:
        """格式化的日期"""
        return self.date.strftime("%Y-%m-%d %H:%M:%S")
    
    @property
    def relative_date(self) -> str:
        """相对日期（例如：2小时前）"""
        now = datetime.now()
        if self.date.tzinfo:
            now = now.replace(tzinfo=self.date.tzinfo)
        
        diff = now - self.date
        
        if diff.days > 30:
            return self.date.strftime("%Y-%m-%d")
        elif diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"
    
    @property
    def summary_line(self) -> str:
        """提交摘要行（第一行）"""
        return self.message.split('\n')[0] if self.message else ""
    
    @property
    def description(self) -> str:
        """提交描述（除第一行外的内容）"""
        lines = self.message.split('\n')
        if len(lines) > 1:
            return '\n'.join(lines[1:]).strip()
        return ""
    
    @property
    def stats_text(self) -> str:
        """统计信息文本"""
        parts = []
        if self.files_changed:
            parts.append(f"{self.files_changed}个文件")
        if self.insertions:
            parts.append(f"+{self.insertions}")
        if self.deletions:
            parts.append(f"-{self.deletions}")
        
        return ", ".join(parts) if parts else "无更改"
    
    @property
    def is_merge_commit(self) -> bool:
        """是否为合并提交"""
        return len(self.parent_hashes) > 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'hash': self.hash,
            'message': self.message,
            'author_name': self.author_name,
            'author_email': self.author_email,
            'date': self.date.isoformat(),
            'parent_hashes': self.parent_hashes,
            'files_changed': self.files_changed,
            'insertions': self.insertions,
            'deletions': self.deletions,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Commit':
        """从字典创建实例"""
        # 处理日期时间
        date = datetime.fromisoformat(data['date'])
        
        return cls(
            hash=data['hash'],
            message=data['message'],
            author_name=data['author_name'],
            author_email=data['author_email'],
            date=date,
            parent_hashes=data.get('parent_hashes', []),
            files_changed=data.get('files_changed', 0),
            insertions=data.get('insertions', 0),
            deletions=data.get('deletions', 0),
        )


@dataclass
class Branch:
    """分支数据模型"""
    
    name: str
    commit_hash: str
    is_current: bool = False
    is_remote: bool = False
    remote_name: Optional[str] = None
    upstream_branch: Optional[str] = None
    ahead_count: int = 0
    behind_count: int = 0
    
    @property
    def full_name(self) -> str:
        """完整名称"""
        if self.is_remote and self.remote_name:
            return f"{self.remote_name}/{self.name}"
        return self.name
    
    @property
    def display_name(self) -> str:
        """显示名称"""
        prefix = "* " if self.is_current else "  "
        suffix = ""
        
        if self.ahead_count > 0 or self.behind_count > 0:
            parts = []
            if self.ahead_count > 0:
                parts.append(f"↑{self.ahead_count}")
            if self.behind_count > 0:
                parts.append(f"↓{self.behind_count}")
            suffix = f" [{'/'.join(parts)}]"
        
        return f"{prefix}{self.name}{suffix}"
    
    @property
    def status_text(self) -> str:
        """状态文本"""
        if self.is_current:
            return "当前分支"
        elif self.is_remote:
            return "远程分支"
        else:
            return "本地分支"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'commit_hash': self.commit_hash,
            'is_current': self.is_current,
            'is_remote': self.is_remote,
            'remote_name': self.remote_name,
            'upstream_branch': self.upstream_branch,
            'ahead_count': self.ahead_count,
            'behind_count': self.behind_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Branch':
        """从字典创建实例"""
        return cls(
            name=data['name'],
            commit_hash=data['commit_hash'],
            is_current=data.get('is_current', False),
            is_remote=data.get('is_remote', False),
            remote_name=data.get('remote_name'),
            upstream_branch=data.get('upstream_branch'),
            ahead_count=data.get('ahead_count', 0),
            behind_count=data.get('behind_count', 0),
        )
