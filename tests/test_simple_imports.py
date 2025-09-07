"""
简单的菜单功能验证脚本
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

def test_imports():
    """测试导入是否正常"""
    try:
        from bakagit.core.config import ConfigManager
        print("✅ ConfigManager 导入成功")
        
        from bakagit.gui.dialogs.language_dialog import LanguageDialog
        print("✅ LanguageDialog 导入成功")
        
        # 测试ConfigManager的新方法
        config = ConfigManager()
        assert hasattr(config, 'reset_to_defaults'), "ConfigManager缺少reset_to_defaults方法"
        print("✅ ConfigManager.reset_to_defaults 方法存在")
        
        print("\n✅ 所有导入和基本功能测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_imports()
    print(f"\n测试结果: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1)
