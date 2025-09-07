"""
语言设置对话框
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QRadioButton, QButtonGroup, QPushButton, 
                            QGroupBox, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon


class LanguageDialog(QDialog):
    """语言设置对话框"""
    
    language_changed = pyqtSignal(str)  # 语言更改信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = parent.config_manager if parent else None
        self.current_language = self.config_manager.get('language', 'zh_CN') if self.config_manager else 'zh_CN'
        
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("语言设置 / Language Settings")
        self.setFixedSize(450, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowFlag.WindowContextHelpButtonHint)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("选择界面语言 / Select Interface Language")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2196F3; padding: 10px;")
        main_layout.addWidget(title_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        # 语言选择组
        language_group = QGroupBox("可用语言 / Available Languages")
        language_layout = QVBoxLayout()
        
        # 创建按钮组
        self.language_group = QButtonGroup()
        
        # 中文简体
        self.zh_cn_radio = QRadioButton("🇨🇳 简体中文 (Simplified Chinese)")
        self.zh_cn_radio.setStyleSheet("QRadioButton { padding: 8px; font-size: 10pt; }")
        self.language_group.addButton(self.zh_cn_radio, 0)
        language_layout.addWidget(self.zh_cn_radio)
        
        # 中文繁体
        self.zh_tw_radio = QRadioButton("🇹🇼 繁體中文 (Traditional Chinese)")
        self.zh_tw_radio.setStyleSheet("QRadioButton { padding: 8px; font-size: 10pt; }")
        self.language_group.addButton(self.zh_tw_radio, 1)
        language_layout.addWidget(self.zh_tw_radio)
        
        # 英语
        self.en_us_radio = QRadioButton("🇺🇸 English (US)")
        self.en_us_radio.setStyleSheet("QRadioButton { padding: 8px; font-size: 10pt; }")
        self.language_group.addButton(self.en_us_radio, 2)
        language_layout.addWidget(self.en_us_radio)
        
        # 日语
        self.ja_jp_radio = QRadioButton("🇯🇵 日本語 (Japanese)")
        self.ja_jp_radio.setStyleSheet("QRadioButton { padding: 8px; font-size: 10pt; }")
        self.language_group.addButton(self.ja_jp_radio, 3)
        language_layout.addWidget(self.ja_jp_radio)
        
        # 韩语
        self.ko_kr_radio = QRadioButton("🇰🇷 한국어 (Korean)")
        self.ko_kr_radio.setStyleSheet("QRadioButton { padding: 8px; font-size: 10pt; }")
        self.language_group.addButton(self.ko_kr_radio, 4)
        language_layout.addWidget(self.ko_kr_radio)
        
        language_group.setLayout(language_layout)
        main_layout.addWidget(language_group)
        
        # 说明文本
        info_label = QLabel(
            "💡 提示：语言更改将在重启应用后生效\n"
            "💡 Note: Language changes will take effect after restarting the application"
        )
        info_label.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                border: 1px solid #BBDEFB;
                border-radius: 6px;
                padding: 12px;
                color: #1976D2;
                font-size: 9pt;
            }
        """)
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        self.cancel_button = QPushButton("取消 / Cancel")
        self.cancel_button.setFixedSize(100, 32)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # 确定按钮
        self.ok_button = QPushButton("确定 / OK")
        self.ok_button.setFixedSize(100, 32)
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept_changes)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        button_layout.addWidget(self.ok_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 连接信号
        self.language_group.buttonToggled.connect(self.on_language_changed)
    
    def load_current_settings(self):
        """加载当前设置"""
        language_map = {
            'zh_CN': self.zh_cn_radio,
            'zh_TW': self.zh_tw_radio,
            'en_US': self.en_us_radio,
            'ja_JP': self.ja_jp_radio,
            'ko_KR': self.ko_kr_radio
        }
        
        current_radio = language_map.get(self.current_language, self.zh_cn_radio)
        current_radio.setChecked(True)
    
    def on_language_changed(self, button, checked):
        """语言选择改变时的处理"""
        if checked:
            # 可以在这里添加预览功能
            pass
    
    def get_selected_language(self):
        """获取选择的语言代码"""
        if self.zh_cn_radio.isChecked():
            return 'zh_CN'
        elif self.zh_tw_radio.isChecked():
            return 'zh_TW'
        elif self.en_us_radio.isChecked():
            return 'en_US'
        elif self.ja_jp_radio.isChecked():
            return 'ja_JP'
        elif self.ko_kr_radio.isChecked():
            return 'ko_KR'
        else:
            return 'zh_CN'  # 默认简体中文
    
    def accept_changes(self):
        """接受更改"""
        selected_language = self.get_selected_language()
        
        if selected_language != self.current_language:
            # 发出语言更改信号
            self.language_changed.emit(selected_language)
            
            # 显示重启提示
            if selected_language in ['en_US', 'ja_JP', 'ko_KR']:
                # 对于非中文语言，显示双语提示
                QMessageBox.information(
                    self, 
                    "Language Changed / 语言已更改",
                    f"Language has been changed. Please restart the application to apply changes.\n"
                    f"语言已更改为 {self.get_language_name(selected_language)}，请重启应用以应用更改。"
                )
            else:
                # 中文语言
                QMessageBox.information(
                    self, 
                    "语言已更改",
                    f"语言已更改为{self.get_language_name(selected_language)}，请重启应用以应用更改。"
                )
        
        self.accept()
    
    def get_language_name(self, language_code):
        """获取语言名称"""
        language_names = {
            'zh_CN': '简体中文',
            'zh_TW': '繁體中文', 
            'en_US': 'English',
            'ja_JP': '日本語',
            'ko_KR': '한국어'
        }
        return language_names.get(language_code, '简体中文')
