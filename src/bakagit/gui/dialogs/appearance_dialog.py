"""快速外观设置对话框"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox,
    QLabel, QPushButton, QCheckBox, QSpinBox, QFormLayout,
    QButtonGroup, QRadioButton, QSlider, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...core.config import ConfigManager


class QuickAppearanceDialog(QDialog):
    """快速外观设置对话框"""
    
    theme_changed = pyqtSignal(str)
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("快速外观设置")
        self.setFixedSize(400, 350)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 主题选择组
        theme_group = QGroupBox("主题选择")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_group = QButtonGroup()
        
        self.dark_radio = QRadioButton("深色主题")
        self.dark_radio.setChecked(True)
        self.theme_group.addButton(self.dark_radio, 0)
        theme_layout.addWidget(self.dark_radio)
        
        self.light_radio = QRadioButton("浅色主题")
        self.theme_group.addButton(self.light_radio, 1)
        theme_layout.addWidget(self.light_radio)
        
        self.system_radio = QRadioButton("跟随系统")
        self.theme_group.addButton(self.system_radio, 2)
        theme_layout.addWidget(self.system_radio)
        
        layout.addWidget(theme_group)
        
        # 字体设置组
        font_group = QGroupBox("字体设置")
        font_layout = QFormLayout(font_group)
        
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Microsoft YaHei", "SimSun", "Arial", 
            "Consolas", "Source Code Pro", "JetBrains Mono"
        ])
        font_layout.addRow("字体族:", self.font_family_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(10)
        font_layout.addRow("字体大小:", self.font_size_spin)
        
        layout.addWidget(font_group)
        
        # 界面选项组
        ui_group = QGroupBox("界面选项")
        ui_layout = QFormLayout(ui_group)
        
        self.show_toolbar = QCheckBox("显示工具栏")
        self.show_toolbar.setChecked(True)
        ui_layout.addRow(self.show_toolbar)
        
        self.show_status_bar = QCheckBox("显示状态栏")
        self.show_status_bar.setChecked(True)
        ui_layout.addRow(self.show_status_bar)
        
        self.compact_mode = QCheckBox("紧凑模式")
        ui_layout.addRow(self.compact_mode)
        
        # 刷新间隔滑块
        self.refresh_slider = QSlider(Qt.Orientation.Horizontal)
        self.refresh_slider.setRange(1, 30)
        self.refresh_slider.setValue(5)
        self.refresh_slider.valueChanged.connect(self.update_refresh_label)
        
        self.refresh_label = QLabel("5 秒")
        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(self.refresh_slider)
        refresh_layout.addWidget(self.refresh_label)
        
        ui_layout.addRow("自动刷新间隔:", refresh_layout)
        
        layout.addWidget(ui_group)
        
        # 预览提示
        preview_label = QLabel("💡 提示：更改会立即预览，点击确定保存设置")
        preview_label.setStyleSheet("QLabel { color: #888; font-style: italic; }")
        layout.addWidget(preview_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 重置按钮
        reset_btn = QPushButton("重置为默认")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        # 预览按钮
        preview_btn = QPushButton("预览")
        preview_btn.clicked.connect(self.preview_changes)
        button_layout.addWidget(preview_btn)
        
        # 确定/取消按钮
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept_changes)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.theme_group.buttonClicked.connect(self.on_theme_changed)
        self.font_family_combo.currentTextChanged.connect(self.preview_changes)
        self.font_size_spin.valueChanged.connect(self.preview_changes)
        
    def update_refresh_label(self, value):
        """更新刷新间隔标签"""
        self.refresh_label.setText(f"{value} 秒")
        
    def load_current_settings(self):
        """加载当前设置"""
        try:
            config = self.config_manager.get_all_settings()
            
            # 加载主题设置
            theme = config.get('theme', 'dark')
            if theme == 'dark':
                self.dark_radio.setChecked(True)
            elif theme == 'light':
                self.light_radio.setChecked(True)
            else:
                self.system_radio.setChecked(True)
            
            # 加载字体设置
            font_family = config.get('font_family', 'Microsoft YaHei')
            index = self.font_family_combo.findText(font_family)
            if index >= 0:
                self.font_family_combo.setCurrentIndex(index)
            
            self.font_size_spin.setValue(config.get('font_size', 10))
            
            # 加载界面选项
            self.show_toolbar.setChecked(config.get('show_toolbar', True))
            self.show_status_bar.setChecked(config.get('show_status_bar', True))
            self.compact_mode.setChecked(config.get('compact_mode', False))
            
            refresh_interval = config.get('auto_refresh_interval', 5)
            self.refresh_slider.setValue(refresh_interval)
            self.update_refresh_label(refresh_interval)
            
        except Exception as e:
            print(f"加载外观设置失败: {e}")
            
    def on_theme_changed(self):
        """主题更改时立即预览"""
        self.preview_changes()
        
    def preview_changes(self):
        """预览更改"""
        try:
            # 获取选择的主题
            if self.dark_radio.isChecked():
                theme = 'dark'
            elif self.light_radio.isChecked():
                theme = 'light'
            else:
                theme = 'system'
            
            # 发送主题更改信号（用于实时预览）
            self.theme_changed.emit(theme)
            
        except Exception as e:
            print(f"预览更改失败: {e}")
            
    def reset_to_defaults(self):
        """重置为默认设置"""
        self.dark_radio.setChecked(True)
        self.font_family_combo.setCurrentText('Microsoft YaHei')
        self.font_size_spin.setValue(10)
        self.show_toolbar.setChecked(True)
        self.show_status_bar.setChecked(True)
        self.compact_mode.setChecked(False)
        self.refresh_slider.setValue(5)
        self.preview_changes()
        
    def accept_changes(self):
        """确认并保存更改"""
        try:
            # 获取设置值
            if self.dark_radio.isChecked():
                theme = 'dark'
            elif self.light_radio.isChecked():
                theme = 'light'
            else:
                theme = 'system'
            
            # 保存设置
            self.config_manager.set_setting('theme', theme)
            self.config_manager.set_setting('font_family', self.font_family_combo.currentText())
            self.config_manager.set_setting('font_size', self.font_size_spin.value())
            self.config_manager.set_setting('show_toolbar', self.show_toolbar.isChecked())
            self.config_manager.set_setting('show_status_bar', self.show_status_bar.isChecked())
            self.config_manager.set_setting('compact_mode', self.compact_mode.isChecked())
            self.config_manager.set_setting('auto_refresh_interval', self.refresh_slider.value())
            
            # 保存配置
            self.config_manager.save_config()
            
            # 发送设置更改信号
            self.settings_changed.emit()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存外观设置失败: {str(e)}")
