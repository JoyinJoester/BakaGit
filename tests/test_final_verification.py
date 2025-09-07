"""
最终功能验证测试
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from PyQt6.QtWidgets import QApplication
from bakagit.gui.main_window import MainWindow
from bakagit.core.git_manager import GitManager

def test_complete_functionality():
    """完整功能测试"""
    print("🚀 BakaGit 完整功能验证测试")
    print("=" * 50)
    
    results = {}
    
    try:
        app = QApplication(sys.argv)
        
        # 1. 测试主窗口创建
        print("1. 测试主窗口创建...")
        window = MainWindow()
        results["主窗口创建"] = True
        print("✅ 主窗口创建成功")
        
        # 2. 测试菜单结构
        print("\n2. 测试菜单结构...")
        menu_bar = window.menuBar()
        menus = [action.text() for action in menu_bar.actions()]
        expected_menus = ['文件', '编辑', '视图', '工具', '设置', '帮助']
        
        if all(menu in menus for menu in expected_menus):
            results["菜单结构"] = True
            print("✅ 菜单结构正确")
            print(f"   发现菜单: {menus}")
        else:
            results["菜单结构"] = False
            print("❌ 菜单结构不完整")
        
        # 3. 测试设置菜单项
        print("\n3. 测试设置菜单项...")
        settings_menu = None
        for action in menu_bar.actions():
            if action.text() == '设置':
                settings_menu = action.menu()
                break
        
        if settings_menu:
            settings_actions = [action.text() for action in settings_menu.actions() if action.text()]
            expected_settings = ['外观设置', '语言设置', '完整设置', '重置所有设置']
            
            if all(setting in settings_actions for setting in expected_settings):
                results["设置菜单"] = True
                print("✅ 设置菜单项正确")
                print(f"   设置选项: {settings_actions}")
            else:
                results["设置菜单"] = False
                print("❌ 设置菜单项不完整")
        else:
            results["设置菜单"] = False
            print("❌ 未找到设置菜单")
        
        # 4. 测试语言设置功能
        print("\n4. 测试语言设置功能...")
        try:
            window.open_language_settings()
            results["语言设置"] = True
            print("✅ 语言设置功能正常")
        except Exception as e:
            results["语言设置"] = False
            print(f"❌ 语言设置功能失败: {e}")
        
        # 5. 测试Git管理器
        print("\n5. 测试Git管理器...")
        git_manager = GitManager()
        current_repo = project_root  # 使用项目根目录，它现在是Git仓库
        
        if git_manager.load_repository(current_repo):
            results["Git管理器"] = True
            print("✅ Git管理器工作正常")
            
            # 测试提交历史
            commits = git_manager.get_commit_history(3)
            if commits:
                results["提交历史"] = True
                print(f"✅ 提交历史获取成功 ({len(commits)} 个提交)")
                for i, commit in enumerate(commits):
                    print(f"   {i+1}. {commit['short_hash']} - {commit['message'][:40]}...")
            else:
                results["提交历史"] = False
                print("❌ 提交历史获取失败")
        else:
            results["Git管理器"] = False
            print(f"❌ Git管理器加载仓库失败: {current_repo}")
        
        # 6. 测试新增的菜单方法
        print("\n6. 测试新增菜单方法...")
        new_methods = [
            'undo_last_action', 'select_all_files', 'toggle_toolbar',
            'toggle_statusbar', 'open_git_config', 'cleanup_repository',
            'open_language_settings', 'reset_all_settings', 'show_tutorial'
        ]
        
        missing_methods = []
        for method in new_methods:
            if not hasattr(window, method):
                missing_methods.append(method)
        
        if not missing_methods:
            results["新增方法"] = True
            print("✅ 所有新增方法都已实现")
        else:
            results["新增方法"] = False
            print(f"❌ 缺少方法: {missing_methods}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📋 测试结果汇总:")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:12} : {status}")
    
    print("-" * 50)
    print(f"总测试数: {total_tests}")
    print(f"通过数量: {passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！BakaGit功能完整！")
        return True
    else:
        print(f"\n⚠️  有 {total_tests - passed_tests} 项测试未通过")
        return False

if __name__ == '__main__':
    success = test_complete_functionality()
    sys.exit(0 if success else 1)
