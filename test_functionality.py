#!/usr/bin/env python3
"""
BakaGit 功能测试脚本
测试应用程序的各项核心功能
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, 'src')

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 核心模块
        from bakagit.core.git_manager import GitManager
        from bakagit.core.config import ConfigManager
        print("✅ 核心模块导入成功")
        
        # GUI模块
        from bakagit.gui.main_window import MainWindow
        from bakagit.gui.dialogs.clone_dialog import CloneRepositoryDialog
        from bakagit.gui.dialogs.settings_dialog import SettingsDialog
        from bakagit.gui.dialogs.appearance_dialog import QuickAppearanceDialog
        print("✅ GUI模块导入成功")
        
        # 依赖库
        import PyQt6.QtWidgets
        import git
        import yaml
        print("✅ 依赖库可用")
        
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config_manager():
    """测试配置管理器"""
    print("\n🔧 测试配置管理器...")
    
    try:
        from bakagit.core.config import ConfigManager
        
        config = ConfigManager()
        
        # 测试基本操作
        config.set('test_key', 'test_value')
        value = config.get('test_key')
        assert value == 'test_value', f"期望 'test_value'，得到 '{value}'"
        print("✅ 基本配置读写成功")
        
        # 测试嵌套键
        config.set('ui.theme', 'dark')
        theme = config.get('ui.theme')
        assert theme == 'dark', f"期望 'dark'，得到 '{theme}'"
        print("✅ 嵌套配置读写成功")
        
        # 测试默认值
        default_value = config.get('nonexistent_key', 'default')
        assert default_value == 'default', f"期望 'default'，得到 '{default_value}'"
        print("✅ 默认值处理成功")
        
        return True
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False

def test_git_manager():
    """测试Git管理器"""
    print("\n🐙 测试Git管理器...")
    
    try:
        from bakagit.core.git_manager import GitManager
        
        git_manager = GitManager()
        
        # 测试Git配置获取
        config = git_manager.get_config()
        print(f"✅ Git配置获取成功，共 {len(config)} 项配置")
        
        # 创建临时目录测试
        with tempfile.TemporaryDirectory() as temp_dir:
            test_repo_path = os.path.join(temp_dir, "test_repo")
            os.makedirs(test_repo_path)
            
            # 测试仓库初始化
            if git_manager.init_repository(test_repo_path):
                print("✅ 仓库初始化成功")
                
                # 测试仓库加载
                if git_manager.load_repository(test_repo_path):
                    print("✅ 仓库加载成功")
                    
                    # 测试分支操作
                    branches = git_manager.get_branches()
                    print(f"✅ 分支列表获取成功: {branches}")
                    
                    current_branch = git_manager.get_current_branch()
                    print(f"✅ 当前分支: {current_branch}")
                else:
                    print("❌ 仓库加载失败")
                    return False
            else:
                print("❌ 仓库初始化失败")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Git管理器测试失败: {e}")
        return False

def test_gui_creation():
    """测试GUI组件创建"""
    print("\n🖼️ 测试GUI组件创建...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from bakagit.gui.main_window import MainWindow
        
        # 创建应用实例（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建主窗口
        window = MainWindow()
        print("✅ 主窗口创建成功")
        
        # 测试对话框创建
        from bakagit.gui.dialogs.appearance_dialog import QuickAppearanceDialog
        appearance_dialog = QuickAppearanceDialog(window)
        print("✅ 外观对话框创建成功")
        
        from bakagit.gui.dialogs.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(window)
        print("✅ 设置对话框创建成功")
        
        return True
    except Exception as e:
        print(f"❌ GUI组件创建失败: {e}")
        return False

def test_file_operations():
    """测试文件操作"""
    print("\n📁 测试文件操作...")
    
    try:
        # 测试配置文件创建
        config_dir = Path.home() / '.bakagit'
        if not config_dir.exists():
            config_dir.mkdir(parents=True)
            print(f"✅ 配置目录创建成功: {config_dir}")
        else:
            print(f"✅ 配置目录已存在: {config_dir}")
        
        # 测试配置文件写入
        from bakagit.core.config import ConfigManager
        config = ConfigManager()
        if config.save_config():
            print("✅ 配置文件保存成功")
        else:
            print("❌ 配置文件保存失败")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 文件操作测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 BakaGit 功能测试开始\n")
    
    tests = [
        ("模块导入", test_imports),
        ("配置管理器", test_config_manager),
        ("Git管理器", test_git_manager),
        ("GUI组件创建", test_gui_creation),
        ("文件操作", test_file_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！BakaGit 运行正常！")
        return True
    else:
        print("⚠️  部分测试失败，请检查问题")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
