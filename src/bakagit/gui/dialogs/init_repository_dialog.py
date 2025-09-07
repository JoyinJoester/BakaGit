"""
初始化仓库对话框

用于创建新的Git仓库。
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox,
    QFileDialog, QMessageBox, QTextEdit, QGroupBox,
    QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
import os


class InitRepositoryWorker(QThread):
    """初始化仓库工作线程"""
    
    progress_updated = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, git_manager, repo_path, bare=False):
        super().__init__()
        self.git_manager = git_manager
        self.repo_path = repo_path
        self.bare = bare
    
    def run(self):
        """执行初始化"""
        try:
            self.progress_updated.emit("正在初始化Git仓库...")
            
            success = self.git_manager.init_repository(self.repo_path, self.bare)
            
            if success:
                self.progress_updated.emit("初始化完成")
                self.finished_signal.emit(True, "Git仓库初始化成功")
            else:
                self.finished_signal.emit(False, "Git仓库初始化失败")
                
        except Exception as e:
            self.finished_signal.emit(False, f"初始化失败: {str(e)}")


class InitRepositoryDialog(QDialog):
    """初始化仓库对话框"""
    
    repository_initialized = pyqtSignal(str)  # 发送初始化完成的仓库路径
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.git_manager = None
        self.worker = None
        self.init_ui()
    
    def set_git_manager(self, git_manager):
        """设置Git管理器"""
        self.git_manager = git_manager
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('初始化Git仓库')
        self.setModal(True)
        self.resize(500, 350)
        
        layout = QVBoxLayout(self)
        
        # 仓库路径设置
        path_group = QGroupBox('仓库路径')
        path_layout = QVBoxLayout(path_group)
        
        path_form = QFormLayout()
        
        # 路径选择
        path_select_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText('选择或输入仓库路径')
        path_select_layout.addWidget(self.path_edit)
        
        self.browse_btn = QPushButton('浏览...')
        self.browse_btn.clicked.connect(self.browse_path)
        path_select_layout.addWidget(self.browse_btn)
        
        path_form.addRow('仓库路径:', path_select_layout)
        
        # 仓库名称
        self.repo_name_edit = QLineEdit()
        self.repo_name_edit.setPlaceholderText('新仓库名称')
        self.repo_name_edit.textChanged.connect(self.update_full_path)
        path_form.addRow('仓库名称:', self.repo_name_edit)
        
        # 完整路径显示
        self.full_path_label = QLabel()
        self.full_path_label.setStyleSheet('color: #666; font-style: italic;')
        path_form.addRow('完整路径:', self.full_path_label)
        
        path_layout.addLayout(path_form)
        layout.addWidget(path_group)
        
        # 初始化选项
        options_group = QGroupBox('初始化选项')
        options_layout = QVBoxLayout(options_group)
        
        self.bare_checkbox = QCheckBox('创建裸仓库（bare repository）')
        self.bare_checkbox.setToolTip('裸仓库没有工作目录，通常用作服务器仓库')
        options_layout.addWidget(self.bare_checkbox)
        
        self.create_readme_checkbox = QCheckBox('创建README.md文件')
        self.create_readme_checkbox.setChecked(True)
        options_layout.addWidget(self.create_readme_checkbox)
        
        self.create_gitignore_checkbox = QCheckBox('创建.gitignore文件')
        self.create_gitignore_checkbox.setChecked(True)
        options_layout.addWidget(self.create_gitignore_checkbox)
        
        layout.addWidget(options_group)
        
        # 初始提交信息
        commit_group = QGroupBox('初始提交')
        commit_layout = QVBoxLayout(commit_group)
        
        self.commit_message_edit = QTextEdit()
        self.commit_message_edit.setMaximumHeight(80)
        self.commit_message_edit.setPlaceholderText('初始提交信息（可选）')
        self.commit_message_edit.setText('Initial commit')
        commit_layout.addWidget(self.commit_message_edit)
        
        layout.addWidget(commit_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.init_btn = QPushButton('初始化仓库')
        self.init_btn.clicked.connect(self.init_repository)
        button_layout.addWidget(self.init_btn)
        
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def browse_path(self):
        """浏览路径"""
        directory = QFileDialog.getExistingDirectory(self, '选择仓库父目录')
        if directory:
            self.path_edit.setText(directory)
            self.update_full_path()
    
    def update_full_path(self):
        """更新完整路径显示"""
        base_path = self.path_edit.text().strip()
        repo_name = self.repo_name_edit.text().strip()
        
        if base_path and repo_name:
            full_path = os.path.join(base_path, repo_name)
            self.full_path_label.setText(full_path)
        else:
            self.full_path_label.setText('')
    
    def init_repository(self):
        """初始化仓库"""
        if not self.git_manager:
            QMessageBox.warning(self, '错误', '未设置Git管理器')
            return
        
        base_path = self.path_edit.text().strip()
        repo_name = self.repo_name_edit.text().strip()
        
        if not base_path:
            QMessageBox.warning(self, '输入错误', '请选择仓库路径')
            return
        
        if not repo_name:
            QMessageBox.warning(self, '输入错误', '请输入仓库名称')
            return
        
        full_path = os.path.join(base_path, repo_name)
        
        # 检查路径是否已存在
        if os.path.exists(full_path):
            if os.listdir(full_path):  # 目录不为空
                reply = QMessageBox.question(
                    self, '确认', 
                    f'目录 "{full_path}" 已存在且不为空。\\n是否继续初始化？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
        
        # 禁用按钮并显示进度
        self.init_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_label.setVisible(True)
        
        # 启动工作线程
        self.worker = InitRepositoryWorker(
            self.git_manager, 
            full_path, 
            self.bare_checkbox.isChecked()
        )
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished_signal.connect(self.on_init_finished)
        self.worker.start()
    
    def update_progress(self, message):
        """更新进度"""
        self.progress_label.setText(message)
    
    def on_init_finished(self, success, message):
        """初始化完成"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.init_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        
        if success:
            repo_path = os.path.join(self.path_edit.text().strip(), self.repo_name_edit.text().strip())
            
            try:
                # 创建初始文件
                self.create_initial_files(repo_path)
                
                # 执行初始提交
                self.create_initial_commit(repo_path)
                
                QMessageBox.information(self, '成功', message)
                self.repository_initialized.emit(repo_path)
                self.accept()
                
            except Exception as e:
                QMessageBox.warning(self, '警告', f'仓库初始化成功，但创建初始文件时出错: {str(e)}')
                self.repository_initialized.emit(repo_path)
                self.accept()
        else:
            QMessageBox.critical(self, '失败', message)
    
    def create_initial_files(self, repo_path):
        """创建初始文件"""
        try:
            if self.create_readme_checkbox.isChecked():
                readme_path = os.path.join(repo_path, 'README.md')
                repo_name = os.path.basename(repo_path)
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(f'# {repo_name}\\n\\n')
                    f.write('这是一个新的Git仓库。\\n\\n')
                    f.write('## 说明\\n\\n')
                    f.write('请在这里添加项目描述。\\n')
            
            if self.create_gitignore_checkbox.isChecked():
                gitignore_path = os.path.join(repo_path, '.gitignore')
                with open(gitignore_path, 'w', encoding='utf-8') as f:
                    f.write('# 临时文件\\n')
                    f.write('*.tmp\\n')
                    f.write('*.temp\\n')
                    f.write('*~\\n\\n')
                    f.write('# 日志文件\\n')
                    f.write('*.log\\n\\n')
                    f.write('# 编译输出\\n')
                    f.write('*.o\\n')
                    f.write('*.obj\\n')
                    f.write('*.exe\\n\\n')
                    f.write('# IDE文件\\n')
                    f.write('.vscode/\\n')
                    f.write('.idea/\\n')
                    f.write('*.swp\\n')
                    f.write('*.swo\\n\\n')
                    f.write('# 系统文件\\n')
                    f.write('.DS_Store\\n')
                    f.write('Thumbs.db\\n')
                    
        except Exception as e:
            print(f'创建初始文件时出错: {e}')
    
    def create_initial_commit(self, repo_path):
        """创建初始提交"""
        try:
            commit_message = self.commit_message_edit.toPlainText().strip()
            if not commit_message:
                return
            
            if not self.bare_checkbox.isChecked():  # 只有非裸仓库才能提交
                # 添加所有文件到暂存区
                self.git_manager.stage_all()
                
                # 执行提交
                self.git_manager.commit(commit_message)
                
        except Exception as e:
            print(f'创建初始提交时出错: {e}')
