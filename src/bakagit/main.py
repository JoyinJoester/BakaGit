"""
BakaGit 主入口模块

启动应用程序的主文件。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from bakagit.gui.main_window import MainWindow
from bakagit import __version__, __description__


class BakaGitApplication:
    """BakaGit应用程序类"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
    
    def initialize(self):
        """初始化应用程序"""
        # 创建QApplication实例
        self.app = QApplication(sys.argv)
        
        # 设置应用程序信息
        self.app.setApplicationName("BakaGit")
        self.app.setApplicationVersion(__version__)
        self.app.setApplicationDisplayName("BakaGit - 笨蛋都会用的Git")
        self.app.setOrganizationName("BakaGit Team")
        
        # 设置应用程序图标（如果存在）
        icon_path = Path(__file__).parent / "resources" / "icons" / "bakagit.ico"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))
        
        # 设置样式
        self.set_application_style()
        
        return True
    
    def set_application_style(self):
        """设置应用程序样式 - 超酷深色主题"""
        # 深色主题样式表
        style_sheet = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        QMenuBar {
            background-color: #2d2d2d;
            color: #ffffff;
            border-bottom: 1px solid #404040;
            padding: 6px;
            font-size: 14px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            color: #ffffff;
            padding: 6px 12px;
            margin: 2px;
            border-radius: 6px;
        }
        
        QMenuBar::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        
        QToolBar {
            background-color: #2d2d2d;
            border: none;
            spacing: 10px;
            padding: 12px;
        }
        
        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            min-height: 16px;
        }
        
        QPushButton:hover {
            background-color: #106ebe;
        }
        
        QPushButton:pressed {
            background-color: #005a9e;
        }
        
        QListWidget {
            background-color: #252525;
            color: #ffffff;
            border: 1px solid #404040;
            border-radius: 8px;
            padding: 6px;
            font-size: 13px;
        }
        
        QListWidget::item {
            padding: 10px;
            border-bottom: 1px solid #333333;
            color: #ffffff;
            border-radius: 4px;
            margin: 1px;
        }
        
        QListWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        
        QListWidget::item:hover {
            background-color: #383838;
        }
        
        QTreeWidget {
            background-color: #252525;
            color: #ffffff;
            border: 1px solid #404040;
            border-radius: 8px;
            font-size: 13px;
        }
        
        QTreeWidget::item {
            padding: 8px;
            color: #ffffff;
        }
        
        QTreeWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        
        QTreeWidget::item:hover {
            background-color: #383838;
        }
        
        QTextEdit {
            background-color: #252525;
            color: #ffffff;
            border: 1px solid #404040;
            border-radius: 8px;
            padding: 12px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.4;
        }
        
        QGroupBox {
            color: #ffffff;
            font-weight: bold;
            font-size: 14px;
            border: 2px solid #404040;
            border-radius: 8px;
            margin-top: 15px;
            padding-top: 15px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 10px 0 10px;
            color: #0078d4;
            font-weight: bold;
        }
        
        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #252525;
            border-radius: 8px;
        }
        
        QTabBar::tab {
            background-color: #1e1e1e;
            color: #ffffff;
            padding: 12px 20px;
            margin-right: 3px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border: 1px solid #404040;
            font-size: 13px;
        }
        
        QTabBar::tab:selected {
            background-color: #252525;
            color: #0078d4;
            border-bottom: none;
            font-weight: bold;
        }
        
        QTabBar::tab:hover {
            background-color: #383838;
        }
        
        QStatusBar {
            background-color: #1e1e1e;
            color: #ffffff;
            border-top: 1px solid #404040;
            padding: 5px;
            font-size: 13px;
        }
        
        QStatusBar QLabel {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 4px 8px;
            margin: 2px;
            font-size: 12px;
        }
        
        QLabel {
            color: #ffffff;
            font-size: 13px;
        }
        
        QSplitter::handle {
            background-color: #404040;
        }
        
        QSplitter::handle:horizontal {
            width: 3px;
        }
        
        QSplitter::handle:vertical {
            height: 3px;
        }
        
        /* 滚动条样式 - 超酷设计 */
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 14px;
            border-radius: 7px;
            margin: 0;
        }
        
        QScrollBar::handle:vertical {
            background-color: #0078d4;
            border-radius: 7px;
            min-height: 30px;
            margin: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #106ebe;
        }
        
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 14px;
            border-radius: 7px;
            margin: 0;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #0078d4;
            border-radius: 7px;
            min-width: 30px;
            margin: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #106ebe;
        }
        """
        
        self.app.setStyleSheet(style_sheet)
    
    def create_main_window(self):
        """创建主窗口"""
        try:
            self.main_window = MainWindow()
            self.main_window.show()
            return True
        except Exception as e:
            QMessageBox.critical(
                None, '错误', 
                f'创建主窗口失败：{str(e)}'
            )
            return False
    
    def run(self):
        """运行应用程序"""
        if not self.initialize():
            return 1
        
        if not self.create_main_window():
            return 1
        
        # 运行事件循环
        return self.app.exec()


def check_requirements():
    """检查运行环境"""
    # 检查Python版本
    if sys.version_info < (3, 9):
        print("错误: BakaGit需要Python 3.9或更高版本")
        return False
    
    # 检查PyQt6
    try:
        import PyQt6
    except ImportError:
        print("错误: 未安装PyQt6。请运行: pip install PyQt6")
        return False
    
    return True


def main():
    """主函数"""
    print(f"正在启动 {__description__} v{__version__}")
    
    # 检查运行环境
    if not check_requirements():
        return 1
    
    # 创建并运行应用程序
    try:
        app = BakaGitApplication()
        return app.run()
    except KeyboardInterrupt:
        print("\n用户中断，正在退出...")
        return 0
    except Exception as e:
        print(f"应用程序运行错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
