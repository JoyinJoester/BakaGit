"""设置对话框"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QGroupBox, QFormLayout, QSpinBox, QTextEdit, QFileDialog,
    QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...core.config import ConfigManager
from ...core.git_manager import GitManager


class SettingsDialog(QDialog):
    """设置对话框"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.git_manager = GitManager()
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("BakaGit 设置")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        # 主布局
        layout = QVBoxLayout(self)
        
        # 标签页组件
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_general_tab()
        self.create_git_tab()
        self.create_advanced_tab()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 恢复默认按钮
        self.restore_defaults_btn = QPushButton("恢复默认")
        self.restore_defaults_btn.clicked.connect(self.restore_defaults)
        button_layout.addWidget(self.restore_defaults_btn)
        
        button_layout.addStretch()
        
        # 确定/取消按钮
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
    def create_general_tab(self):
        """创建常规设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 工作区设置
        workspace_group = QGroupBox("工作区设置")
        workspace_layout = QFormLayout(workspace_group)
        
        self.default_clone_path_edit = QLineEdit()
        clone_path_layout = QHBoxLayout()
        clone_path_layout.addWidget(self.default_clone_path_edit)
        
        browse_clone_btn = QPushButton("浏览...")
        browse_clone_btn.clicked.connect(self.browse_clone_path)
        clone_path_layout.addWidget(browse_clone_btn)
        
        workspace_layout.addRow("默认克隆路径:", clone_path_layout)
        
        self.auto_open_cloned_repo = QCheckBox("克隆后自动打开仓库")
        workspace_layout.addRow(self.auto_open_cloned_repo)
        
        self.remember_recent_repos = QCheckBox("记住最近打开的仓库")
        workspace_layout.addRow(self.remember_recent_repos)
        
        self.max_recent_repos = QSpinBox()
        self.max_recent_repos.setRange(1, 20)
        self.max_recent_repos.setValue(10)
        workspace_layout.addRow("最近仓库数量:", self.max_recent_repos)
        
        scroll_layout.addWidget(workspace_group)
        
        # 编辑器设置
        editor_group = QGroupBox("编辑器设置")
        editor_layout = QFormLayout(editor_group)
        
        self.external_editor_path = QLineEdit()
        editor_path_layout = QHBoxLayout()
        editor_path_layout.addWidget(self.external_editor_path)
        
        browse_editor_btn = QPushButton("浏览...")
        browse_editor_btn.clicked.connect(self.browse_editor_path)
        editor_path_layout.addWidget(browse_editor_btn)
        
        editor_layout.addRow("外部编辑器:", editor_path_layout)
        
        self.auto_stage_on_commit = QCheckBox("提交时自动暂存文件")
        editor_layout.addRow(self.auto_stage_on_commit)
        
        scroll_layout.addWidget(editor_group)
        
        # 语言设置
        language_group = QGroupBox("语言设置")
        language_layout = QFormLayout(language_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        language_layout.addRow("界面语言:", self.language_combo)
        
        scroll_layout.addWidget(language_group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        self.tab_widget.addTab(widget, "常规")
        
    def create_git_tab(self):
        """创建Git设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 用户信息
        user_group = QGroupBox("用户信息")
        user_layout = QFormLayout(user_group)
        
        self.git_user_name = QLineEdit()
        user_layout.addRow("用户名:", self.git_user_name)
        
        self.git_user_email = QLineEdit()
        user_layout.addRow("邮箱:", self.git_user_email)
        
        scroll_layout.addWidget(user_group)
        
        # SSH设置
        ssh_group = QGroupBox("SSH设置")
        ssh_layout = QFormLayout(ssh_group)
        
        self.ssh_key_path = QLineEdit()
        ssh_key_layout = QHBoxLayout()
        ssh_key_layout.addWidget(self.ssh_key_path)
        
        browse_ssh_btn = QPushButton("浏览...")
        browse_ssh_btn.clicked.connect(self.browse_ssh_key)
        ssh_key_layout.addWidget(browse_ssh_btn)
        
        ssh_layout.addRow("SSH私钥路径:", ssh_key_layout)
        
        scroll_layout.addWidget(ssh_group)
        
        # 提交设置
        commit_group = QGroupBox("提交设置")
        commit_layout = QFormLayout(commit_group)
        
        self.default_commit_message = QTextEdit()
        self.default_commit_message.setMaximumHeight(80)
        self.default_commit_message.setPlaceholderText("可选的默认提交消息模板...")
        commit_layout.addRow("默认提交消息:", self.default_commit_message)
        
        self.auto_sign_commits = QCheckBox("自动签名提交")
        commit_layout.addRow(self.auto_sign_commits)
        
        self.verify_ssl = QCheckBox("验证SSL证书")
        self.verify_ssl.setChecked(True)
        commit_layout.addRow(self.verify_ssl)
        
        scroll_layout.addWidget(commit_group)
        
        # 远程设置
        remote_group = QGroupBox("远程仓库设置")
        remote_layout = QFormLayout(remote_group)
        
        self.default_remote_name = QLineEdit()
        self.default_remote_name.setText("origin")
        remote_layout.addRow("默认远程名称:", self.default_remote_name)
        
        self.fetch_before_push = QCheckBox("推送前自动拉取")
        remote_layout.addRow(self.fetch_before_push)
        
        self.push_timeout = QSpinBox()
        self.push_timeout.setRange(10, 300)
        self.push_timeout.setValue(60)
        self.push_timeout.setSuffix(" 秒")
        remote_layout.addRow("推送超时时间:", self.push_timeout)
        
        scroll_layout.addWidget(remote_group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        self.tab_widget.addTab(widget, "Git")
        
    def create_advanced_tab(self):
        """创建高级设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 性能设置
        performance_group = QGroupBox("性能设置")
        performance_layout = QFormLayout(performance_group)
        
        self.max_history_entries = QSpinBox()
        self.max_history_entries.setRange(50, 1000)
        self.max_history_entries.setValue(200)
        performance_layout.addRow("最大历史记录:", self.max_history_entries)
        
        self.enable_file_cache = QCheckBox("启用文件缓存")
        self.enable_file_cache.setChecked(True)
        performance_layout.addRow(self.enable_file_cache)
        
        self.cache_size_mb = QSpinBox()
        self.cache_size_mb.setRange(10, 500)
        self.cache_size_mb.setValue(50)
        self.cache_size_mb.setSuffix(" MB")
        performance_layout.addRow("缓存大小:", self.cache_size_mb)
        
        layout.addWidget(performance_group)
        
        # 调试设置
        debug_group = QGroupBox("调试设置")
        debug_layout = QFormLayout(debug_group)
        
        self.enable_debug_log = QCheckBox("启用调试日志")
        debug_layout.addRow(self.enable_debug_log)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["ERROR", "WARNING", "INFO", "DEBUG"])
        self.log_level_combo.setCurrentText("INFO")
        debug_layout.addRow("日志级别:", self.log_level_combo)
        
        self.log_file_path = QLineEdit()
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(self.log_file_path)
        
        browse_log_btn = QPushButton("浏览...")
        browse_log_btn.clicked.connect(self.browse_log_path)
        log_path_layout.addWidget(browse_log_btn)
        
        debug_layout.addRow("日志文件路径:", log_path_layout)
        
        layout.addWidget(debug_group)
        
        # 实验性功能
        experimental_group = QGroupBox("实验性功能")
        experimental_layout = QFormLayout(experimental_group)
        
        self.enable_git_lfs = QCheckBox("启用Git LFS支持")
        experimental_layout.addRow(self.enable_git_lfs)
        
        self.enable_submodules = QCheckBox("启用子模块支持")
        experimental_layout.addRow(self.enable_submodules)
        
        self.enable_hooks = QCheckBox("启用Git钩子")
        experimental_layout.addRow(self.enable_hooks)
        
        layout.addWidget(experimental_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "高级")
        
    def browse_clone_path(self):
        """浏览克隆路径"""
        path = QFileDialog.getExistingDirectory(
            self, "选择默认克隆路径", self.default_clone_path_edit.text()
        )
        if path:
            self.default_clone_path_edit.setText(path)
            
    def browse_editor_path(self):
        """浏览编辑器路径"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择外部编辑器", self.external_editor_path.text(),
            "可执行文件 (*.exe);;所有文件 (*)"
        )
        if path:
            self.external_editor_path.setText(path)
            
    def browse_ssh_key(self):
        """浏览SSH密钥"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择SSH私钥文件", self.ssh_key_path.text(),
            "私钥文件 (*.pem *.key id_rsa);;所有文件 (*)"
        )
        if path:
            self.ssh_key_path.setText(path)
            
    def browse_log_path(self):
        """浏览日志路径"""
        path, _ = QFileDialog.getSaveFileName(
            self, "选择日志文件路径", self.log_file_path.text(),
            "日志文件 (*.log);;文本文件 (*.txt);;所有文件 (*)"
        )
        if path:
            self.log_file_path.setText(path)
            
    def load_settings(self):
        """加载设置"""
        try:
            config = self.config_manager.get_all_settings()
            
            # 常规设置
            self.default_clone_path_edit.setText(config.get('default_clone_path', ''))
            self.auto_open_cloned_repo.setChecked(config.get('auto_open_cloned_repo', True))
            self.remember_recent_repos.setChecked(config.get('remember_recent_repos', True))
            self.max_recent_repos.setValue(config.get('max_recent_repos', 10))
            self.external_editor_path.setText(config.get('external_editor_path', ''))
            self.auto_stage_on_commit.setChecked(config.get('auto_stage_on_commit', False))
            
            language = config.get('language', 'zh_CN')
            self.language_combo.setCurrentText("简体中文" if language == 'zh_CN' else "English")
            
            # Git设置
            git_config = self.git_manager.get_config()
            self.git_user_name.setText(git_config.get('user.name', ''))
            self.git_user_email.setText(git_config.get('user.email', ''))
            
            self.ssh_key_path.setText(config.get('ssh_key_path', ''))
            self.default_commit_message.setPlainText(config.get('default_commit_message', ''))
            self.auto_sign_commits.setChecked(config.get('auto_sign_commits', False))
            self.verify_ssl.setChecked(config.get('verify_ssl', True))
            self.default_remote_name.setText(config.get('default_remote_name', 'origin'))
            self.fetch_before_push.setChecked(config.get('fetch_before_push', False))
            self.push_timeout.setValue(config.get('push_timeout', 60))
            
            # 高级设置
            self.max_history_entries.setValue(config.get('max_history_entries', 200))
            self.enable_file_cache.setChecked(config.get('enable_file_cache', True))
            self.cache_size_mb.setValue(config.get('cache_size_mb', 50))
            self.enable_debug_log.setChecked(config.get('enable_debug_log', False))
            self.log_level_combo.setCurrentText(config.get('log_level', 'INFO'))
            self.log_file_path.setText(config.get('log_file_path', ''))
            self.enable_git_lfs.setChecked(config.get('enable_git_lfs', False))
            self.enable_submodules.setChecked(config.get('enable_submodules', False))
            self.enable_hooks.setChecked(config.get('enable_hooks', False))
            
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载设置时出错: {str(e)}")
            
    def save_settings(self):
        """保存设置"""
        try:
            # 收集所有设置
            settings = {
                # 常规设置
                'default_clone_path': self.default_clone_path_edit.text(),
                'auto_open_cloned_repo': self.auto_open_cloned_repo.isChecked(),
                'remember_recent_repos': self.remember_recent_repos.isChecked(),
                'max_recent_repos': self.max_recent_repos.value(),
                'external_editor_path': self.external_editor_path.text(),
                'auto_stage_on_commit': self.auto_stage_on_commit.isChecked(),
                'language': 'zh_CN' if self.language_combo.currentText() == '简体中文' else 'en_US',
                
                # Git设置
                'ssh_key_path': self.ssh_key_path.text(),
                'default_commit_message': self.default_commit_message.toPlainText(),
                'auto_sign_commits': self.auto_sign_commits.isChecked(),
                'verify_ssl': self.verify_ssl.isChecked(),
                'default_remote_name': self.default_remote_name.text(),
                'fetch_before_push': self.fetch_before_push.isChecked(),
                'push_timeout': self.push_timeout.value(),
                
                # 高级设置
                'max_history_entries': self.max_history_entries.value(),
                'enable_file_cache': self.enable_file_cache.isChecked(),
                'cache_size_mb': self.cache_size_mb.value(),
                'enable_debug_log': self.enable_debug_log.isChecked(),
                'log_level': self.log_level_combo.currentText(),
                'log_file_path': self.log_file_path.text(),
                'enable_git_lfs': self.enable_git_lfs.isChecked(),
                'enable_submodules': self.enable_submodules.isChecked(),
                'enable_hooks': self.enable_hooks.isChecked(),
            }
            
            # 保存应用设置
            for key, value in settings.items():
                self.config_manager.set_setting(key, value)
            
            # 保存配置到文件
            if not self.config_manager.save_config():
                raise Exception("配置文件保存失败")
                
            # 保存Git用户信息
            if self.git_user_name.text().strip():
                self.git_manager.set_config('user.name', self.git_user_name.text().strip())
            if self.git_user_email.text().strip():
                self.git_manager.set_config('user.email', self.git_user_email.text().strip())
                
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置时出错: {str(e)}")
            return False
            
    def restore_defaults(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self, "确认", "确定要恢复所有设置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 重置配置管理器
                self.config_manager.reset_to_defaults()
                
                # 重新加载设置
                self.load_settings()
                
                QMessageBox.information(self, "成功", "已恢复默认设置")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"恢复默认设置时出错: {str(e)}")
                
    def accept_settings(self):
        """确认设置"""
        if self.save_settings():
            self.settings_changed.emit()
            self.accept()
