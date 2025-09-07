"""
配置管理模块

处理应用程序的配置文件，包括用户设置、Git配置等。
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置目录路径，如果为None则使用默认路径
        """
        if config_dir is None:
            # 使用用户主目录下的 .bakagit 文件夹
            self.config_dir = Path.home() / '.bakagit'
        else:
            self.config_dir = Path(config_dir)
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置文件路径
        self.config_file = self.config_dir / 'config.yaml'
        self.recent_repos_file = self.config_dir / 'recent_repos.json'
        
        # 默认配置
        self.default_config = {
            'ui': {
                'theme': 'dark',  # 主题: light, dark
                'font_size': 13,
                'window_size': [1200, 800],
                'window_position': [100, 100],
                'show_welcome': True,
            },
            'git': {
                'default_author_name': '',
                'default_author_email': '',
                'auto_fetch': True,
                'auto_fetch_interval': 300,  # 秒
                'commit_template': '',
                'diff_tool': '',
                'merge_tool': '',
            },
            'editor': {
                'external_editor': '',
                'show_line_numbers': True,
                'word_wrap': True,
                'tab_size': 4,
            },
            'notifications': {
                'show_push_success': True,
                'show_pull_success': True,
                'show_commit_success': True,
                'play_sound': False,
            }
        }
        
        # 加载配置
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            Dict: 配置数据
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    # 合并默认配置和用户配置
                    return self._merge_config(self.default_config, config)
            else:
                # 如果配置文件不存在，创建默认配置
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.default_config.copy()
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存配置文件
        
        Args:
            config: 要保存的配置数据，如果为None则保存当前配置
            
        Returns:
            bool: 是否成功保存
        """
        try:
            if config is None:
                config = self.config
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点分隔的嵌套键，如 'ui.theme'
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点分隔的嵌套键
            value: 配置值
            
        Returns:
            bool: 是否成功设置
        """
        keys = key.split('.')
        config = self.config
        
        try:
            # 导航到最后一级的父字典
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            return True
        except Exception as e:
            print(f"设置配置值失败: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        重置为默认配置
        
        Returns:
            bool: 是否成功重置
        """
        self.config = self.default_config.copy()
        return self.save_config()
    
    def get_recent_repositories(self) -> list:
        """
        获取最近访问的仓库列表
        
        Returns:
            list: 最近仓库路径列表
        """
        try:
            if self.recent_repos_file.exists():
                with open(self.recent_repos_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"加载最近仓库列表失败: {e}")
            return []
    
    def add_recent_repository(self, repo_path: str, max_count: int = 10) -> bool:
        """
        添加仓库到最近访问列表
        
        Args:
            repo_path: 仓库路径
            max_count: 最大保存数量
            
        Returns:
            bool: 是否成功添加
        """
        try:
            recent_repos = self.get_recent_repositories()
            
            # 如果已存在，先移除
            if repo_path in recent_repos:
                recent_repos.remove(repo_path)
            
            # 添加到列表开头
            recent_repos.insert(0, repo_path)
            
            # 限制列表长度
            recent_repos = recent_repos[:max_count]
            
            # 保存到文件
            with open(self.recent_repos_file, 'w', encoding='utf-8') as f:
                json.dump(recent_repos, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"添加最近仓库失败: {e}")
            return False
    
    def remove_recent_repository(self, repo_path: str) -> bool:
        """
        从最近访问列表中移除仓库
        
        Args:
            repo_path: 要移除的仓库路径
            
        Returns:
            bool: 是否成功移除
        """
        try:
            recent_repos = self.get_recent_repositories()
            
            if repo_path in recent_repos:
                recent_repos.remove(repo_path)
                
                with open(self.recent_repos_file, 'w', encoding='utf-8') as f:
                    json.dump(recent_repos, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"移除最近仓库失败: {e}")
            return False
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并默认配置和用户配置
        
        Args:
            default: 默认配置
            user: 用户配置
            
        Returns:
            Dict: 合并后的配置
        """
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def export_config(self, export_path: str) -> bool:
        """
        导出配置到指定文件
        
        Args:
            export_path: 导出文件路径
            
        Returns:
            bool: 是否成功导出
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        从文件导入配置
        
        Args:
            import_path: 导入文件路径
            
        Returns:
            bool: 是否成功导入
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = yaml.safe_load(f)
            
            # 合并导入的配置
            self.config = self._merge_config(self.default_config, imported_config)
            
            # 保存合并后的配置
            return self.save_config()
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        获取所有设置（扁平化格式）
        
        Returns:
            Dict: 扁平化的设置字典
        """
        settings = {}
        
        # 将嵌套配置转换为扁平格式
        def flatten_dict(d, prefix=''):
            for key, value in d.items():
                if isinstance(value, dict):
                    flatten_dict(value, f"{prefix}{key}_" if prefix else f"{key}_")
                else:
                    settings[f"{prefix}{key}"] = value
        
        flatten_dict(self.config)
        return settings
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        设置单个设置值（支持扁平化键名）
        
        Args:
            key: 设置键名
            value: 设置值
            
        Returns:
            bool: 是否成功设置
        """
        # 将扁平化的键名转换为嵌套结构
        if '_' in key:
            # 处理嵌套键，如 ui_theme -> ui.theme
            parts = key.split('_', 1)
            nested_key = f"{parts[0]}.{parts[1]}"
            return self.set(nested_key, value)
        else:
            # 直接设置到根级别
            self.config[key] = value
            return True
    
    def reset_to_defaults(self) -> bool:
        """
        重置所有设置为默认值
        
        Returns:
            bool: 是否成功重置
        """
        try:
            # 重置配置为默认值
            self.config = self.default_config.copy()
            
            # 保存重置后的配置
            success = self.save_config()
            
            if success:
                print("所有设置已重置为默认值")
            else:
                print("重置设置时保存失败")
                
            return success
            
        except Exception as e:
            print(f"重置设置失败: {e}")
            return False
