"""
测试语言设置和提交历史功能
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

def test_language_dialog():
    """测试语言设置对话框"""
    print("=== 测试语言设置对话框 ===")
    
    try:
        app = QApplication(sys.argv)
        
        # 创建主窗口
        window = MainWindow()
        
        # 尝试打开语言设置
        print("尝试调用 open_language_settings()...")
        window.open_language_settings()
        print("✅ 语言设置对话框调用成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 语言设置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_commit_history():
    """测试提交历史功能"""
    print("\n=== 测试提交历史功能 ===")
    
    try:
        # 创建GitManager实例
        git_manager = GitManager()
        
        # 尝试加载当前仓库（BakaGit项目本身）
        current_repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"尝试加载仓库: {current_repo}")
        
        if git_manager.load_repository(current_repo):
            print("✅ 仓库加载成功")
            
            # 获取提交历史
            commits = git_manager.get_commit_history(5)  # 只获取前5个提交
            print(f"获取到 {len(commits)} 个提交")
            
            if commits:
                print("最近的提交:")
                for i, commit in enumerate(commits[:3]):
                    print(f"  {i+1}. {commit['short_hash']} - {commit['message'][:50]}...")
                return True
            else:
                print("❌ 没有获取到提交历史")
                return False
        else:
            print("❌ 仓库加载失败")
            return False
            
    except Exception as e:
        print(f"❌ 提交历史测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # 测试语言设置
    lang_success = test_language_dialog()
    
    # 测试提交历史
    commit_success = test_commit_history()
    
    print(f"\n=== 测试结果 ===")
    print(f"语言设置: {'✅ 成功' if lang_success else '❌ 失败'}")
    print(f"提交历史: {'✅ 成功' if commit_success else '❌ 失败'}")
    
    sys.exit(0 if (lang_success and commit_success) else 1)
