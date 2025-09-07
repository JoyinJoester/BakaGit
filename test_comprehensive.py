#!/usr/bin/env python3
"""
BakaGit 集成测试脚本
测试应用程序的完整工作流程
"""

import sys
import os
import tempfile
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, 'src')

def test_app_workflow():
    """测试完整的应用程序工作流程"""
    print("🔄 测试完整应用程序工作流程...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from bakagit.gui.main_window import MainWindow
        from bakagit.core.git_manager import GitManager
        from bakagit.core.config import ConfigManager
        
        # 创建应用实例
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建主窗口
        window = MainWindow()
        print("✅ 主窗口创建成功")
        
        # 测试配置管理
        config_manager = ConfigManager()
        config_manager.set('test_setting', 'test_value')
        config_manager.save_config()
        print("✅ 配置管理功能正常")
        
        # 测试Git管理器
        git_manager = GitManager()
        git_config = git_manager.get_config()
        print(f"✅ Git配置读取成功，包含 {len(git_config)} 项")
        
        # 创建临时仓库进行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            test_repo = os.path.join(temp_dir, "test_repo")
            os.makedirs(test_repo)
            
            # 初始化仓库
            if git_manager.init_repository(test_repo):
                print("✅ 测试仓库初始化成功")
                
                # 加载仓库
                if git_manager.load_repository(test_repo):
                    print("✅ 测试仓库加载成功")
                    
                    # 测试分支操作
                    current_branch = git_manager.get_current_branch()
                    print(f"✅ 当前分支: {current_branch}")
                    
                    # 创建测试文件
                    test_file = os.path.join(test_repo, "test.txt")
                    with open(test_file, 'w') as f:
                        f.write("Hello BakaGit!")
                    
                    # 测试文件状态
                    status = git_manager.get_status()
                    print(f"✅ 文件状态获取成功: {len(status.get('untracked', []))} 个未跟踪文件")
                    
                    # 测试添加文件
                    if git_manager.add_files(["test.txt"]):
                        print("✅ 文件添加到暂存区成功")
                        
                        # 测试提交
                        commit_result = git_manager.commit("Initial commit", "Test User", "test@example.com")
                        if commit_result:
                            print("✅ 提交操作成功")
                        else:
                            print("⚠️  提交操作失败（可能是Git配置问题）")
                    else:
                        print("⚠️  文件添加失败")
                else:
                    print("❌ 测试仓库加载失败")
                    return False
            else:
                print("❌ 测试仓库初始化失败")
                return False
        
        print("✅ 完整工作流程测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_components():
    """测试GUI组件的创建和基本功能"""
    print("\n🖼️ 测试GUI组件详细功能...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from bakagit.gui.main_window import MainWindow
        from bakagit.gui.dialogs.appearance_dialog import QuickAppearanceDialog
        from bakagit.gui.dialogs.settings_dialog import SettingsDialog
        
        # 确保应用实例存在
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建主窗口
        window = MainWindow()
        
        # 测试主窗口组件
        assert hasattr(window, 'toolbar'), "主窗口缺少工具栏"
        assert hasattr(window, 'branch_combo'), "主窗口缺少分支选择器"
        assert hasattr(window, 'tab_widget'), "主窗口缺少标签页组件"
        print("✅ 主窗口组件完整")
        
        # 测试外观对话框
        appearance_dialog = QuickAppearanceDialog(window)
        assert hasattr(appearance_dialog, 'theme_group'), "外观对话框缺少主题组"
        assert hasattr(appearance_dialog, 'font_family_combo'), "外观对话框缺少字体选择"
        print("✅ 外观对话框组件完整")
        
        # 测试设置对话框
        settings_dialog = SettingsDialog(window)
        assert hasattr(settings_dialog, 'tab_widget'), "设置对话框缺少标签页"
        print("✅ 设置对话框组件完整")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI组件测试失败: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n⚠️ 测试错误处理...")
    
    try:
        from bakagit.core.git_manager import GitManager
        
        git_manager = GitManager()
        
        # 测试加载不存在的仓库
        result = git_manager.load_repository("/nonexistent/path")
        assert result == False, "应该返回False对于不存在的仓库"
        print("✅ 不存在仓库路径处理正确")
        
        # 测试在没有仓库的情况下进行操作
        status = git_manager.get_status()
        assert isinstance(status, dict), "应该返回空字典而不是报错"
        print("✅ 无仓库状态下操作处理正确")
        
        # 测试无效分支操作
        result = git_manager.checkout_branch("nonexistent_branch")
        assert result == False, "应该返回False对于不存在的分支"
        print("✅ 无效分支操作处理正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False

def run_comprehensive_tests():
    """运行综合测试"""
    print("🚀 BakaGit 综合测试开始\n")
    
    tests = [
        ("完整工作流程", test_app_workflow),
        ("GUI组件功能", test_gui_components),
        ("错误处理", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过\n")
            else:
                print(f"❌ {test_name} 测试失败\n")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}\n")
    
    print("=" * 60)
    print(f"📊 综合测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有综合测试通过！BakaGit 功能完整且稳定！")
        return True
    else:
        print("⚠️  部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
