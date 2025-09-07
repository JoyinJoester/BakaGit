"""
克隆仓库对话框

提供用户友好的Git仓库克隆界面。
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QProgressBar, QLabel,
    QFileDialog, QMessageBox, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from ...core.git_manager import GitManager
from ...core.utils import is_valid_git_url


class CloneWorker(QThread):
    """克隆操作的工作线程"""
    
    progress = pyqtSignal(str)  # 进度信息
    finished = pyqtSignal(bool, str)  # 完成信号：(成功, 消息)
    
    def __init__(self, url: str, target_path: str):
        super().__init__()
        self.url = url
        self.target_path = target_path
        self.git_manager = GitManager()
    
    def run(self):
        """执行克隆操作"""
        try:
            self.progress.emit("正在验证仓库URL...")
            
            # 验证URL
            if not is_valid_git_url(self.url):
                self.finished.emit(False, "无效的Git仓库URL")
                return
            
            self.progress.emit("正在创建目标目录...")
            
            # 确保目标路径存在
            target_dir = Path(self.target_path)
            if target_dir.exists():
                if any(target_dir.iterdir()):  # 目录不为空
                    self.finished.emit(False, f"目标目录不为空: {self.target_path}")
                    return
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
            
            self.progress.emit("正在克隆仓库...")
            
            # 执行克隆
            success = self.git_manager.clone_repository(self.url, self.target_path)
            
            if success:
                self.progress.emit("克隆完成！")
                self.finished.emit(True, f"仓库已成功克隆到: {self.target_path}")
            else:
                self.finished.emit(False, "克隆失败，请检查URL和网络连接")
                
        except Exception as e:
            self.finished.emit(False, f"克隆过程中出现错误: {str(e)}")


class CloneRepositoryDialog(QDialog):
    """克隆仓库对话框"""
    
    repository_cloned = pyqtSignal(str)  # 克隆成功信号，传递仓库路径
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("克隆Git仓库")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        
        # 工作线程
        self.clone_worker = None
        
        # 初始化UI
        self.init_ui()
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 16px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
            QProgressBar {
                background-color: #252525;
                border: 1px solid #404040;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 5px;
            }
            QTextEdit {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #0078d4;
                padding: 0 8px;
            }
        """)
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("克隆Git仓库")
        title_label.setFont(QFont('', 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #0078d4; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 输入区域
        input_group = QGroupBox("仓库信息")
        input_layout = QFormLayout(input_group)
        
        # 仓库URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入Git仓库URL (https://github.com/user/repo.git)")
        self.url_input.textChanged.connect(self.validate_inputs)
        input_layout.addRow("仓库URL:", self.url_input)
        
        # 目标路径
        target_layout = QHBoxLayout()
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("选择克隆目标路径")
        self.target_input.textChanged.connect(self.validate_inputs)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_target_path)
        
        target_layout.addWidget(self.target_input)
        target_layout.addWidget(browse_btn)
        input_layout.addRow("目标路径:", target_layout)
        
        layout.addWidget(input_group)
        
        # 进度显示区域
        progress_group = QGroupBox("克隆进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_label = QLabel("准备就绪")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # 日志输出
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(100)
        self.log_output.setPlaceholderText("操作日志将显示在这里...")
        progress_layout.addWidget(self.log_output)
        
        layout.addWidget(progress_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 填充空间
        button_layout.addStretch()
        
        # 克隆按钮
        self.clone_btn = QPushButton("开始克隆")
        self.clone_btn.clicked.connect(self.start_clone)
        self.clone_btn.setEnabled(False)
        button_layout.addWidget(self.clone_btn)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def validate_inputs(self):
        """验证输入内容"""
        url = self.url_input.text().strip()
        target = self.target_input.text().strip()
        
        valid = bool(url and target and is_valid_git_url(url))
        self.clone_btn.setEnabled(valid)
        
        if url and not is_valid_git_url(url):
            self.log_message("❌ 无效的Git仓库URL", "error")
        elif valid:
            self.log_message("✅ 输入验证通过", "success")
    
    def browse_target_path(self):
        """浏览目标路径"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择克隆目标目录",
            str(Path.home())
        )
        
        if directory:
            # 自动添加仓库名称作为子目录
            url = self.url_input.text().strip()
            if url:
                repo_name = Path(url).stem
                if repo_name.endswith('.git'):
                    repo_name = repo_name[:-4]
                target_path = str(Path(directory) / repo_name)
                self.target_input.setText(target_path)
            else:
                self.target_input.setText(directory)
    
    def start_clone(self):
        """开始克隆操作"""
        url = self.url_input.text().strip()
        target_path = self.target_input.text().strip()
        
        # 禁用按钮
        self.clone_btn.setEnabled(False)
        self.cancel_btn.setText("停止")
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 清空日志
        self.log_output.clear()
        self.log_message(f"🚀 开始克隆: {url}", "info")
        self.log_message(f"📁 目标路径: {target_path}", "info")
        
        # 创建并启动工作线程
        self.clone_worker = CloneWorker(url, target_path)
        self.clone_worker.progress.connect(self.update_progress)
        self.clone_worker.finished.connect(self.clone_finished)
        self.clone_worker.start()
    
    def update_progress(self, message: str):
        """更新进度"""
        self.progress_label.setText(message)
        self.log_message(f"ℹ️ {message}", "info")
    
    def clone_finished(self, success: bool, message: str):
        """克隆完成"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 恢复按钮
        self.clone_btn.setEnabled(True)
        self.cancel_btn.setText("关闭")
        
        if success:
            self.log_message(f"✅ {message}", "success")
            self.progress_label.setText("克隆成功！")
            
            # 发射信号
            repo_path = self.target_input.text().strip()
            self.repository_cloned.emit(repo_path)
            
            # 显示成功消息
            QMessageBox.information(self, "克隆成功", message)
            self.accept()
        else:
            self.log_message(f"❌ {message}", "error")
            self.progress_label.setText("克隆失败")
            QMessageBox.warning(self, "克隆失败", message)
    
    def log_message(self, message: str, level: str = "info"):
        """添加日志消息"""
        color_map = {
            "info": "#ffffff",
            "success": "#4caf50", 
            "error": "#f44336",
            "warning": "#ff9800"
        }
        
        color = color_map.get(level, "#ffffff")
        formatted_message = f'<span style="color: {color};">{message}</span>'
        
        self.log_output.append(formatted_message)
        
        # 滚动到底部
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """关闭事件"""
        # 如果正在克隆，询问用户是否确定关闭
        if self.clone_worker and self.clone_worker.isRunning():
            reply = QMessageBox.question(
                self, "确认", 
                "克隆操作正在进行中，确定要关闭吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.clone_worker.terminate()
                self.clone_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
