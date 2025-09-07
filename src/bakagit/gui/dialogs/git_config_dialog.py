"""
Git配置对话框

用于设置Git用户信息和其他配置。
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTabWidget, QWidget,
    QLabel, QCheckBox, QGroupBox, QMessageBox,
    QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class GitConfigDialog(QDialog):
    """Git配置对话框"""
    
    config_saved = pyqtSignal()
    
    def __init__(self, git_manager, parent=None):
        super().__init__(parent)
        self.git_manager = git_manager
        self.init_ui()
        self.load_current_config()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('Git配置')
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 用户信息选项卡
        self.create_user_info_tab()
        
        # 全局设置选项卡
        self.create_global_settings_tab()
        
        # 仓库设置选项卡
        self.create_repo_settings_tab()
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_btn = QPushButton('应用')
        self.apply_btn.clicked.connect(self.apply_config)
        button_layout.addWidget(self.apply_btn)
        
        self.ok_btn = QPushButton('确定')
        self.ok_btn.clicked.connect(self.accept_config)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_user_info_tab(self):
        """创建用户信息选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 全局用户信息
        global_group = QGroupBox('全局用户信息')
        global_layout = QFormLayout(global_group)
        
        self.global_name_edit = QLineEdit()
        self.global_name_edit.setPlaceholderText('您的全名')
        global_layout.addRow('姓名:', self.global_name_edit)
        
        self.global_email_edit = QLineEdit()
        self.global_email_edit.setPlaceholderText('your.email@example.com')
        global_layout.addRow('邮箱:', self.global_email_edit)
        
        layout.addWidget(global_group)
        
        # 当前仓库用户信息
        repo_group = QGroupBox('当前仓库用户信息')
        repo_layout = QFormLayout(repo_group)
        
        self.repo_name_edit = QLineEdit()
        self.repo_name_edit.setPlaceholderText('留空使用全局设置')
        repo_layout.addRow('姓名:', self.repo_name_edit)
        
        self.repo_email_edit = QLineEdit()
        self.repo_email_edit.setPlaceholderText('留空使用全局设置')
        repo_layout.addRow('邮箱:', self.repo_email_edit)
        
        layout.addWidget(repo_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, '用户信息')
    
    def create_global_settings_tab(self):
        """创建全局设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 编辑器设置
        editor_group = QGroupBox('编辑器设置')
        editor_layout = QFormLayout(editor_group)
        
        self.core_editor_edit = QLineEdit()
        self.core_editor_edit.setPlaceholderText('默认文本编辑器（如: code, vim, nano）')
        editor_layout.addRow('默认编辑器:', self.core_editor_edit)
        
        layout.addWidget(editor_group)
        
        # 行尾符设置
        crlf_group = QGroupBox('行尾符设置')
        crlf_layout = QFormLayout(crlf_group)
        
        self.core_crlf_combo = QComboBox()
        self.core_crlf_combo.addItems(['auto', 'true', 'false', 'input'])
        crlf_layout.addRow('autocrlf:', self.core_crlf_combo)
        
        layout.addWidget(crlf_group)
        
        # 推送设置
        push_group = QGroupBox('推送设置')
        push_layout = QFormLayout(push_group)
        
        self.push_default_combo = QComboBox()
        self.push_default_combo.addItems(['simple', 'matching', 'upstream', 'current'])
        push_layout.addRow('push.default:', self.push_default_combo)
        
        layout.addWidget(push_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, '全局设置')
    
    def create_repo_settings_tab(self):
        """创建仓库设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 远程仓库设置
        remote_group = QGroupBox('远程仓库')
        remote_layout = QVBoxLayout(remote_group)
        
        info_label = QLabel('当前仓库的远程仓库信息:')
        remote_layout.addWidget(info_label)
        
        self.remote_info_text = QTextEdit()
        self.remote_info_text.setMaximumHeight(150)
        self.remote_info_text.setReadOnly(True)
        remote_layout.addWidget(self.remote_info_text)
        
        layout.addWidget(remote_group)
        
        # 分支设置
        branch_group = QGroupBox('分支设置')
        branch_layout = QFormLayout(branch_group)
        
        self.default_branch_edit = QLineEdit()
        self.default_branch_edit.setPlaceholderText('main 或 master')
        branch_layout.addRow('默认分支:', self.default_branch_edit)
        
        layout.addWidget(branch_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, '仓库设置')
    
    def load_current_config(self):
        """加载当前配置"""
        try:
            # 加载用户信息
            user_info = self.git_manager.get_user_info()
            
            if user_info['name']:
                self.global_name_edit.setText(user_info['name'])
            if user_info['email']:
                self.global_email_edit.setText(user_info['email'])
            if user_info['local_name']:
                self.repo_name_edit.setText(user_info['local_name'])
            if user_info['local_email']:
                self.repo_email_edit.setText(user_info['local_email'])
            
            # 加载其他配置
            editor = self.git_manager.get_git_config('core.editor', global_config=True)
            if editor:
                self.core_editor_edit.setText(editor)
            
            autocrlf = self.git_manager.get_git_config('core.autocrlf', global_config=True)
            if autocrlf:
                index = self.core_crlf_combo.findText(autocrlf)
                if index >= 0:
                    self.core_crlf_combo.setCurrentIndex(index)
            
            push_default = self.git_manager.get_git_config('push.default', global_config=True)
            if push_default:
                index = self.push_default_combo.findText(push_default)
                if index >= 0:
                    self.push_default_combo.setCurrentIndex(index)
            
            # 加载远程仓库信息
            self.load_remote_info()
            
        except Exception as e:
            QMessageBox.warning(self, '警告', f'加载配置时出错: {str(e)}')
    
    def load_remote_info(self):
        """加载远程仓库信息"""
        try:
            if not self.git_manager.repo:
                self.remote_info_text.setText('当前没有打开仓库')
                return
            
            remotes_info = []
            for remote in self.git_manager.repo.remotes:
                remotes_info.append(f"{remote.name}: {list(remote.urls)[0] if remote.urls else '无URL'}")
            
            if remotes_info:
                self.remote_info_text.setText('\\n'.join(remotes_info))
            else:
                self.remote_info_text.setText('当前仓库没有配置远程仓库')
                
        except Exception as e:
            self.remote_info_text.setText(f'获取远程仓库信息失败: {str(e)}')
    
    def apply_config(self):
        """应用配置"""
        try:
            # 保存全局用户信息
            global_name = self.global_name_edit.text().strip()
            global_email = self.global_email_edit.text().strip()
            
            if global_name and global_email:
                if not self.git_manager.set_user_info(global_name, global_email, global_config=True):
                    QMessageBox.warning(self, '警告', '设置全局用户信息失败')
                    return
            
            # 保存仓库用户信息
            repo_name = self.repo_name_edit.text().strip()
            repo_email = self.repo_email_edit.text().strip()
            
            if repo_name and repo_email and self.git_manager.repo:
                if not self.git_manager.set_user_info(repo_name, repo_email, global_config=False):
                    QMessageBox.warning(self, '警告', '设置仓库用户信息失败')
                    return
            
            # 保存其他配置
            editor = self.core_editor_edit.text().strip()
            if editor:
                self.git_manager.set_git_config('core.editor', editor, global_config=True)
            
            autocrlf = self.core_crlf_combo.currentText()
            self.git_manager.set_git_config('core.autocrlf', autocrlf, global_config=True)
            
            push_default = self.push_default_combo.currentText()
            self.git_manager.set_git_config('push.default', push_default, global_config=True)
            
            QMessageBox.information(self, '成功', 'Git配置已保存')
            self.config_saved.emit()
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存配置时出错: {str(e)}')
    
    def accept_config(self):
        """确定并关闭"""
        self.apply_config()
        self.accept()
