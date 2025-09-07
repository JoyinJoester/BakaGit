"""
测试新菜单功能的简单脚本
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from src.bakagit.gui.main_window import MainWindow
from src.bakagit.core.config import ConfigManager


def test_menu_structure():
    """测试菜单结构"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    config_manager = ConfigManager()
    window = MainWindow(config_manager)
    
    # 检查菜单栏是否存在
    menu_bar = window.menuBar()
    assert menu_bar is not None, "菜单栏未创建"
    
    # 获取所有菜单
    menus = menu_bar.actions()
    menu_titles = [action.text() for action in menus]
    
    print("发现的菜单:")
    for title in menu_titles:
        print(f"  - {title}")
    
    # 检查是否包含设置菜单
    assert "设置" in menu_titles, "设置菜单未找到"
    
    print("\n✅ 菜单结构测试通过!")
    
    # 检查新方法是否存在
    methods_to_check = [
        'undo_last_action',
        'select_all_files', 
        'toggle_toolbar',
        'toggle_statusbar',
        'open_git_config',
        'cleanup_repository',
        'open_language_settings',
        'reset_all_settings',
        'show_tutorial'
    ]
    
    missing_methods = []
    for method_name in methods_to_check:
        if not hasattr(window, method_name):
            missing_methods.append(method_name)
    
    if missing_methods:
        print(f"\n❌ 缺少以下方法: {missing_methods}")
    else:
        print("\n✅ 所有新方法都已实现!")
    
    return len(missing_methods) == 0


if __name__ == '__main__':
    try:
        success = test_menu_structure()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"测试失败: {e}")
        sys.exit(1)
