"""
Git操作管理器

提供对Git仓库的各种操作功能，包括克隆、提交、推送、拉取等。
"""

import os
import git
from typing import List, Optional, Dict, Any
from pathlib import Path
from git.exc import GitError, InvalidGitRepositoryError, NoSuchPathError


class GitManager:
    """Git操作管理器类"""
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        初始化Git管理器
        
        Args:
            repo_path: Git仓库路径，如果为None则不加载仓库
        """
        self.repo = None
        self.repo_path = None
        
        if repo_path:
            self.load_repository(repo_path)
    
    def load_repository(self, repo_path: str) -> bool:
        """
        加载Git仓库
        
        Args:
            repo_path: 仓库路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            self.repo = git.Repo(repo_path)
            self.repo_path = repo_path
            return True
        except (InvalidGitRepositoryError, NoSuchPathError):
            self.repo = None
            self.repo_path = None
            return False
    
    def init_repository(self, repo_path: str) -> bool:
        """
        初始化新的Git仓库
        
        Args:
            repo_path: 要初始化的仓库路径
            
        Returns:
            bool: 是否成功初始化
        """
        try:
            # 确保目录存在
            Path(repo_path).mkdir(parents=True, exist_ok=True)
            
            # 初始化仓库
            self.repo = git.Repo.init(repo_path)
            self.repo_path = repo_path
            return True
        except Exception as e:
            print(f"初始化仓库失败: {e}")
            return False
    
    def clone_repository(self, url: str, target_path: str) -> bool:
        """
        克隆远程仓库
        
        Args:
            url: 远程仓库URL
            target_path: 本地目标路径
            
        Returns:
            bool: 是否成功克隆
        """
        try:
            self.repo = git.Repo.clone_from(url, target_path)
            self.repo_path = target_path
            return True
        except Exception as e:
            print(f"克隆仓库失败: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取仓库状态
        
        Returns:
            Dict: 包含仓库状态信息的字典
        """
        if not self.repo:
            return {}
        
        try:
            return {
                'is_dirty': self.repo.is_dirty(),
                'untracked_files': self.repo.untracked_files,
                'modified_files': [item.a_path for item in self.repo.index.diff(None)],
                'staged_files': [item.a_path for item in self.repo.index.diff("HEAD")],
                'current_branch': self.repo.active_branch.name,
                'remote_branches': [ref.name for ref in self.repo.remote().refs],
                'local_branches': [ref.name for ref in self.repo.heads],
            }
        except Exception as e:
            print(f"获取状态失败: {e}")
            return {}
    
    def add_files(self, file_paths: List[str]) -> bool:
        """
        添加文件到暂存区
        
        Args:
            file_paths: 要添加的文件路径列表
            
        Returns:
            bool: 是否成功添加
        """
        if not self.repo:
            return False
        
        try:
            self.repo.index.add(file_paths)
            return True
        except Exception as e:
            print(f"添加文件失败: {e}")
            return False
    
    def add_file(self, file_path: str) -> bool:
        """
        添加单个文件到暂存区
        
        Args:
            file_path: 要添加的文件路径
            
        Returns:
            bool: 是否成功添加
        """
        return self.add_files([file_path])
    
    def commit(self, message: str, author_name: Optional[str] = None, 
               author_email: Optional[str] = None) -> bool:
        """
        提交更改
        
        Args:
            message: 提交信息
            author_name: 作者姓名
            author_email: 作者邮箱
            
        Returns:
            bool: 是否成功提交
        """
        if not self.repo:
            return False
        
        try:
            # 设置作者信息（如果提供）
            commit_kwargs = {'message': message}
            if author_name and author_email:
                commit_kwargs['author'] = git.Actor(author_name, author_email)
            
            self.repo.index.commit(**commit_kwargs)
            return True
        except Exception as e:
            print(f"提交失败: {e}")
            return False
    
    def push(self, remote_name: str = 'origin', branch_name: Optional[str] = None) -> bool:
        """
        推送到远程仓库
        
        Args:
            remote_name: 远程仓库名称
            branch_name: 分支名称，如果为None则使用当前分支
            
        Returns:
            bool: 是否成功推送
        """
        if not self.repo:
            return False
        
        try:
            remote = self.repo.remote(remote_name)
            if branch_name is None:
                branch_name = self.repo.active_branch.name
            
            remote.push(refspec=f'{branch_name}:{branch_name}')
            return True
        except Exception as e:
            print(f"推送失败: {e}")
            return False
    
    def pull(self, remote_name: str = 'origin', branch_name: Optional[str] = None) -> bool:
        """
        从远程仓库拉取
        
        Args:
            remote_name: 远程仓库名称
            branch_name: 分支名称，如果为None则使用当前分支
            
        Returns:
            bool: 是否成功拉取
        """
        if not self.repo:
            return False
        
        try:
            remote = self.repo.remote(remote_name)
            if branch_name is None:
                branch_name = self.repo.active_branch.name
            
            remote.pull(branch_name)
            return True
        except Exception as e:
            print(f"拉取失败: {e}")
            return False
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        创建新分支
        
        Args:
            branch_name: 新分支名称
            checkout: 是否切换到新分支
            
        Returns:
            bool: 是否成功创建
        """
        if not self.repo:
            return False
        
        try:
            new_branch = self.repo.create_head(branch_name)
            if checkout:
                new_branch.checkout()
            return True
        except Exception as e:
            print(f"创建分支失败: {e}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """
        切换分支
        
        Args:
            branch_name: 要切换的分支名称
            
        Returns:
            bool: 是否成功切换
        """
        if not self.repo:
            return False
        
        try:
            self.repo.git.checkout(branch_name)
            return True
        except Exception as e:
            print(f"切换分支失败: {e}")
            return False
    
    def get_commit_history(self, max_count: int = 50) -> List[Dict[str, Any]]:
        """
        获取提交历史
        
        Args:
            max_count: 最大提交数量
            
        Returns:
            List[Dict]: 提交历史列表
        """
        if not self.repo:
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=max_count):
                commits.append({
                    'hash': commit.hexsha,
                    'short_hash': commit.hexsha[:8],
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'date': commit.committed_datetime,
                    'files_changed': len(commit.stats.files),
                })
            return commits
        except Exception as e:
            print(f"获取提交历史失败: {e}")
            return []
    
    def is_git_repository(self, path: str) -> bool:
        """
        检查路径是否为Git仓库
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 是否为Git仓库
        """
        try:
            git.Repo(path)
            return True
        except (InvalidGitRepositoryError, NoSuchPathError):
            return False
    
    def get_config(self, scope: str = 'global') -> Dict[str, str]:
        """
        获取Git配置
        
        Args:
            scope: 配置范围，'global', 'local', 'system'
            
        Returns:
            Dict: Git配置字典
        """
        try:
            config = {}
            
            if scope == 'global':
                # 使用git命令获取全局配置
                import subprocess
                result = subprocess.run(['git', 'config', '--global', '--list'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key] = value
            elif scope == 'local' and self.repo:
                # 读取本地仓库配置
                reader = self.repo.config_reader()
                for section_name in reader.sections():
                    for option_name in reader.options(section_name):
                        key = f"{section_name}.{option_name}"
                        value = reader.get_value(section_name, option_name)
                        config[key] = value
            
            return config
            
        except Exception as e:
            print(f"获取Git配置失败: {e}")
            return {}
    
    def set_config(self, key: str, value: str, scope: str = 'global') -> bool:
        """
        设置Git配置
        
        Args:
            key: 配置键，如 'user.name'
            value: 配置值
            scope: 配置范围，'global', 'local'
            
        Returns:
            bool: 是否成功设置
        """
        try:
            if scope == 'global':
                # 使用git命令设置全局配置
                import subprocess
                result = subprocess.run(['git', 'config', '--global', key, value], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            elif scope == 'local' and self.repo:
                # 设置本地仓库配置
                with self.repo.config_writer() as writer:
                    section, option = key.split('.', 1)
                    writer.set_value(section, option, value)
                return True
            else:
                return False
            
        except Exception as e:
            print(f"设置Git配置失败: {e}")
            return False
    
    def get_branches(self) -> List[str]:
        """
        获取所有分支列表
        
        Returns:
            List[str]: 分支名称列表
        """
        if not self.repo:
            return []
        
        try:
            branches = []
            
            # 获取本地分支
            for branch in self.repo.branches:
                branches.append(branch.name)
            
            # 获取远程分支（可选）
            for remote in self.repo.remotes:
                for ref in remote.refs:
                    if ref.name not in branches:
                        branch_name = ref.name.split('/')[-1]  # 去掉远程前缀
                        if branch_name not in branches and branch_name != 'HEAD':
                            branches.append(branch_name)
            
            return sorted(branches)
        except Exception as e:
            print(f"获取分支列表失败: {e}")
            return []
    
    def get_current_branch(self) -> str:
        """
        获取当前分支名称
        
        Returns:
            str: 当前分支名称，如果获取失败返回空字符串
        """
        if not self.repo:
            return ""
        
        try:
            return self.repo.active_branch.name
        except Exception as e:
            print(f"获取当前分支失败: {e}")
            return ""
    
    def create_branch(self, branch_name: str) -> bool:
        """
        创建新分支
        
        Args:
            branch_name: 新分支名称
            
        Returns:
            bool: 是否成功创建
        """
        if not self.repo:
            return False
        
        try:
            # 检查分支是否已存在
            if branch_name in [branch.name for branch in self.repo.branches]:
                print(f"分支 '{branch_name}' 已存在")
                return False
            
            # 创建新分支
            new_branch = self.repo.create_head(branch_name)
            return True
        except Exception as e:
            print(f"创建分支失败: {e}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """
        切换到指定分支
        
        Args:
            branch_name: 目标分支名称
            
        Returns:
            bool: 是否成功切换
        """
        if not self.repo:
            return False
        
        try:
            # 检查分支是否存在
            if branch_name not in [branch.name for branch in self.repo.branches]:
                print(f"分支 '{branch_name}' 不存在")
                return False
            
            # 切换分支
            self.repo.git.checkout(branch_name)
            return True
        except Exception as e:
            print(f"切换分支失败: {e}")
            return False
