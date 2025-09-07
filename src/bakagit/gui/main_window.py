"""
主窗口模块

定义BakaGit应用程序的主窗口界面。
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMenuBar, QToolBar, QStatusBar,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QTextEdit, QLabel, QPushButton, QFileDialog, QMessageBox,
    QTabWidget, QGroupBox, QGridLayout, QProgressBar, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont, QPixmap

from ..core.git_manager import GitManager
from ..core.config import ConfigManager
from ..core.utils import is_git_installed, get_git_version
from .dialogs.clone_dialog import CloneRepositoryDialog


class MainWindow(QMainWindow):
    """BakaGit主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化核心组件
        self.git_manager = GitManager()
        self.config_manager = ConfigManager()
        
        # 当前仓库路径
        self.current_repo_path = None
        
        # 初始化UI
        self.init_ui()
        
        # 加载配置
        self.load_settings()
        
        # 检查Git环境
        self.check_git_environment()
        
        # 初始化界面状态
        self.refresh_repository()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("BakaGit - 笨蛋都会用的Git")
        self.setMinimumSize(1000, 700)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # 创建左侧面板（仓库列表）
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # 创建右侧面板（主工作区）
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # 设置分割器比例
        main_splitter.setSizes([250, 750])
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        # 新建仓库
        new_repo_action = QAction('新建仓库', self)
        new_repo_action.setShortcut('Ctrl+N')
        new_repo_action.triggered.connect(self.new_repository)
        file_menu.addAction(new_repo_action)
        
        # 打开仓库
        open_repo_action = QAction('打开仓库', self)
        open_repo_action.setShortcut('Ctrl+O')
        open_repo_action.triggered.connect(self.open_repository)
        file_menu.addAction(open_repo_action)
        
        # 克隆仓库
        clone_repo_action = QAction('克隆仓库', self)
        clone_repo_action.setShortcut('Ctrl+Shift+O')
        clone_repo_action.triggered.connect(self.clone_repository)
        file_menu.addAction(clone_repo_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        # 撤销
        undo_action = QAction('撤销', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo_last_action)
        edit_menu.addAction(undo_action)
        
        edit_menu.addSeparator()
        
        # 全选文件
        select_all_action = QAction('全选文件', self)
        select_all_action.setShortcut('Ctrl+A')
        select_all_action.triggered.connect(self.select_all_files)
        edit_menu.addAction(select_all_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        # 刷新
        refresh_action = QAction('刷新', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_repository)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        # 显示/隐藏工具栏
        toggle_toolbar_action = QAction('显示工具栏', self)
        toggle_toolbar_action.setCheckable(True)
        toggle_toolbar_action.setChecked(True)
        toggle_toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(toggle_toolbar_action)
        
        # 显示/隐藏状态栏
        toggle_status_action = QAction('显示状态栏', self)
        toggle_status_action.setCheckable(True)
        toggle_status_action.setChecked(True)
        toggle_status_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(toggle_status_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        # Git配置
        git_config_action = QAction('Git配置', self)
        git_config_action.triggered.connect(self.open_git_config)
        tools_menu.addAction(git_config_action)
        
        # 清理仓库
        cleanup_action = QAction('清理仓库', self)
        cleanup_action.triggered.connect(self.cleanup_repository)
        tools_menu.addAction(cleanup_action)
        
        # 设置菜单（独立出来）
        settings_menu = menubar.addMenu('设置')
        
        # 完整设置
        full_settings_action = QAction('完整设置', self)
        full_settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(full_settings_action)
        
        # 重置设置
        reset_settings_action = QAction('重置所有设置', self)
        reset_settings_action.triggered.connect(self.reset_all_settings)
        settings_menu.addAction(reset_settings_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        # 快速教程
        tutorial_action = QAction('快速教程', self)
        tutorial_action.triggered.connect(self.show_tutorial)
        help_menu.addAction(tutorial_action)
        
        help_menu.addSeparator()
        
        # 关于
        about_action = QAction('关于 BakaGit', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        """创建工具栏"""
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # 仓库操作组
        # 新建仓库按钮
        new_repo_btn = QPushButton('新建仓库')
        new_repo_btn.setToolTip('初始化一个新的Git仓库')
        new_repo_btn.clicked.connect(self.new_repository)
        self.toolbar.addWidget(new_repo_btn)
        
        # 打开仓库按钮
        open_repo_btn = QPushButton('打开仓库')
        open_repo_btn.setToolTip('打开现有的Git仓库')
        open_repo_btn.clicked.connect(self.open_repository)
        self.toolbar.addWidget(open_repo_btn)
        
        # 克隆按钮
        clone_btn = QPushButton('克隆仓库')
        clone_btn.setToolTip('从远程地址克隆仓库')
        clone_btn.clicked.connect(self.clone_repository)
        self.toolbar.addWidget(clone_btn)
        
        self.toolbar.addSeparator()
        
        # 文件操作组
        # 添加文件到暂存区
        stage_btn = QPushButton('暂存文件')
        stage_btn.setToolTip('将选中文件添加到暂存区')
        stage_btn.clicked.connect(self.stage_selected_files)
        self.toolbar.addWidget(stage_btn)
        
        # 提交按钮
        commit_btn = QPushButton('提交')
        commit_btn.setToolTip('提交暂存区的更改')
        commit_btn.clicked.connect(self.commit_changes)
        self.toolbar.addWidget(commit_btn)
        
        self.toolbar.addSeparator()
        
        # 远程同步组
        # 拉取按钮
        pull_btn = QPushButton('拉取')
        pull_btn.setToolTip('从远程仓库拉取最新更改')
        pull_btn.clicked.connect(self.pull_changes)
        self.toolbar.addWidget(pull_btn)
        
        # 推送按钮
        push_btn = QPushButton('推送')
        push_btn.setToolTip('推送本地更改到远程仓库')
        push_btn.clicked.connect(self.push_changes)
        self.toolbar.addWidget(push_btn)
        
        self.toolbar.addSeparator()
        
        # 分支管理组
        # 分支下拉菜单
        self.branch_combo = QComboBox()
        self.branch_combo.setToolTip('当前分支，点击切换')
        self.branch_combo.setMinimumWidth(120)
        self.branch_combo.currentTextChanged.connect(self.switch_branch)
        self.toolbar.addWidget(self.branch_combo)
        
        # 新建分支按钮
        new_branch_btn = QPushButton('新建分支')
        new_branch_btn.setToolTip('创建新分支')
        new_branch_btn.clicked.connect(self.create_new_branch)
        self.toolbar.addWidget(new_branch_btn)
        
        self.toolbar.addSeparator()
        
        # 视图和工具组
        # 刷新按钮
        refresh_btn = QPushButton('刷新')
        refresh_btn.setToolTip('刷新仓库状态 (F5)')
        refresh_btn.clicked.connect(self.refresh_repository)
        self.toolbar.addWidget(refresh_btn)
        
        # 设置按钮
        settings_btn = QPushButton('设置')
        settings_btn.setToolTip('打开完整设置')
        settings_btn.clicked.connect(self.open_settings)
        self.toolbar.addWidget(settings_btn)
    
    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 仓库列表标题
        repo_label = QLabel('仓库列表')
        repo_label.setFont(QFont('', 10, QFont.Weight.Bold))
        layout.addWidget(repo_label)
        
        # 仓库列表
        self.repo_tree = QTreeWidget()
        self.repo_tree.setHeaderLabel('仓库')
        self.repo_tree.itemClicked.connect(self.on_repo_selected)
        layout.addWidget(self.repo_tree)
        
        # 添加仓库按钮
        add_repo_btn = QPushButton('添加仓库')
        add_repo_btn.clicked.connect(self.open_repository)
        layout.addWidget(add_repo_btn)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """创建右侧主工作区"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 文件状态选项卡
        self.create_file_status_tab()
        
        # 提交历史选项卡
        self.create_commit_history_tab()
        
        # 分支管理选项卡
        self.create_branch_management_tab()
        
        return panel
    
    def create_file_status_tab(self):
        """创建文件状态选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文件状态分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # 工作区文件列表
        working_group = QGroupBox('工作区')
        working_layout = QVBoxLayout(working_group)
        self.working_files = QListWidget()
        working_layout.addWidget(self.working_files)
        splitter.addWidget(working_group)
        
        # 暂存区文件列表
        staged_group = QGroupBox('暂存区')
        staged_layout = QVBoxLayout(staged_group)
        self.staged_files = QListWidget()
        staged_layout.addWidget(self.staged_files)
        splitter.addWidget(staged_group)
        
        # 操作按钮区
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton('添加到暂存区')
        add_btn.clicked.connect(self.add_to_staging)
        button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton('从暂存区移除')
        remove_btn.clicked.connect(self.remove_from_staging)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        # 提交区域
        commit_group = QGroupBox('提交')
        commit_layout = QVBoxLayout(commit_group)
        
        # 提交消息输入框
        self.commit_message = QTextEdit()
        self.commit_message.setMaximumHeight(100)
        self.commit_message.setPlaceholderText('输入提交消息...')
        commit_layout.addWidget(self.commit_message)
        
        # 提交按钮
        commit_btn = QPushButton('提交更改')
        commit_btn.clicked.connect(self.commit_changes)
        commit_layout.addWidget(commit_btn)
        
        layout.addWidget(commit_group)
        
        self.tab_widget.addTab(tab, '文件状态')
    
    def create_commit_history_tab(self):
        """创建提交历史选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 提交历史列表
        self.commit_list = QListWidget()
        layout.addWidget(self.commit_list)
        
        self.tab_widget.addTab(tab, '提交历史')
    
    def create_branch_management_tab(self):
        """创建分支管理选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 分支列表
        self.branch_list = QListWidget()
        layout.addWidget(self.branch_list)
        
        # 分支操作按钮
        button_layout = QHBoxLayout()
        
        new_branch_btn = QPushButton('新建分支')
        new_branch_btn.clicked.connect(self.create_branch)
        button_layout.addWidget(new_branch_btn)
        
        switch_branch_btn = QPushButton('切换分支')
        switch_branch_btn.clicked.connect(self.switch_branch)
        button_layout.addWidget(switch_branch_btn)
        
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(tab, '分支管理')
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 当前分支标签
        self.branch_label = QLabel('无仓库')
        self.status_bar.addWidget(self.branch_label)
        
        # 状态标签
        self.status_label = QLabel('就绪')
        self.status_bar.addPermanentWidget(self.status_label)
    
    def load_settings(self):
        """加载设置"""
        # 窗口大小和位置
        window_size = self.config_manager.get('ui.window_size', [1200, 800])
        window_pos = self.config_manager.get('ui.window_position', [100, 100])
        
        self.resize(window_size[0], window_size[1])
        self.move(window_pos[0], window_pos[1])
        
        # 加载最近的仓库
        self.load_recent_repositories()
    
    def load_recent_repositories(self):
        """加载最近的仓库列表"""
        recent_repos = self.config_manager.get_recent_repositories()
        
        self.repo_tree.clear()
        for repo_path in recent_repos:
            item = QTreeWidgetItem([repo_path])
            self.repo_tree.addTopLevelItem(item)
    
    def check_git_environment(self):
        """检查Git环境"""
        if not is_git_installed():
            QMessageBox.warning(
                self, '警告', 
                'Git未安装或未找到。请安装Git后重新启动应用程序。'
            )
        else:
            git_version = get_git_version()
            self.status_label.setText(f'Git {git_version}')
    
    # 槽函数实现
    def new_repository(self):
        """新建仓库"""
        directory = QFileDialog.getExistingDirectory(self, '选择新仓库目录')
        if directory:
            reply = QMessageBox.question(
                self, '确认', 
                f'是否在目录 {directory} 中初始化新的Git仓库？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.git_manager.init_repository(directory):
                    self.current_repo_path = directory
                    self.config_manager.add_recent_repository(directory)
                    self.load_recent_repositories()
                    self.refresh_repository()
                    self.status_label.setText(f'已初始化新仓库: {directory}')
                    QMessageBox.information(self, '成功', '新Git仓库已成功初始化！')
                else:
                    QMessageBox.warning(self, '错误', '初始化Git仓库失败')
    
    def open_repository(self):
        """打开仓库"""
        repo_path = QFileDialog.getExistingDirectory(self, '选择Git仓库')
        if repo_path:
            # 验证是否为Git仓库
            if not self.git_manager.is_git_repository(repo_path):
                reply = QMessageBox.question(
                    self, '非Git仓库', 
                    f'目录 {repo_path} 不是Git仓库。\n是否要在此目录初始化新的Git仓库？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    if self.git_manager.init_repository(repo_path):
                        QMessageBox.information(self, '成功', '新Git仓库已初始化！')
                    else:
                        QMessageBox.warning(self, '错误', '初始化Git仓库失败')
                        return
                else:
                    return
            
            # 加载仓库
            if self.git_manager.load_repository(repo_path):
                self.current_repo_path = repo_path
                self.config_manager.add_recent_repository(repo_path)
                self.load_recent_repositories()
                self.refresh_repository()
                self.statusBar().showMessage(f'已打开仓库: {repo_path}', 5000)
            else:
                QMessageBox.warning(
                    self, '错误', 
                    f'加载Git仓库失败: {repo_path}\n\n可能的原因：\n'
                    '• 目录不存在或无权限访问\n'
                    '• .git文件夹损坏\n'
                    '• 不是有效的Git仓库'
                )
    
    def clone_repository(self):
        """克隆仓库"""
        dialog = CloneRepositoryDialog(self)
        dialog.repository_cloned.connect(self.on_repository_cloned)
        dialog.exec()
    
    def on_repository_cloned(self, repo_path: str):
        """仓库克隆完成后的处理"""
        # 添加到最近仓库列表
        self.config_manager.add_recent_repository(repo_path)
        
        # 刷新仓库列表
        self.load_recent_repositories()
        
        # 自动加载新克隆的仓库
        if self.git_manager.load_repository(repo_path):
            self.current_repo_path = repo_path
            self.refresh_repository()
            self.status_label.setText(f'已克隆并打开: {repo_path}')
    
    def refresh_repository(self):
        """刷新仓库状态"""
        if not self.git_manager.repo:
            # 当没有仓库时，清空显示
            self.branch_label.setText('分支: 未打开仓库')
            self.working_files.clear()
            self.staged_files.clear()
            self.commit_list.clear()
            self.statusBar().showMessage("请打开一个Git仓库", 5000)
            return
        
        # 更新状态信息
        status = self.git_manager.get_status()
        
        # 更新分支信息
        current_branch = status.get('current_branch', '未知')
        self.branch_label.setText(f'分支: {current_branch}')
        
        # 更新文件列表
        self.update_file_lists()
        
        # 更新提交历史
        self.update_commit_history()
        
        # 显示成功消息
        self.statusBar().showMessage("仓库状态已更新", 3000)
        
        # 更新分支列表
        self.update_branch_list()
    
    def update_file_lists(self):
        """更新文件列表"""
        if not self.git_manager.repo:
            return
        
        status = self.git_manager.get_status()
        
        # 清空列表
        self.working_files.clear()
        self.staged_files.clear()
        
        # 添加未跟踪文件
        for file_path in status.get('untracked_files', []):
            item = QListWidgetItem(f'[新文件] {file_path}')
            self.working_files.addItem(item)
        
        # 添加已修改文件
        for file_path in status.get('modified_files', []):
            item = QListWidgetItem(f'[已修改] {file_path}')
            self.working_files.addItem(item)
        
        # 添加暂存区文件
        for file_path in status.get('staged_files', []):
            item = QListWidgetItem(file_path)
            self.staged_files.addItem(item)
    
    def update_commit_history(self):
        """更新提交历史"""
        if not self.git_manager.repo:
            return
        
        commits = self.git_manager.get_commit_history()
        
        self.commit_list.clear()
        for commit in commits:
            text = f"{commit['short_hash']} - {commit['message']} ({commit['author']})"
            item = QListWidgetItem(text)
            self.commit_list.addItem(item)
    
    def update_branch_list(self):
        """更新分支列表"""
        if not self.git_manager.repo:
            return
        
        status = self.git_manager.get_status()
        current_branch = status.get('current_branch', '')
        local_branches = status.get('local_branches', [])
        
        self.branch_list.clear()
        for branch in local_branches:
            text = f"* {branch}" if branch == current_branch else f"  {branch}"
            item = QListWidgetItem(text)
            self.branch_list.addItem(item)
    
    def on_repo_selected(self, item):
        """仓库选择事件"""
        repo_path = item.text(0)
        if self.git_manager.load_repository(repo_path):
            self.current_repo_path = repo_path
            self.refresh_repository()
    
    def add_to_staging(self):
        """添加到暂存区"""
        if not self.git_manager.repo:
            QMessageBox.warning(self, '警告', '请先打开一个Git仓库')
            return
        
        # 获取选中的文件
        selected_items = self.working_files.selectedItems()
        if not selected_items:
            # 如果没有选中，提示用户
            reply = QMessageBox.question(
                self, '确认', 
                '没有选中任何文件。是否要添加所有更改到暂存区？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # 添加所有文件
                status = self.git_manager.get_status()
                all_files = status.get('untracked_files', []) + status.get('modified_files', [])
                if all_files:
                    if self.git_manager.add_files(all_files):
                        self.refresh_repository()
                        self.status_label.setText(f'已添加 {len(all_files)} 个文件到暂存区')
                    else:
                        QMessageBox.warning(self, '错误', '添加文件到暂存区失败')
                else:
                    QMessageBox.information(self, '提示', '没有文件需要添加')
            return
        
        # 解析选中的文件路径
        files_to_add = []
        for item in selected_items:
            text = item.text()
            # 移除状态前缀 [新文件] 或 [已修改]
            if '] ' in text:
                file_path = text.split('] ', 1)[1]
                files_to_add.append(file_path)
        
        if files_to_add:
            if self.git_manager.add_files(files_to_add):
                self.refresh_repository()
                self.status_label.setText(f'已添加 {len(files_to_add)} 个文件到暂存区')
            else:
                QMessageBox.warning(self, '错误', '添加文件到暂存区失败')
    
    def remove_from_staging(self):
        """从暂存区移除"""
        if not self.git_manager.repo:
            QMessageBox.warning(self, '警告', '请先打开一个Git仓库')
            return
        
        # 获取选中的文件
        selected_items = self.staged_files.selectedItems()
        if not selected_items:
            QMessageBox.information(self, '提示', '请选择要从暂存区移除的文件')
            return
        
        # 解析选中的文件路径
        files_to_remove = []
        for item in selected_items:
            files_to_remove.append(item.text())
        
        if files_to_remove:
            try:
                # 使用git reset HEAD <file> 来取消暂存
                for file_path in files_to_remove:
                    self.git_manager.repo.git.reset('HEAD', file_path)
                
                self.refresh_repository()
                self.status_label.setText(f'已从暂存区移除 {len(files_to_remove)} 个文件')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'从暂存区移除文件失败: {str(e)}')
    
    def commit_changes(self):
        """提交更改"""
        if not self.git_manager.repo:
            QMessageBox.warning(self, '警告', '请先打开一个Git仓库')
            return
        
        # 检查暂存区是否有文件
        status = self.git_manager.get_status()
        staged_files = status.get('staged_files', [])
        
        if not staged_files:
            reply = QMessageBox.question(
                self, '暂存区为空', 
                '暂存区没有文件。是否要先添加所有更改到暂存区然后提交？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 添加所有文件到暂存区
                all_files = status.get('untracked_files', []) + status.get('modified_files', [])
                if all_files:
                    if not self.git_manager.add_files(all_files):
                        QMessageBox.warning(self, '错误', '添加文件到暂存区失败')
                        return
                else:
                    QMessageBox.information(self, '提示', '没有文件需要提交')
                    return
            else:
                return
        
        # 获取提交消息
        commit_message = self.commit_message.toPlainText().strip()
        
        if not commit_message:
            QMessageBox.warning(self, '警告', '请输入提交消息')
            self.commit_message.setFocus()
            return
        
        # 获取作者信息
        author_name = self.config_manager.get('git.default_author_name', '')
        author_email = self.config_manager.get('git.default_author_email', '')
        
        # 如果没有配置作者信息，提示用户输入
        if not author_name or not author_email:
            from PyQt6.QtWidgets import QInputDialog
            
            if not author_name:
                author_name, ok = QInputDialog.getText(
                    self, '作者姓名', '请输入您的姓名:'
                )
                if not ok or not author_name.strip():
                    return
                author_name = author_name.strip()
                self.config_manager.set('git.default_author_name', author_name)
            
            if not author_email:
                author_email, ok = QInputDialog.getText(
                    self, '作者邮箱', '请输入您的邮箱:'
                )
                if not ok or not author_email.strip():
                    return
                author_email = author_email.strip()
                self.config_manager.set('git.default_author_email', author_email)
            
            # 保存配置
            self.config_manager.save_config()
        
        # 执行提交
        try:
            success = self.git_manager.commit(commit_message, author_name, author_email)
            
            if success:
                # 清空提交消息
                self.commit_message.clear()
                
                # 刷新界面
                self.refresh_repository()
                
                # 显示成功消息
                QMessageBox.information(self, '提交成功', f'提交已完成！\n\n消息: {commit_message}')
                self.status_label.setText('提交成功')
            else:
                QMessageBox.warning(self, '错误', '提交失败，请检查暂存区和提交消息')
                
        except Exception as e:
            QMessageBox.critical(self, '提交错误', f'提交过程中发生错误:\n{str(e)}')
    
    def pull_changes(self):
        """拉取更改"""
        if not self.git_manager.repo:
            QMessageBox.warning(self, '警告', '请先打开一个Git仓库')
            return
        
        try:
            # 检查是否有远程仓库
            remotes = list(self.git_manager.repo.remotes)
            if not remotes:
                QMessageBox.warning(self, '警告', '当前仓库没有配置远程仓库')
                return
            
            # 检查是否有未提交的更改
            if self.git_manager.repo.is_dirty():
                reply = QMessageBox.question(
                    self, '有未提交的更改', 
                    '工作区有未提交的更改。拉取可能会导致冲突。\n是否继续？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # 显示进度对话框
            from PyQt6.QtWidgets import QProgressDialog
            from PyQt6.QtCore import QTimer
            
            progress = QProgressDialog("正在拉取更改...", "取消", 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setAutoClose(True)
            progress.show()
            
            # 执行拉取操作
            QTimer.singleShot(100, lambda: self._do_pull(progress))
            
        except Exception as e:
            QMessageBox.critical(self, '拉取错误', f'拉取过程中发生错误:\n{str(e)}')
    
    def _do_pull(self, progress_dialog):
        """执行拉取操作"""
        try:
            success = self.git_manager.pull()
            progress_dialog.close()
            
            if success:
                self.refresh_repository()
                QMessageBox.information(self, '拉取成功', '远程更改已成功拉取！')
                self.status_label.setText('拉取成功')
            else:
                QMessageBox.warning(self, '拉取失败', '拉取失败，请检查网络连接和远程仓库设置')
                
        except Exception as e:
            progress_dialog.close()
            if "conflict" in str(e).lower():
                QMessageBox.warning(
                    self, '合并冲突', 
                    f'拉取时发生合并冲突:\n{str(e)}\n\n请解决冲突后重新提交。'
                )
            else:
                QMessageBox.critical(self, '拉取错误', f'拉取失败:\n{str(e)}')
    
    def push_changes(self):
        """推送更改"""
        if not self.git_manager.repo:
            QMessageBox.warning(self, '警告', '请先打开一个Git仓库')
            return
        
        try:
            # 检查是否有远程仓库
            remotes = list(self.git_manager.repo.remotes)
            if not remotes:
                reply = QMessageBox.question(
                    self, '没有远程仓库', 
                    '当前仓库没有配置远程仓库。\n是否要添加远程仓库？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._add_remote_repository()
                return
            
            # 检查是否有提交可以推送
            try:
                # 获取当前分支与远程分支的差异
                current_branch = self.git_manager.repo.active_branch
                remote_branch = f"origin/{current_branch.name}"
                
                # 检查是否领先于远程分支
                commits_ahead = list(self.git_manager.repo.iter_commits(f'{remote_branch}..{current_branch.name}'))
                
                if not commits_ahead:
                    QMessageBox.information(self, '无需推送', '当前分支与远程分支同步，无需推送')
                    return
                    
                # 确认推送
                reply = QMessageBox.question(
                    self, '确认推送', 
                    f'将推送 {len(commits_ahead)} 个提交到远程仓库。\n是否继续？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
                    
            except:
                # 如果无法比较（可能是首次推送），直接推送
                pass
            
            # 显示进度对话框
            from PyQt6.QtWidgets import QProgressDialog
            from PyQt6.QtCore import QTimer
            
            progress = QProgressDialog("正在推送更改...", "取消", 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setAutoClose(True)
            progress.show()
            
            # 执行推送操作
            QTimer.singleShot(100, lambda: self._do_push(progress))
            
        except Exception as e:
            QMessageBox.critical(self, '推送错误', f'推送过程中发生错误:\n{str(e)}')
    
    def _do_push(self, progress_dialog):
        """执行推送操作"""
        try:
            success = self.git_manager.push()
            progress_dialog.close()
            
            if success:
                self.refresh_repository()
                QMessageBox.information(self, '推送成功', '更改已成功推送到远程仓库！')
                self.status_label.setText('推送成功')
            else:
                QMessageBox.warning(self, '推送失败', '推送失败，请检查网络连接和权限设置')
                
        except Exception as e:
            progress_dialog.close()
            if "rejected" in str(e).lower():
                QMessageBox.warning(
                    self, '推送被拒绝', 
                    f'推送被远程仓库拒绝:\n{str(e)}\n\n可能需要先拉取远程更改。'
                )
            else:
                QMessageBox.critical(self, '推送错误', f'推送失败:\n{str(e)}')
    
    def _add_remote_repository(self):
        """添加远程仓库"""
        from PyQt6.QtWidgets import QInputDialog
        
        url, ok = QInputDialog.getText(
            self, '添加远程仓库', 
            '请输入远程仓库URL:'
        )
        
        if ok and url.strip():
            try:
                self.git_manager.repo.create_remote('origin', url.strip())
                QMessageBox.information(self, '成功', '远程仓库已添加！')
                self.refresh_repository()
            except Exception as e:
                QMessageBox.warning(self, '错误', f'添加远程仓库失败:\n{str(e)}')
    
    def manage_branches(self):
        """管理分支"""
        if not self.git_manager.repo:
            QMessageBox.warning(self, '警告', '请先打开一个Git仓库')
            return
        
        # 切换到分支管理选项卡
        self.tab_widget.setCurrentIndex(2)  # 分支管理是第3个选项卡
    
    def create_branch(self):
        """创建分支"""
        if not self.git_manager.repo:
            QMessageBox.warning(self, '警告', '请先打开一个Git仓库')
            return
        
        from PyQt6.QtWidgets import QInputDialog
        
        # 输入新分支名称
        branch_name, ok = QInputDialog.getText(
            self, '创建新分支', 
            '请输入新分支名称:'
        )
        
        if ok and branch_name.strip():
            branch_name = branch_name.strip()
            
            # 验证分支名称
            if not self._is_valid_branch_name(branch_name):
                QMessageBox.warning(
                    self, '无效分支名', 
                    '分支名称包含无效字符。\n分支名称不能包含空格、冒号、问号等特殊字符。'
                )
                return
            
            # 检查分支是否已存在
            existing_branches = [branch.name for branch in self.git_manager.repo.heads]
            if branch_name in existing_branches:
                QMessageBox.warning(self, '分支已存在', f'分支 "{branch_name}" 已存在')
                return
            
            # 询问是否切换到新分支
            reply = QMessageBox.question(
                self, '创建分支', 
                f'是否在创建分支 "{branch_name}" 后切换到该分支？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            checkout = reply == QMessageBox.StandardButton.Yes
            
            # 创建分支
            if self.git_manager.create_branch(branch_name, checkout):
                self.refresh_repository()
                if checkout:
                    QMessageBox.information(
                        self, '创建成功', 
                        f'分支 "{branch_name}" 已创建并切换成功！'
                    )
                    self.status_label.setText(f'已切换到分支: {branch_name}')
                else:
                    QMessageBox.information(
                        self, '创建成功', 
                        f'分支 "{branch_name}" 已创建成功！'
                    )
            else:
                QMessageBox.warning(self, '创建失败', f'创建分支 "{branch_name}" 失败')
    
    def switch_branch(self):
        """切换分支"""
        if not self.git_manager.repo:
            QMessageBox.warning(self, '警告', '请先打开一个Git仓库')
            return
        
        # 获取选中的分支
        selected_items = self.branch_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, '提示', '请选择要切换的分支')
            return
        
        # 解析分支名称
        branch_text = selected_items[0].text()
        branch_name = branch_text.replace('* ', '').replace('  ', '').strip()
        
        # 检查是否已经是当前分支
        current_branch = self.git_manager.repo.active_branch.name
        if branch_name == current_branch:
            QMessageBox.information(self, '提示', f'已经在分支 "{branch_name}" 上')
            return
        
        # 检查是否有未提交的更改
        if self.git_manager.repo.is_dirty():
            reply = QMessageBox.question(
                self, '有未提交的更改', 
                '工作区有未提交的更改。切换分支将丢失这些更改。\n是否继续？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # 切换分支
        if self.git_manager.checkout_branch(branch_name):
            self.refresh_repository()
            QMessageBox.information(
                self, '切换成功', 
                f'已成功切换到分支 "{branch_name}"'
            )
            self.status_label.setText(f'已切换到分支: {branch_name}')
        else:
            QMessageBox.warning(self, '切换失败', f'切换到分支 "{branch_name}" 失败')
    
    def _is_valid_branch_name(self, name: str) -> bool:
        """验证分支名称是否有效"""
        # Git分支名称规则
        invalid_chars = [' ', '~', '^', ':', '?', '*', '[', '\\']
        
        # 检查无效字符
        for char in invalid_chars:
            if char in name:
                return False
        
        # 不能以点或斜杠开头/结尾
        if name.startswith('.') or name.startswith('/') or name.endswith('.') or name.endswith('/'):
            return False
        
        # 不能包含 ".."
        if '..' in name:
            return False
        
        # 不能为空
        if not name.strip():
            return False
        
        return True
    
    def open_settings(self):
        """打开设置"""
        from .dialogs.settings_dialog import SettingsDialog
        
        try:
            dialog = SettingsDialog(self)
            dialog.settings_changed.connect(self.apply_settings)
            
            if dialog.exec() == dialog.DialogCode.Accepted:
                self.statusBar().showMessage("设置已保存", 3000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开设置对话框失败: {str(e)}")
    
    def apply_settings(self):
        """应用设置更改"""
        try:
            # 重新加载配置
            config = self.config_manager.get_all_settings()
            
            # 应用主题设置
            theme = config.get('ui_theme', 'dark')
            if hasattr(self, 'current_theme') and theme != self.current_theme:
                self.current_theme = theme
                # 这里可以添加主题切换逻辑
                self.statusBar().showMessage("主题已更新，重启应用后生效", 5000)
            else:
                self.current_theme = theme
            
            # 应用其他设置...
            self.statusBar().showMessage("设置已应用", 3000)
            
        except Exception as e:
            QMessageBox.warning(self, "警告", f"应用设置时出错: {str(e)}")
    
    def stage_selected_files(self):
        """暂存选中的文件"""
        try:
            # 获取当前选中的文件
            current_widget = self.tab_widget.currentWidget()
            
            if current_widget == self.working_tree_list:
                # 在工作区文件列表
                selected_items = self.working_tree_list.selectedItems()
                if not selected_items:
                    QMessageBox.information(self, "提示", "请先选择要暂存的文件")
                    return
                
                # 暂存选中的文件
                for item in selected_items:
                    file_path = item.text()
                    if self.git_manager.add_file(file_path):
                        self.statusBar().showMessage(f"已暂存文件: {file_path}", 2000)
                    else:
                        QMessageBox.warning(self, "警告", f"暂存文件失败: {file_path}")
                
                # 刷新文件状态
                self.refresh_file_status()
                
            else:
                QMessageBox.information(self, "提示", "请在工作区文件列表中选择文件")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"暂存文件失败: {str(e)}")
    
    def create_new_branch(self):
        """创建新分支"""
        from PyQt6.QtWidgets import QInputDialog
        
        try:
            if not self.git_manager or not self.git_manager.repo:
                QMessageBox.warning(self, "警告", "请先打开一个Git仓库")
                return
            
            branch_name, ok = QInputDialog.getText(
                self, "创建新分支", "请输入新分支名称:"
            )
            
            if ok and branch_name.strip():
                branch_name = branch_name.strip()
                
                # 验证分支名称
                if not self.is_valid_branch_name(branch_name):
                    QMessageBox.warning(self, "警告", "分支名称包含无效字符")
                    return
                
                # 创建并切换到新分支
                if self.git_manager.create_branch(branch_name):
                    if self.git_manager.checkout_branch(branch_name):
                        self.statusBar().showMessage(f"已创建并切换到分支: {branch_name}", 3000)
                        self.refresh_branches()
                    else:
                        QMessageBox.warning(self, "警告", f"创建分支成功，但切换失败: {branch_name}")
                else:
                    QMessageBox.warning(self, "警告", f"创建分支失败: {branch_name}")
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建分支失败: {str(e)}")
    
    def switch_branch(self, branch_name):
        """切换分支"""
        try:
            if not self.git_manager or not self.git_manager.repo or not branch_name:
                return
            
            # 避免重复切换到当前分支
            current_branch = self.git_manager.get_current_branch()
            if branch_name == current_branch:
                return
            
            # 切换分支
            if self.git_manager.checkout_branch(branch_name):
                self.statusBar().showMessage(f"已切换到分支: {branch_name}", 3000)
                self.refresh_file_status()
            else:
                QMessageBox.warning(self, "警告", f"切换分支失败: {branch_name}")
                # 恢复到原来的分支选择
                self.refresh_branches()
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"切换分支失败: {str(e)}")
            self.refresh_branches()
    
    def refresh_branches(self):
        """刷新分支列表"""
        try:
            if not self.git_manager or not self.git_manager.repo:
                return
            
            # 获取所有分支
            branches = self.git_manager.get_branches()
            current_branch = self.git_manager.get_current_branch()
            
            # 更新分支下拉菜单
            if hasattr(self, 'branch_combo'):
                self.branch_combo.blockSignals(True)  # 阻止信号避免递归
                self.branch_combo.clear()
                self.branch_combo.addItems(branches)
                
                # 设置当前分支
                if current_branch in branches:
                    self.branch_combo.setCurrentText(current_branch)
                
                self.branch_combo.blockSignals(False)
                
        except Exception as e:
            print(f"刷新分支列表失败: {e}")
    
    def is_valid_branch_name(self, name):
        """验证分支名称是否有效"""
        import re
        # Git分支名称规则：不能包含空格、特殊字符等
        return re.match(r'^[a-zA-Z0-9._/-]+$', name) is not None
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <h2>BakaGit</h2>
        <p><b>版本:</b> 1.0.0</p>
        <p><b>作者:</b> BakaGit 开发团队</p>
        <p><b>描述:</b> 一个简单易用的Git图形界面工具，专为初学者设计</p>
        <br>
        <p><b>主要功能:</b></p>
        <ul>
        <li>直观的Git仓库管理</li>
        <li>可视化的文件状态显示</li>
        <li>简化的提交和推送流程</li>
        <li>友好的分支管理</li>
        <li>现代化的深色主题界面</li>
        </ul>
        <br>
        <p><b>技术栈:</b> Python + PyQt6 + GitPython</p>
        <p><b>开源协议:</b> MIT License</p>
        <p>© 2025 BakaGit Team</p>
        """
        QMessageBox.about(self, '关于 BakaGit', about_text)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存窗口大小和位置
        self.config_manager.set('ui.window_size', [self.width(), self.height()])
        self.config_manager.set('ui.window_position', [self.x(), self.y()])
        self.config_manager.save_config()
        
        event.accept()
    
    # 新增的菜单功能方法
    def undo_last_action(self):
        """撤销上次操作"""
        # TODO: 实现撤销功能
        QMessageBox.information(self, "提示", "撤销功能正在开发中...")
    
    def select_all_files(self):
        """全选当前文件列表中的文件"""
        try:
            current_widget = self.tab_widget.currentWidget()
            if hasattr(current_widget, 'selectAll'):
                current_widget.selectAll()
                self.statusBar().showMessage("已选择所有文件", 2000)
            else:
                QMessageBox.information(self, "提示", "当前标签页不支持全选操作")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"全选操作失败: {str(e)}")
    
    def toggle_toolbar(self, checked):
        """切换工具栏显示/隐藏"""
        if hasattr(self, 'toolbar'):
            self.toolbar.setVisible(checked)
            self.config_manager.set('show_toolbar', checked)
            self.config_manager.save_config()
            status = "显示" if checked else "隐藏"
            self.statusBar().showMessage(f"工具栏已{status}", 2000)
    
    def toggle_statusbar(self, checked):
        """切换状态栏显示/隐藏"""
        self.statusBar().setVisible(checked)
        self.config_manager.set('show_status_bar', checked)
        self.config_manager.save_config()
        if checked:
            self.statusBar().showMessage("状态栏已显示", 2000)
    
    def open_git_config(self):
        """打开Git配置对话框"""
        from PyQt6.QtWidgets import QInputDialog
        
        try:
            # 获取当前Git配置
            config = self.git_manager.get_config()
            current_name = config.get('user.name', '')
            current_email = config.get('user.email', '')
            
            # 设置用户名
            name, ok = QInputDialog.getText(
                self, "Git配置", f"用户名 (当前: {current_name}):", 
                text=current_name
            )
            
            if ok and name.strip():
                if self.git_manager.set_config('user.name', name.strip()):
                    self.statusBar().showMessage("Git用户名已更新", 3000)
                
                # 设置邮箱
                email, ok = QInputDialog.getText(
                    self, "Git配置", f"邮箱 (当前: {current_email}):", 
                    text=current_email
                )
                
                if ok and email.strip():
                    if self.git_manager.set_config('user.email', email.strip()):
                        self.statusBar().showMessage("Git邮箱已更新", 3000)
                        QMessageBox.information(self, "成功", "Git配置已更新")
                    else:
                        QMessageBox.warning(self, "警告", "邮箱设置失败")
                else:
                    QMessageBox.warning(self, "警告", "用户名设置失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"Git配置失败: {str(e)}")
    
    def cleanup_repository(self):
        """清理当前仓库"""
        if not self.git_manager or not self.git_manager.repo:
            QMessageBox.warning(self, "警告", "请先打开一个Git仓库")
            return
        
        reply = QMessageBox.question(
            self, "确认清理", 
            "这将清理未跟踪的文件和文件夹，确定继续吗？\n注意：此操作不可撤销！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 执行清理操作
                self.git_manager.repo.git.clean('-fd')
                self.statusBar().showMessage("仓库清理完成", 3000)
                self.refresh_file_status()
                QMessageBox.information(self, "成功", "仓库清理完成")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"仓库清理失败: {str(e)}")
    
    def reset_all_settings(self):
        """重置所有设置"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置所有设置为默认值吗？\n这将清除所有自定义配置，包括主题、Git配置等。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.config_manager.reset_to_defaults()
                QMessageBox.information(self, "成功", "所有设置已重置为默认值，重启应用后生效")
                self.statusBar().showMessage("设置已重置", 3000)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"重置设置失败: {str(e)}")
    
    def show_tutorial(self):
        """显示快速教程"""
        tutorial_text = """
        <h2>🚀 BakaGit 快速入门</h2>
        
        <h3>📋 基本操作流程</h3>
        <ol>
        <li><b>打开仓库</b>：点击"打开仓库"选择项目文件夹</li>
        <li><b>查看文件</b>：在文件列表中查看修改状态</li>
        <li><b>暂存文件</b>：选择文件后点击"暂存文件"</li>
        <li><b>提交更改</b>：点击"提交"并填写提交信息</li>
        <li><b>推送到远程</b>：点击"推送"同步到远程仓库</li>
        </ol>
        
        <h3>🎨 界面说明</h3>
        <ul>
        <li><b>工具栏</b>：包含所有常用Git操作</li>
        <li><b>文件列表</b>：显示工作区和暂存区文件</li>
        <li><b>分支选择</b>：右上角下拉菜单切换分支</li>
        <li><b>状态栏</b>：显示操作结果和提示</li>
        </ul>
        
        <h3>⌨️ 快捷键</h3>
        <ul>
        <li><b>F5</b>：刷新仓库状态</li>
        <li><b>Ctrl+A</b>：全选文件</li>
        <li><b>Ctrl+Q</b>：退出应用</li>
        </ul>
        
        <h3>💡 小贴士</h3>
        <ul>
        <li>每个按钮都有工具提示，鼠标悬停查看详细说明</li>
        <li>在设置中可以配置Git用户信息和其他选项</li>
        </ul>
        """
        
        QMessageBox.about(self, "BakaGit 快速教程", tutorial_text)
