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
    QTabWidget, QGroupBox, QGridLayout, QProgressBar, QComboBox,
    QCheckBox, QDialog, QInputDialog, QPlainTextEdit, QApplication, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QAction, QIcon, QFont, QPixmap, QTextCharFormat, QColor, QSyntaxHighlighter, QTextDocument

from ..core.git_manager import GitManager
from ..core.config import ConfigManager
from ..core.utils import is_git_installed, get_git_version
from .dialogs.clone_dialog import CloneRepositoryDialog
from .dialogs.git_config_dialog import GitConfigDialog
from .dialogs.init_repository_dialog import InitRepositoryDialog


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
    
    def create_menu_bar(self):
        """创建菜单栏"""
        self.menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = self.menu_bar.addMenu('文件(&F)')
        
        # 打开仓库
        open_action = QAction('打开仓库(&O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('打开一个Git仓库')
        open_action.triggered.connect(self.open_repository)
        file_menu.addAction(open_action)
        
        # 克隆仓库
        clone_action = QAction('克隆仓库(&C)', self)
        clone_action.setShortcut('Ctrl+Shift+C')
        clone_action.setStatusTip('克隆一个远程仓库')
        clone_action.triggered.connect(self.clone_repository)
        file_menu.addAction(clone_action)
        
        file_menu.addSeparator()
        
        # 刷新
        refresh_action = QAction('刷新(&R)', self)
        refresh_action.setShortcut('F5')
        refresh_action.setStatusTip('刷新仓库状态')
        refresh_action.triggered.connect(self.refresh_repository)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('退出应用程序')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = self.menu_bar.addMenu('编辑(&E)')
        
        # 暂存所有文件
        stage_all_action = QAction('暂存所有文件(&A)', self)
        stage_all_action.setShortcut('Ctrl+A')
        stage_all_action.setStatusTip('暂存所有修改的文件')
        stage_all_action.triggered.connect(self.stage_all_files)
        edit_menu.addAction(stage_all_action)
        
        # 取消暂存所有文件
        unstage_all_action = QAction('取消暂存所有文件(&U)', self)
        unstage_all_action.setShortcut('Ctrl+Shift+A')
        unstage_all_action.setStatusTip('取消暂存所有文件')
        unstage_all_action.triggered.connect(self.unstage_all_files)
        edit_menu.addAction(unstage_all_action)
        
        edit_menu.addSeparator()
        
        # 提交
        commit_action = QAction('提交(&M)', self)
        commit_action.setShortcut('Ctrl+M')
        commit_action.setStatusTip('提交暂存的更改')
        commit_action.triggered.connect(self.show_commit_tab)
        edit_menu.addAction(commit_action)
        
        # 视图菜单
        view_menu = self.menu_bar.addMenu('视图(&V)')
        
        # 切换标签页
        files_tab_action = QAction('文件状态(&F)', self)
        files_tab_action.setShortcut('Ctrl+1')
        files_tab_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(files_tab_action)
        
        commit_tab_action = QAction('增强提交(&C)', self)
        commit_tab_action.setShortcut('Ctrl+2')
        commit_tab_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(commit_tab_action)
        
        history_tab_action = QAction('提交历史(&H)', self)
        history_tab_action.setShortcut('Ctrl+3')
        history_tab_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction(history_tab_action)
        
        branch_tab_action = QAction('分支管理(&B)', self)
        branch_tab_action.setShortcut('Ctrl+4')
        branch_tab_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        view_menu.addAction(branch_tab_action)
        
        remote_tab_action = QAction('远程操作(&R)', self)
        remote_tab_action.setShortcut('Ctrl+5')
        remote_tab_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        view_menu.addAction(remote_tab_action)
        
        tags_tab_action = QAction('标签管理(&T)', self)
        tags_tab_action.setShortcut('Ctrl+6')
        tags_tab_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(5))
        view_menu.addAction(tags_tab_action)
        
        # Git菜单
        git_menu = self.menu_bar.addMenu('Git(&G)')
        
        # 推送
        push_action = QAction('推送(&P)', self)
        push_action.setShortcut('Ctrl+P')
        push_action.setStatusTip('推送到远程仓库')
        push_action.triggered.connect(self.quick_push)
        git_menu.addAction(push_action)
        
        # 拉取
        pull_action = QAction('拉取(&L)', self)
        pull_action.setShortcut('Ctrl+L')
        pull_action.setStatusTip('从远程仓库拉取')
        pull_action.triggered.connect(self.quick_pull)
        git_menu.addAction(pull_action)
        
        # 获取
        fetch_action = QAction('获取(&F)', self)
        fetch_action.setShortcut('Ctrl+F')
        fetch_action.setStatusTip('从远程仓库获取')
        fetch_action.triggered.connect(self.quick_fetch)
        git_menu.addAction(fetch_action)
        
        git_menu.addSeparator()
        
        # 创建分支
        create_branch_action = QAction('创建分支(&B)', self)
        create_branch_action.setShortcut('Ctrl+B')
        create_branch_action.setStatusTip('创建新分支')
        create_branch_action.triggered.connect(self.create_new_branch)
        git_menu.addAction(create_branch_action)
        
        # 创建标签
        create_tag_action = QAction('创建标签(&T)', self)
        create_tag_action.setShortcut('Ctrl+T')
        create_tag_action.setStatusTip('创建新标签')
        create_tag_action.triggered.connect(self.create_tag)
        git_menu.addAction(create_tag_action)
        
        # 工具菜单
        tools_menu = self.menu_bar.addMenu('工具(&T)')
        
        # Git配置
        git_config_action = QAction('Git配置...(&C)', self)
        git_config_action.setStatusTip('配置Git用户信息和设置')
        git_config_action.triggered.connect(self.open_git_config)
        tools_menu.addAction(git_config_action)
        
        # 初始化仓库
        init_repo_action = QAction('初始化仓库...(&I)', self)
        init_repo_action.setShortcut('Ctrl+Shift+N')
        init_repo_action.setStatusTip('在指定目录初始化新的Git仓库')
        init_repo_action.triggered.connect(self.init_repository)
        tools_menu.addAction(init_repo_action)
        
        # 设置远程仓库
        setup_remote_action = QAction('设置远程仓库...(&R)', self)
        setup_remote_action.setStatusTip('设置GitHub等远程仓库地址')
        setup_remote_action.triggered.connect(self.setup_remote_repository)
        tools_menu.addAction(setup_remote_action)
        
        tools_menu.addSeparator()
        
        # 清理仓库
        cleanup_action = QAction('清理仓库(&L)', self)
        cleanup_action.setStatusTip('清理未跟踪的文件和文件夹')
        cleanup_action.triggered.connect(self.cleanup_repository)
        tools_menu.addAction(cleanup_action)
        
        # 设置菜单
        settings_menu = self.menu_bar.addMenu('设置(&S)')
        
        # 偏好设置
        settings_action = QAction('偏好设置(&P)', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.setStatusTip('打开设置对话框')
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = self.menu_bar.addMenu('帮助(&H)')
        
        # 键盘快捷键
        shortcuts_action = QAction('键盘快捷键(&K)', self)
        shortcuts_action.setShortcut('F1')
        shortcuts_action.setStatusTip('查看键盘快捷键')
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        # 关于
        about_action = QAction('关于(&A)', self)
        about_action.setStatusTip('关于BakaGit')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_commit_tab(self):
        """显示提交标签页"""
        if hasattr(self, 'tab_widget'):
            self.tab_widget.setCurrentIndex(1)  # 增强提交标签页
    
    def quick_push(self):
        """快速推送"""
        if hasattr(self, 'push_to_remote'):
            self.push_to_remote()
        else:
            QMessageBox.information(self, '提示', '请先打开远程操作标签页进行推送')
    
    def quick_pull(self):
        """快速拉取"""
        if hasattr(self, 'pull_from_remote'):
            self.pull_from_remote()
        else:
            QMessageBox.information(self, '提示', '请先打开远程操作标签页进行拉取')
    
    def quick_fetch(self):
        """快速获取"""
        if hasattr(self, 'fetch_from_remote'):
            self.fetch_from_remote()
        else:
            QMessageBox.information(self, '提示', '请先打开远程操作标签页进行获取')
    
    def create_new_branch(self):
        """创建新分支"""
        branch_name, ok = QInputDialog.getText(self, '创建分支', '分支名称:')
        if ok and branch_name.strip():
            try:
                if self.git_manager.create_branch(branch_name.strip()):
                    self.refresh_repository()
                    self.statusBar().showMessage(f'已创建分支: {branch_name}', 3000)
                else:
                    QMessageBox.warning(self, '创建失败', f'创建分支 "{branch_name}" 失败')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'创建分支时出错: {str(e)}')
    
    def show_shortcuts(self):
        """显示键盘快捷键"""
        shortcuts_text = """
键盘快捷键:

文件操作:
  Ctrl+O    打开仓库
  Ctrl+Shift+C    克隆仓库
  F5        刷新仓库状态
  Ctrl+Q    退出应用

编辑操作:
  Ctrl+A    暂存所有文件
  Ctrl+Shift+A    取消暂存所有文件
  Ctrl+M    显示提交界面

视图切换:
  Ctrl+1    文件状态
  Ctrl+2    增强提交
  Ctrl+3    提交历史
  Ctrl+4    分支管理
  Ctrl+5    远程操作
  Ctrl+6    标签管理

Git操作:
  Ctrl+P    推送
  Ctrl+L    拉取
  Ctrl+F    获取
  Ctrl+B    创建分支
  Ctrl+T    创建标签

其他:
  Ctrl+,    偏好设置
  F1        显示此帮助
        """
        QMessageBox.information(self, '键盘快捷键', shortcuts_text)
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
<h2>BakaGit - 笨蛋都会用的Git图形化工具</h2>
<p><b>版本:</b> 0.1.0</p>
<p><b>作者:</b> BakaGit Team</p>
<p><b>描述:</b> 一个简单易用的Git图形化管理工具</p>

<h3>主要功能:</h3>
<ul>
<li>文件状态管理和差异查看</li>
<li>增强的提交界面</li>
<li>完整的分支管理</li>
<li>远程仓库操作</li>
<li>标签管理</li>
<li>友好的用户界面</li>
</ul>

<p><b>技术栈:</b> Python 3.13, PyQt6, GitPython</p>
<p><b>开源协议:</b> MIT License</p>
        """
        QMessageBox.about(self, '关于 BakaGit', about_text)

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
        
        # 增强提交选项卡
        enhanced_commit_tab = self.create_enhanced_commit_tab()
        self.tab_widget.addTab(enhanced_commit_tab, '💾 增强提交')
        
        # 提交历史选项卡
        self.create_commit_history_tab()
        
        # 分支管理选项卡
        self.create_branch_management_tab()
        
        # 远程操作选项卡
        remote_tab = self.create_remote_operations_tab()
        self.tab_widget.addTab(remote_tab, '🌐 远程操作')
        
        # 标签管理选项卡
        tags_tab = self.create_tags_management_tab()
        self.tab_widget.addTab(tags_tab, '🏷️ 标签管理')
        
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
        self.working_files.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.working_files.customContextMenuRequested.connect(self.show_working_files_context_menu)
        self.working_files.itemDoubleClicked.connect(self.view_file_diff)
        working_layout.addWidget(self.working_files)
        splitter.addWidget(working_group)
        
        # 暂存区文件列表
        staged_group = QGroupBox('暂存区')
        staged_layout = QVBoxLayout(staged_group)
        self.staged_files = QListWidget()
        self.staged_files.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.staged_files.customContextMenuRequested.connect(self.show_staged_files_context_menu)
        self.staged_files.itemDoubleClicked.connect(self.view_file_diff)
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
    
    def create_enhanced_commit_tab(self):
        """创建增强的提交标签页"""
        commit_tab = QWidget()
        layout = QVBoxLayout(commit_tab)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧：文件列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 工作区文件组
        working_group = QGroupBox("工作区文件")
        working_layout = QVBoxLayout(working_group)
        
        # 工作区工具栏
        working_toolbar = QHBoxLayout()
        self.stage_all_btn = QPushButton("📁 全部暂存")
        self.stage_all_btn.clicked.connect(self.stage_all_files)
        working_toolbar.addWidget(self.stage_all_btn)
        working_toolbar.addStretch()
        working_layout.addLayout(working_toolbar)
        
        self.working_files_enhanced = QListWidget()
        self.working_files_enhanced.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.working_files_enhanced.customContextMenuRequested.connect(self.show_working_files_context_menu)
        self.working_files_enhanced.itemDoubleClicked.connect(self.view_file_diff)
        working_layout.addWidget(self.working_files_enhanced)
        
        left_layout.addWidget(working_group)
        
        # 暂存区文件组
        staged_group = QGroupBox("暂存区文件")
        staged_layout = QVBoxLayout(staged_group)
        
        # 暂存区工具栏
        staged_toolbar = QHBoxLayout()
        self.unstage_all_btn = QPushButton("📤 全部取消暂存")
        self.unstage_all_btn.clicked.connect(self.unstage_all_files)
        staged_toolbar.addWidget(self.unstage_all_btn)
        staged_toolbar.addStretch()
        staged_layout.addLayout(staged_toolbar)
        
        self.staged_files_enhanced = QListWidget()
        self.staged_files_enhanced.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.staged_files_enhanced.customContextMenuRequested.connect(self.show_staged_files_context_menu)
        self.staged_files_enhanced.itemDoubleClicked.connect(self.view_file_diff)
        staged_layout.addWidget(self.staged_files_enhanced)
        
        left_layout.addWidget(staged_group)
        
        splitter.addWidget(left_widget)
        
        # 右侧：提交面板
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 提交信息组
        commit_group = QGroupBox("提交信息")
        commit_layout = QVBoxLayout(commit_group)
        
        # 提交消息输入
        commit_label = QLabel("提交消息:")
        commit_layout.addWidget(commit_label)
        
        self.commit_message_enhanced = QTextEdit()
        self.commit_message_enhanced.setMaximumHeight(100)
        self.commit_message_enhanced.setPlaceholderText("输入提交消息...")
        commit_layout.addWidget(self.commit_message_enhanced)
        
        # 提交选项
        options_layout = QHBoxLayout()
        
        # 修正提交复选框
        self.amend_commit = QCheckBox("修正上一次提交")
        options_layout.addWidget(self.amend_commit)
        
        options_layout.addStretch()
        commit_layout.addLayout(options_layout)
        
        # 提交按钮
        commit_btn_layout = QHBoxLayout()
        commit_btn_layout.addStretch()
        
        self.commit_btn_enhanced = QPushButton("💾 提交")
        self.commit_btn_enhanced.setMinimumHeight(40)
        self.commit_btn_enhanced.clicked.connect(self.commit_changes_enhanced)
        commit_btn_layout.addWidget(self.commit_btn_enhanced)
        
        commit_layout.addLayout(commit_btn_layout)
        
        right_layout.addWidget(commit_group)
        
        # 最近提交组
        recent_group = QGroupBox("最近提交")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_commits_enhanced = QListWidget()
        self.recent_commits_enhanced.setMaximumHeight(200)
        self.recent_commits_enhanced.itemDoubleClicked.connect(self.view_commit_details)
        recent_layout.addWidget(self.recent_commits_enhanced)
        
        right_layout.addWidget(recent_group)
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 300])
        
        return commit_tab
    
    def stage_all_files(self):
        """暂存所有文件"""
        try:
            if self.git_manager.stage_all():
                self.refresh_repository()
                self.statusBar().showMessage('已暂存所有文件', 3000)
            else:
                QMessageBox.warning(self, '操作失败', '暂存所有文件失败')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'暂存文件时出错: {str(e)}')
    
    def unstage_all_files(self):
        """取消暂存所有文件"""
        try:
            self.git_manager.repo.index.reset()
            self.refresh_repository()
            self.statusBar().showMessage('已取消暂存所有文件', 3000)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'取消暂存时出错: {str(e)}')
    
    def commit_changes_enhanced(self):
        """提交更改（增强版）"""
        commit_msg = self.commit_message_enhanced.toPlainText().strip()
        if not commit_msg:
            QMessageBox.warning(self, '提交失败', '请输入提交消息')
            return
        
        try:
            # 检查是否有暂存的文件
            if not list(self.git_manager.repo.index.diff("HEAD")):
                if not self.amend_commit.isChecked():
                    QMessageBox.warning(self, '提交失败', '没有暂存的文件可提交')
                    return
            
            # 执行提交
            if self.amend_commit.isChecked():
                # 修正提交
                self.git_manager.repo.git.commit('--amend', '-m', commit_msg)
            else:
                # 普通提交
                if self.git_manager.commit(commit_msg):
                    self.commit_message_enhanced.clear()
                    self.refresh_repository()
                    self.statusBar().showMessage('提交成功', 3000)
                else:
                    QMessageBox.warning(self, '提交失败', '提交操作失败')
                    return
            
            self.refresh_repository()
            self.statusBar().showMessage('提交成功', 3000)
            
        except Exception as e:
            QMessageBox.critical(self, '提交失败', f'提交时出错: {str(e)}')
    
    def view_commit_details(self, item):
        """查看提交详情"""
        commit_hash = item.data(Qt.ItemDataRole.UserRole)
        if not commit_hash:
            return
        
        try:
            commit = self.git_manager.repo.commit(commit_hash)
            
            # 获取提交差异
            if commit.parents:
                diff = self.git_manager.repo.git.diff(commit.parents[0], commit)
            else:
                diff = self.git_manager.repo.git.show(commit_hash)
            
            title = f'提交详情: {commit_hash[:8]} - {commit.summary}'
            self.show_diff_dialog(title, diff)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查看提交详情时出错: {str(e)}')

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
        self.branch_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.branch_list.customContextMenuRequested.connect(self.show_branch_context_menu)
        self.branch_list.itemDoubleClicked.connect(self.switch_to_branch_by_item)
        layout.addWidget(self.branch_list)
        
        # 分支操作按钮
        button_layout = QHBoxLayout()
        
        new_branch_btn = QPushButton('新建分支')
        new_branch_btn.clicked.connect(self.create_branch)
        button_layout.addWidget(new_branch_btn)
        
        switch_branch_btn = QPushButton('切换分支')
        switch_branch_btn.clicked.connect(self.switch_branch)
        button_layout.addWidget(switch_branch_btn)
        
        delete_branch_btn = QPushButton('删除分支')
        delete_branch_btn.clicked.connect(self.delete_branch)
        button_layout.addWidget(delete_branch_btn)
        
        merge_branch_btn = QPushButton('合并分支')
        merge_branch_btn.clicked.connect(self.merge_branch)
        button_layout.addWidget(merge_branch_btn)
        
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(tab, '分支管理')
    
    def create_remote_operations_tab(self):
        """创建远程操作标签页"""
        remote_tab = QWidget()
        layout = QVBoxLayout(remote_tab)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧：远程仓库列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 远程仓库组
        remotes_group = QGroupBox("远程仓库")
        remotes_layout = QVBoxLayout(remotes_group)
        
        # 远程仓库工具栏
        remotes_toolbar = QHBoxLayout()
        self.add_remote_btn = QPushButton("➕ 添加远程")
        self.add_remote_btn.clicked.connect(self.add_remote_repository)
        remotes_toolbar.addWidget(self.add_remote_btn)
        
        self.remove_remote_btn = QPushButton("❌ 删除远程")
        self.remove_remote_btn.clicked.connect(self.remove_remote_repository)
        remotes_toolbar.addWidget(self.remove_remote_btn)
        
        remotes_toolbar.addStretch()
        remotes_layout.addLayout(remotes_toolbar)
        
        # 远程仓库列表
        self.remotes_list = QListWidget()
        self.remotes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.remotes_list.customContextMenuRequested.connect(self.show_remote_context_menu)
        remotes_layout.addWidget(self.remotes_list)
        
        left_layout.addWidget(remotes_group)
        
        # 远程分支组
        remote_branches_group = QGroupBox("远程分支")
        remote_branches_layout = QVBoxLayout(remote_branches_group)
        
        self.remote_branches_list = QListWidget()
        remote_branches_layout.addWidget(self.remote_branches_list)
        
        left_layout.addWidget(remote_branches_group)
        
        splitter.addWidget(left_widget)
        
        # 右侧：操作面板
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 推送组
        push_group = QGroupBox("推送")
        push_layout = QVBoxLayout(push_group)
        
        # 推送选项
        push_options_layout = QHBoxLayout()
        
        self.push_remote_combo = QComboBox()
        push_options_layout.addWidget(QLabel("远程:"))
        push_options_layout.addWidget(self.push_remote_combo)
        
        self.push_branch_combo = QComboBox()
        push_options_layout.addWidget(QLabel("分支:"))
        push_options_layout.addWidget(self.push_branch_combo)
        
        push_layout.addLayout(push_options_layout)
        
        # 推送按钮
        push_btn_layout = QHBoxLayout()
        push_btn_layout.addStretch()
        
        self.push_btn = QPushButton("📤 推送")
        self.push_btn.setMinimumHeight(40)
        self.push_btn.clicked.connect(self.push_to_remote)
        push_btn_layout.addWidget(self.push_btn)
        
        push_layout.addLayout(push_btn_layout)
        
        right_layout.addWidget(push_group)
        
        # 拉取组
        pull_group = QGroupBox("拉取")
        pull_layout = QVBoxLayout(pull_group)
        
        # 拉取选项
        pull_options_layout = QHBoxLayout()
        
        self.pull_remote_combo = QComboBox()
        pull_options_layout.addWidget(QLabel("远程:"))
        pull_options_layout.addWidget(self.pull_remote_combo)
        
        self.pull_branch_combo = QComboBox()
        pull_options_layout.addWidget(QLabel("分支:"))
        pull_options_layout.addWidget(self.pull_branch_combo)
        
        pull_layout.addLayout(pull_options_layout)
        
        # 拉取按钮
        pull_btn_layout = QHBoxLayout()
        
        self.fetch_btn = QPushButton("📥 获取")
        self.fetch_btn.clicked.connect(self.fetch_from_remote)
        pull_btn_layout.addWidget(self.fetch_btn)
        
        self.pull_btn = QPushButton("⬇️ 拉取")
        self.pull_btn.setMinimumHeight(40)
        self.pull_btn.clicked.connect(self.pull_from_remote)
        pull_btn_layout.addWidget(self.pull_btn)
        
        pull_layout.addLayout(pull_btn_layout)
        
        right_layout.addWidget(pull_group)
        
        # 进度条
        self.remote_progress = QProgressBar()
        self.remote_progress.setVisible(False)
        right_layout.addWidget(self.remote_progress)
        
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 300])
        
        return remote_tab
    
    def create_tags_management_tab(self):
        """创建标签管理标签页"""
        tags_tab = QWidget()
        layout = QVBoxLayout(tags_tab)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧：标签列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 标签列表组
        tags_group = QGroupBox("标签列表")
        tags_layout = QVBoxLayout(tags_group)
        
        # 标签工具栏
        tags_toolbar = QHBoxLayout()
        self.create_tag_btn = QPushButton("➕ 创建标签")
        self.create_tag_btn.clicked.connect(self.create_tag)
        tags_toolbar.addWidget(self.create_tag_btn)
        
        self.delete_tag_btn = QPushButton("❌ 删除标签")
        self.delete_tag_btn.clicked.connect(self.delete_tag)
        tags_toolbar.addWidget(self.delete_tag_btn)
        
        tags_toolbar.addStretch()
        tags_layout.addLayout(tags_toolbar)
        
        # 标签列表
        self.tags_list = QListWidget()
        self.tags_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tags_list.customContextMenuRequested.connect(self.show_tag_context_menu)
        self.tags_list.itemDoubleClicked.connect(self.view_tag_details)
        tags_layout.addWidget(self.tags_list)
        
        left_layout.addWidget(tags_group)
        
        splitter.addWidget(left_widget)
        
        # 右侧：标签操作面板
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 创建标签组
        create_group = QGroupBox("创建新标签")
        create_layout = QVBoxLayout(create_group)
        
        # 标签名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("标签名称:"))
        self.tag_name_input = QLineEdit()
        self.tag_name_input.setPlaceholderText("例如: v1.0.0")
        name_layout.addWidget(self.tag_name_input)
        create_layout.addLayout(name_layout)
        
        # 标签消息
        msg_layout = QVBoxLayout()
        msg_layout.addWidget(QLabel("标签消息 (可选):"))
        self.tag_message_input = QTextEdit()
        self.tag_message_input.setMaximumHeight(80)
        self.tag_message_input.setPlaceholderText("输入标签描述...")
        msg_layout.addWidget(self.tag_message_input)
        create_layout.addLayout(msg_layout)
        
        # 目标提交
        commit_layout = QHBoxLayout()
        commit_layout.addWidget(QLabel("目标提交:"))
        self.tag_commit_combo = QComboBox()
        self.tag_commit_combo.setEditable(True)
        commit_layout.addWidget(self.tag_commit_combo)
        create_layout.addLayout(commit_layout)
        
        # 创建按钮
        create_btn_layout = QHBoxLayout()
        create_btn_layout.addStretch()
        
        self.create_tag_main_btn = QPushButton("🏷️ 创建标签")
        self.create_tag_main_btn.setMinimumHeight(40)
        self.create_tag_main_btn.clicked.connect(self.create_tag_from_input)
        create_btn_layout.addWidget(self.create_tag_main_btn)
        
        create_layout.addLayout(create_btn_layout)
        
        right_layout.addWidget(create_group)
        
        # 标签操作组
        operations_group = QGroupBox("标签操作")
        operations_layout = QVBoxLayout(operations_group)
        
        # 推送操作
        push_layout = QHBoxLayout()
        
        self.push_tag_btn = QPushButton("📤 推送选中标签")
        self.push_tag_btn.clicked.connect(self.push_selected_tag)
        push_layout.addWidget(self.push_tag_btn)
        
        self.push_all_tags_btn = QPushButton("📤 推送所有标签")
        self.push_all_tags_btn.clicked.connect(self.push_all_tags)
        push_layout.addWidget(self.push_all_tags_btn)
        
        operations_layout.addLayout(push_layout)
        
        # 远程选择
        remote_layout = QHBoxLayout()
        remote_layout.addWidget(QLabel("目标远程:"))
        self.tag_remote_combo = QComboBox()
        remote_layout.addWidget(self.tag_remote_combo)
        operations_layout.addLayout(remote_layout)
        
        right_layout.addWidget(operations_group)
        
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 300])
        
        return tags_tab

    def create_status_bar(self):
        """创建增强的状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 当前分支标签
        self.branch_label = QLabel('无仓库')
        self.branch_label.setStyleSheet("QLabel { padding: 2px 8px; background-color: #2d2d2d; color: #0078d4; border: 1px solid #404040; border-radius: 3px; }")
        self.status_bar.addWidget(self.branch_label)
        
        # 添加分隔符
        separator1 = QLabel('|')
        separator1.setStyleSheet("color: gray;")
        self.status_bar.addWidget(separator1)
        
        # 文件状态标签
        self.file_status_label = QLabel('文件: 0 修改, 0 暂存')
        self.file_status_label.setStyleSheet("QLabel { padding: 2px 8px; }")
        self.status_bar.addWidget(self.file_status_label)
        
        # 添加分隔符
        separator2 = QLabel('|')
        separator2.setStyleSheet("color: gray;")
        self.status_bar.addWidget(separator2)
        
        # 远程状态标签
        self.remote_status_label = QLabel('远程: 未连接')
        self.remote_status_label.setStyleSheet("QLabel { padding: 2px 8px; }")
        self.status_bar.addWidget(self.remote_status_label)
        
        # 添加弹性空间
        self.status_bar.addPermanentWidget(QLabel())
        
        # 添加进度条（隐藏状态）
        self.main_progress = QProgressBar()
        self.main_progress.setVisible(False)
        self.main_progress.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.main_progress)
        
        # Git状态图标
        self.git_status_label = QLabel('📦 Git')
        self.git_status_label.setStyleSheet("QLabel { padding: 2px 8px; background-color: #2d2d2d; color: #4caf50; border: 1px solid #404040; border-radius: 3px; }")
        self.status_bar.addPermanentWidget(self.git_status_label)
        
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
    
    def update_status_bar(self):
        """更新状态栏信息"""
        if not self.git_manager.repo:
            self.branch_label.setText('无仓库')
            self.file_status_label.setText('文件: 0 修改, 0 暂存')
            self.remote_status_label.setText('远程: 未连接')
            self.git_status_label.setText('📦 无仓库')
            return
        
        try:
            status = self.git_manager.get_status()
            
            # 更新分支信息
            current_branch = status.get('current_branch', '未知')
            self.branch_label.setText(f'🌿 分支: {current_branch}')
            
            # 更新文件状态
            modified_count = len(status.get('modified', []))
            staged_count = len(status.get('staged', []))
            self.file_status_label.setText(f'📁 文件: {modified_count} 修改, {staged_count} 暂存')
            
            # 更新远程状态
            remotes = self.git_manager.get_remotes()
            if remotes:
                self.remote_status_label.setText(f'🌐 远程: {len(remotes)} 个')
                self.remote_status_label.setStyleSheet("QLabel { padding: 2px 8px; color: green; }")
            else:
                self.remote_status_label.setText('🌐 远程: 无')
                self.remote_status_label.setStyleSheet("QLabel { padding: 2px 8px; color: orange; }")
            
            # 更新Git状态
            if modified_count > 0 or staged_count > 0:
                self.git_status_label.setText('📝 有更改')
                self.git_status_label.setStyleSheet("QLabel { padding: 2px 8px; background-color: #fff3e0; border-radius: 3px; }")
            else:
                self.git_status_label.setText('✅ 干净')
                self.git_status_label.setStyleSheet("QLabel { padding: 2px 8px; background-color: #f1f8e9; border-radius: 3px; }")
                
        except Exception as e:
            print(f"更新状态栏时出错: {e}")
            self.git_status_label.setText('❌ 错误')
            self.git_status_label.setStyleSheet("QLabel { padding: 2px 8px; background-color: #ffebee; border-radius: 3px; }")

    def show_loading(self, message="加载中..."):
        """显示加载进度"""
        self.main_progress.setVisible(True)
        self.main_progress.setRange(0, 0)  # 不确定进度
        self.statusBar().showMessage(message)
    
    def hide_loading(self):
        """隐藏加载进度"""
        self.main_progress.setVisible(False)
        self.statusBar().clearMessage()

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
            # 只有在status_label存在时才设置文本
            if hasattr(self, 'status_label'):
                self.status_label.setText(f'Git {git_version}')
    
    # 槽函数实现
    def init_repository(self):
        """初始化仓库"""
        dialog = InitRepositoryDialog(self)
        dialog.set_git_manager(self.git_manager)
        dialog.repository_initialized.connect(self.on_repository_initialized)
        dialog.exec()
    
    def on_repository_initialized(self, repo_path: str):
        """仓库初始化完成后的处理"""
        self.current_repo_path = repo_path
        self.config_manager.add_recent_repository(repo_path)
        self.load_recent_repositories()
        self.refresh_repository()
        self.statusBar().showMessage(f'已初始化新仓库: {repo_path}', 5000)
    
    def open_git_config(self):
        """打开Git配置对话框"""
        dialog = GitConfigDialog(self.git_manager, self)
        dialog.config_saved.connect(self.on_git_config_saved)
        dialog.exec()
    
    def on_git_config_saved(self):
        """Git配置保存后的处理"""
        self.statusBar().showMessage('Git配置已保存', 3000)
        # 刷新状态栏显示
        self.update_status_bar()
    
    def new_repository(self):
        """新建仓库（保持向后兼容）"""
        # 调用新的初始化仓库方法
        self.init_repository()
    
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
            
            # 清空增强提交界面
            if hasattr(self, 'working_files_enhanced'):
                self.working_files_enhanced.clear()
            if hasattr(self, 'staged_files_enhanced'):
                self.staged_files_enhanced.clear()
            if hasattr(self, 'recent_commits_enhanced'):
                self.recent_commits_enhanced.clear()
            
            self.statusBar().showMessage("请打开一个Git仓库", 5000)
            return
        
        # 更新状态信息
        status = self.git_manager.get_status()
        
        # 更新分支信息
        current_branch = status.get('current_branch', '未知')
        self.branch_label.setText(f'分支: {current_branch}')
        
        # 更新文件列表
        self.update_file_lists()
        
        # 更新增强文件列表
        self.update_enhanced_file_lists()
        
        # 更新提交历史
        self.update_commit_history()
        
        # 更新增强提交历史
        self.update_enhanced_commit_history()
        
        # 显示成功消息
        self.statusBar().showMessage("仓库状态已更新", 3000)
        
        # 更新分支列表
        self.update_branch_list()
        
        # 更新远程仓库信息
        self.refresh_remote_info()
        
        # 更新标签信息
        self.refresh_tags_info()
        
        # 更新状态栏
        self.update_status_bar()
    
    def refresh_remote_info(self):
        """刷新远程仓库信息"""
        if not hasattr(self, 'remotes_list'):
            return
            
        if not self.git_manager.repo:
            self.remotes_list.clear()
            if hasattr(self, 'remote_branches_list'):
                self.remote_branches_list.clear()
            if hasattr(self, 'push_remote_combo'):
                self.push_remote_combo.clear()
                self.pull_remote_combo.clear()
                self.push_branch_combo.clear()
                self.pull_branch_combo.clear()
            return
        
        try:
            # 更新远程仓库列表
            remotes = self.git_manager.get_remotes()
            self.remotes_list.clear()
            if hasattr(self, 'push_remote_combo'):
                self.push_remote_combo.clear()
                self.pull_remote_combo.clear()
            
            for remote in remotes:
                self.remotes_list.addItem(remote)
                if hasattr(self, 'push_remote_combo'):
                    self.push_remote_combo.addItem(remote)
                    self.pull_remote_combo.addItem(remote)
            
            # 更新分支列表
            if hasattr(self, 'push_branch_combo'):
                branches = self.git_manager.get_branches()
                self.push_branch_combo.clear()
                self.pull_branch_combo.clear()
                
                # 添加当前分支到第一位
                if self.git_manager.repo.active_branch:
                    current_branch = self.git_manager.repo.active_branch.name
                    self.push_branch_combo.addItem(current_branch)
                    self.pull_branch_combo.addItem(current_branch)
                
                for branch in branches:
                    if branch != (self.git_manager.repo.active_branch.name if self.git_manager.repo.active_branch else ""):
                        self.push_branch_combo.addItem(branch)
                        self.pull_branch_combo.addItem(branch)
            
            # 更新远程分支列表
            if hasattr(self, 'remote_branches_list'):
                self.remote_branches_list.clear()
                for remote in self.git_manager.repo.remotes:
                    for ref in remote.refs:
                        if 'HEAD' not in ref.name:
                            self.remote_branches_list.addItem(ref.name)
                            
        except Exception as e:
            print(f"刷新远程信息时出错: {e}")
    
    def refresh_tags_info(self):
        """刷新标签信息"""
        if not hasattr(self, 'tags_list'):
            return
            
        if not self.git_manager.repo:
            self.tags_list.clear()
            if hasattr(self, 'tag_commit_combo'):
                self.tag_commit_combo.clear()
                self.tag_remote_combo.clear()
            return
        
        try:
            # 更新标签列表
            tags = self.git_manager.get_tags()
            self.tags_list.clear()
            
            for tag in tags:
                item = QListWidgetItem(tag)
                item.setData(Qt.ItemDataRole.UserRole, tag)
                self.tags_list.addItem(item)
            
            # 更新提交列表
            if hasattr(self, 'tag_commit_combo'):
                self.tag_commit_combo.clear()
                self.tag_commit_combo.addItem("HEAD (当前提交)")
                
                # 添加最近的提交
                commits = self.git_manager.get_commit_history(max_count=20)
                for commit_info in commits:
                    hash_short = commit_info['hash'][:8]
                    message = commit_info['message']
                    item_text = f"{hash_short} - {message}"
                    self.tag_commit_combo.addItem(item_text, commit_info['hash'])
            
            # 更新远程列表
            if hasattr(self, 'tag_remote_combo'):
                remotes = self.git_manager.get_remotes()
                self.tag_remote_combo.clear()
                for remote in remotes:
                    self.tag_remote_combo.addItem(remote)
                    
        except Exception as e:
            print(f"刷新标签信息时出错: {e}")
    
    def create_tag(self):
        """创建新标签（简单版）"""
        tag_name, ok = QInputDialog.getText(self, '创建标签', '标签名称:')
        if not ok or not tag_name.strip():
            return
        
        try:
            if self.git_manager.create_tag(tag_name.strip()):
                self.refresh_tags_info()
                self.statusBar().showMessage(f'已创建标签: {tag_name}', 3000)
            else:
                QMessageBox.warning(self, '创建失败', f'创建标签 "{tag_name}" 失败')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'创建标签时出错: {str(e)}')
    
    def create_tag_from_input(self):
        """从输入框创建标签"""
        if not hasattr(self, 'tag_name_input'):
            return
            
        tag_name = self.tag_name_input.text().strip()
        if not tag_name:
            QMessageBox.warning(self, '创建失败', '请输入标签名称')
            return
        
        tag_message = self.tag_message_input.toPlainText().strip()
        
        # 获取目标提交
        commit_hash = None
        if self.tag_commit_combo.currentData():
            commit_hash = self.tag_commit_combo.currentData()
        
        try:
            if self.git_manager.create_tag(tag_name, tag_message if tag_message else None, commit_hash):
                self.tag_name_input.clear()
                self.tag_message_input.clear()
                self.refresh_tags_info()
                self.statusBar().showMessage(f'已创建标签: {tag_name}', 3000)
            else:
                QMessageBox.warning(self, '创建失败', f'创建标签 "{tag_name}" 失败')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'创建标签时出错: {str(e)}')
    
    def delete_tag(self):
        """删除标签"""
        if not hasattr(self, 'tags_list'):
            return
            
        current_item = self.tags_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '删除失败', '请选择要删除的标签')
            return
        
        tag_name = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, '确认删除', 
            f'确定要删除标签 "{tag_name}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.git_manager.delete_tag(tag_name):
                    self.refresh_tags_info()
                    self.statusBar().showMessage(f'已删除标签: {tag_name}', 3000)
                else:
                    QMessageBox.warning(self, '删除失败', f'删除标签 "{tag_name}" 失败')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除标签时出错: {str(e)}')

    def add_remote_repository(self):
        """添加远程仓库"""
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok1 = QInputDialog.getText(self, '添加远程仓库', '远程仓库名称:')
        if not ok1 or not name.strip():
            return
        
        url, ok2 = QInputDialog.getText(self, '添加远程仓库', '远程仓库URL:')
        if not ok2 or not url.strip():
            return
        
        try:
            if self.git_manager.add_remote(name.strip(), url.strip()):
                self.refresh_remote_info()
                self.statusBar().showMessage(f'已添加远程仓库: {name}', 3000)
            else:
                QMessageBox.warning(self, '添加失败', f'添加远程仓库 "{name}" 失败')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'添加远程仓库时出错: {str(e)}')
    
    def remove_remote_repository(self):
        """删除远程仓库"""
        if not hasattr(self, 'remotes_list'):
            return
            
        current_item = self.remotes_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '删除失败', '请选择要删除的远程仓库')
            return
        
        remote_name = current_item.text()
        
        reply = QMessageBox.question(
            self, '确认删除', 
            f'确定要删除远程仓库 "{remote_name}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.git_manager.remove_remote(remote_name):
                    self.refresh_remote_info()
                    self.statusBar().showMessage(f'已删除远程仓库: {remote_name}', 3000)
                else:
                    QMessageBox.warning(self, '删除失败', f'删除远程仓库 "{remote_name}" 失败')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除远程仓库时出错: {str(e)}')
    
    def show_remote_context_menu(self, position):
        """显示远程仓库右键菜单"""
        if not hasattr(self, 'remotes_list'):
            return
            
        item = self.remotes_list.itemAt(position)
        if not item:
            return
        
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        # 获取
        fetch_action = menu.addAction('📥 获取')
        fetch_action.triggered.connect(lambda: self.fetch_from_remote_by_name(item.text()))
        
        # 删除
        delete_action = menu.addAction('❌ 删除')
        delete_action.triggered.connect(lambda: self.remove_remote_by_name(item.text()))
        
        menu.exec(self.remotes_list.mapToGlobal(position))
    
    def fetch_from_remote_by_name(self, remote_name):
        """从指定远程仓库获取"""
        try:
            if hasattr(self, 'remote_progress'):
                self.remote_progress.setVisible(True)
                self.remote_progress.setRange(0, 0)  # 不确定进度
            
            if self.git_manager.fetch_from_remote(remote_name):
                self.refresh_remote_info()
                self.statusBar().showMessage(f'从 {remote_name} 获取完成', 3000)
            else:
                QMessageBox.warning(self, '获取失败', f'从远程仓库 "{remote_name}" 获取失败')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'获取时出错: {str(e)}')
        finally:
            if hasattr(self, 'remote_progress'):
                self.remote_progress.setVisible(False)
    
    def remove_remote_by_name(self, remote_name):
        """删除指定远程仓库"""
        reply = QMessageBox.question(
            self, '确认删除', 
            f'确定要删除远程仓库 "{remote_name}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.git_manager.remove_remote(remote_name):
                    self.refresh_remote_info()
                    self.statusBar().showMessage(f'已删除远程仓库: {remote_name}', 3000)
                else:
                    QMessageBox.warning(self, '删除失败', f'删除远程仓库 "{remote_name}" 失败')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除远程仓库时出错: {str(e)}')
    
    def push_to_remote(self):
        """推送到远程仓库"""
        if not hasattr(self, 'push_remote_combo'):
            return
            
        remote_name = self.push_remote_combo.currentText()
        branch_name = self.push_branch_combo.currentText()
        
        if not remote_name:
            QMessageBox.warning(self, '推送失败', '请选择远程仓库')
            return
        
        try:
            self.show_loading(f"正在推送到 {remote_name}...")
            
            if self.git_manager.push_to_remote(remote_name, branch_name if branch_name else None):
                self.statusBar().showMessage(f'推送到 {remote_name} 完成', 3000)
            else:
                QMessageBox.warning(self, '推送失败', f'推送到远程仓库 "{remote_name}" 失败')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'推送时出错: {str(e)}')
        finally:
            self.hide_loading()
    
    def setup_remote_repository(self):
        """设置远程仓库地址"""
        if not self.git_manager.repo:
            QMessageBox.warning(self, '警告', '请先打开一个Git仓库')
            return
        
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle('设置远程仓库')
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 说明文本
        info_label = QLabel(
            "设置远程仓库地址后，所有推送操作都会推送到这个仓库。\n"
            "通常设置为您的GitHub仓库地址。"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 远程仓库名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('远程仓库名称:'))
        self.remote_name_edit = QLineEdit()
        self.remote_name_edit.setText('origin')  # 默认名称
        name_layout.addWidget(self.remote_name_edit)
        layout.addLayout(name_layout)
        
        # 远程仓库URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel('远程仓库URL:'))
        self.remote_url_edit = QLineEdit()
        self.remote_url_edit.setPlaceholderText('https://github.com/用户名/仓库名.git')
        url_layout.addWidget(self.remote_url_edit)
        layout.addLayout(url_layout)
        
        # 选项
        self.set_default_checkbox = QCheckBox('设为默认推送仓库')
        self.set_default_checkbox.setChecked(True)
        layout.addWidget(self.set_default_checkbox)
        
        self.initial_push_checkbox = QCheckBox('立即推送当前分支到远程仓库')
        layout.addWidget(self.initial_push_checkbox)
        
        # 当前远程仓库信息
        current_label = QLabel('当前远程仓库:')
        layout.addWidget(current_label)
        
        self.current_remotes_text = QTextEdit()
        self.current_remotes_text.setMaximumHeight(100)
        self.current_remotes_text.setReadOnly(True)
        
        # 显示当前远程仓库
        current_remotes = self.git_manager.get_remotes()
        if current_remotes:
            remotes_info = []
            for remote in current_remotes:
                try:
                    remote_obj = self.git_manager.repo.remotes[remote]
                    urls = list(remote_obj.urls)
                    if urls:
                        remotes_info.append(f"{remote}: {urls[0]}")
                except:
                    remotes_info.append(f"{remote}: (URL获取失败)")
            self.current_remotes_text.setText('\n'.join(remotes_info))
        else:
            self.current_remotes_text.setText('暂无远程仓库')
        
        layout.addWidget(self.current_remotes_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(lambda: self.apply_remote_setup(dialog))
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def apply_remote_setup(self, dialog):
        """应用远程仓库设置"""
        remote_name = self.remote_name_edit.text().strip()
        remote_url = self.remote_url_edit.text().strip()
        
        if not remote_name:
            QMessageBox.warning(dialog, '错误', '请输入远程仓库名称')
            return
        
        if not remote_url:
            QMessageBox.warning(dialog, '错误', '请输入远程仓库URL')
            return
        
        try:
            # 检查远程仓库是否已存在
            current_remotes = self.git_manager.get_remotes()
            
            if remote_name in current_remotes:
                reply = QMessageBox.question(
                    dialog, '远程仓库已存在', 
                    f'远程仓库 "{remote_name}" 已存在，是否覆盖？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # 删除现有远程仓库
                    if not self.git_manager.remove_remote(remote_name):
                        QMessageBox.critical(dialog, '错误', f'删除现有远程仓库 "{remote_name}" 失败')
                        return
                else:
                    return
            
            # 添加远程仓库
            if self.git_manager.add_remote(remote_name, remote_url):
                success_message = f'远程仓库 "{remote_name}" 设置成功！'
                
                # 如果选择了立即推送
                if self.initial_push_checkbox.isChecked():
                    try:
                        current_branch = self.git_manager.get_current_branch()
                        if current_branch:
                            # 设置上游分支并推送
                            result = self.git_manager.repo.git.push('-u', remote_name, current_branch)
                            success_message += f'\n已推送分支 "{current_branch}" 到远程仓库。'
                        else:
                            QMessageBox.warning(dialog, '推送失败', '无法获取当前分支')
                    except Exception as e:
                        QMessageBox.warning(dialog, '推送失败', f'推送到远程仓库失败: {str(e)}')
                
                QMessageBox.information(dialog, '成功', success_message)
                
                # 刷新远程信息
                if hasattr(self, 'refresh_remote_info'):
                    self.refresh_remote_info()
                
                # 更新状态栏
                self.statusBar().showMessage(f'远程仓库 "{remote_name}" 已设置', 5000)
                
                dialog.accept()
                
            else:
                QMessageBox.critical(dialog, '错误', f'添加远程仓库 "{remote_name}" 失败')
                
        except Exception as e:
            QMessageBox.critical(dialog, '错误', f'设置远程仓库时出错: {str(e)}')
    
    def pull_from_remote(self):
        """从远程仓库拉取"""
        if not hasattr(self, 'pull_remote_combo'):
            return
            
        remote_name = self.pull_remote_combo.currentText()
        branch_name = self.pull_branch_combo.currentText()
        
        if not remote_name:
            QMessageBox.warning(self, '拉取失败', '请选择远程仓库')
            return
        
        try:
            self.show_loading(f"正在从 {remote_name} 拉取...")
            
            if self.git_manager.pull_from_remote(remote_name, branch_name if branch_name else None):
                self.refresh_repository()
                self.statusBar().showMessage(f'从 {remote_name} 拉取完成', 3000)
            else:
                QMessageBox.warning(self, '拉取失败', f'从远程仓库 "{remote_name}" 拉取失败')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'拉取时出错: {str(e)}')
        finally:
            self.hide_loading()
    
    def fetch_from_remote(self):
        """从远程仓库获取"""
        if not hasattr(self, 'pull_remote_combo'):
            return
            
        remote_name = self.pull_remote_combo.currentText()
        
        if not remote_name:
            QMessageBox.warning(self, '获取失败', '请选择远程仓库')
            return
        
        try:
            self.show_loading(f"正在从 {remote_name} 获取...")
            
            if self.git_manager.fetch_from_remote(remote_name):
                self.refresh_remote_info()
                self.statusBar().showMessage(f'从 {remote_name} 获取完成', 3000)
            else:
                QMessageBox.warning(self, '获取失败', f'从远程仓库 "{remote_name}" 获取失败')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'获取时出错: {str(e)}')
        finally:
            self.hide_loading()

    def update_branch_list(self):
        """更新分支列表"""
        if not hasattr(self, 'branch_list') or not self.git_manager.repo:
            return
        
        try:
            branches = self.git_manager.get_branches()
            self.branch_list.clear()
            
            for branch in branches:
                item = QListWidgetItem(branch)
                # 标记当前分支
                if self.git_manager.repo.active_branch and branch == self.git_manager.repo.active_branch.name:
                    item.setText(f"* {branch}")
                self.branch_list.addItem(item)
                
        except Exception as e:
            print(f"更新分支列表时出错: {e}")
    
    def refresh_tags_info(self):
        """刷新标签信息"""
        if not hasattr(self, 'tags_list'):
            return
            
        if not self.git_manager.repo:
            self.tags_list.clear()
            return
        
        try:
            tags = self.git_manager.get_tags()
            self.tags_list.clear()
            
            for tag in tags:
                self.tags_list.addItem(tag)
                
        except Exception as e:
            print(f"刷新标签信息时出错: {e}")
    
    def show_tag_context_menu(self, position):
        """显示标签右键菜单"""
        if not hasattr(self, 'tags_list'):
            return
            
        item = self.tags_list.itemAt(position)
        if not item:
            return
        
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        # 删除标签
        delete_action = menu.addAction('❌ 删除标签')
        delete_action.triggered.connect(lambda: self.delete_tag_by_name(item.text()))
        
        # 推送标签
        push_action = menu.addAction('📤 推送标签')
        push_action.triggered.connect(lambda: self.push_tag_by_name(item.text()))
        
        menu.exec(self.tags_list.mapToGlobal(position))
    
    def create_tag(self):
        """创建标签"""
        from PyQt6.QtWidgets import QInputDialog
        
        tag_name, ok1 = QInputDialog.getText(self, '创建标签', '标签名称:')
        if not ok1 or not tag_name.strip():
            return
        
        message, ok2 = QInputDialog.getText(self, '创建标签', '标签消息 (可选):')
        if not ok2:
            message = ""
        
        try:
            if self.git_manager.create_tag(tag_name.strip(), message.strip() if message else None):
                self.refresh_tags_info()
                self.statusBar().showMessage(f'已创建标签: {tag_name}', 3000)
            else:
                QMessageBox.warning(self, '创建失败', f'创建标签 "{tag_name}" 失败')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'创建标签时出错: {str(e)}')
    
    def delete_tag_by_name(self, tag_name):
        """删除指定标签"""
        reply = QMessageBox.question(
            self, '确认删除', 
            f'确定要删除标签 "{tag_name}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.git_manager.delete_tag(tag_name):
                    self.refresh_tags_info()
                    self.statusBar().showMessage(f'已删除标签: {tag_name}', 3000)
                else:
                    QMessageBox.warning(self, '删除失败', f'删除标签 "{tag_name}" 失败')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除标签时出错: {str(e)}')
    
    def push_tag_by_name(self, tag_name):
        """推送指定标签"""
        try:
            if self.git_manager.push_tag(tag_name):
                self.statusBar().showMessage(f'标签 {tag_name} 推送完成', 3000)
            else:
                QMessageBox.warning(self, '推送失败', f'推送标签 "{tag_name}" 失败')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'推送标签时出错: {str(e)}')
    
    def view_tag_details(self, item):
        """查看标签详情"""
        tag_name = item.text()
        
        try:
            # 获取标签信息
            tag = self.git_manager.repo.tags[tag_name]
            
            # 构建详情文本
            details = f"标签: {tag_name}\n"
            details += f"提交: {tag.commit.hexsha[:8]}\n"
            details += f"作者: {tag.commit.author.name} <{tag.commit.author.email}>\n"
            details += f"日期: {tag.commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            details += f"消息: {tag.commit.message.strip()}"
            
            # 如果是标注标签，添加标签消息
            if hasattr(tag, 'tag') and tag.tag:
                details += f"\n\n标签消息: {tag.tag.message.strip()}"
            
            QMessageBox.information(self, f'标签详情 - {tag_name}', details)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查看标签详情时出错: {str(e)}')
    
    def push_selected_tag(self):
        """推送选中的标签"""
        if not hasattr(self, 'tags_list'):
            return
            
        current_item = self.tags_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '推送失败', '请选择要推送的标签')
            return
        
        tag_name = current_item.text()
        self.push_tag_by_name(tag_name)
    
    def delete_selected_tag(self):
        """删除选中的标签"""
        if not hasattr(self, 'tags_list'):
            return
            
        current_item = self.tags_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '删除失败', '请选择要删除的标签')
            return
        
        tag_name = current_item.text()
        self.delete_tag_by_name(tag_name)
    
    def push_all_tags(self):
        """推送所有标签"""
        try:
            if self.git_manager.push_all_tags():
                self.statusBar().showMessage('所有标签推送完成', 3000)
            else:
                QMessageBox.warning(self, '推送失败', '推送所有标签失败')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'推送所有标签时出错: {str(e)}')

    def update_enhanced_file_lists(self):
        """更新增强文件列表"""
        if not hasattr(self, 'working_files_enhanced') or not hasattr(self, 'staged_files_enhanced'):
            return
        
        if not self.git_manager.repo:
            self.working_files_enhanced.clear()
            self.staged_files_enhanced.clear()
            return
        
        try:
            status = self.git_manager.get_status()
            
            # 清空列表
            self.working_files_enhanced.clear()
            self.staged_files_enhanced.clear()
            
            # 更新工作区文件
            for file_path, status_code in status.get('modified', []):
                status_text = self.get_file_status_text(status_code)
                item_text = f"[{status_text}] {file_path}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.working_files_enhanced.addItem(item)
            
            # 更新暂存区文件
            for file_path in status.get('staged', []):
                item = QListWidgetItem(file_path)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.staged_files_enhanced.addItem(item)
                
        except Exception as e:
            print(f"更新增强文件列表时出错: {e}")
    
    def update_enhanced_commit_history(self):
        """更新增强提交历史"""
        if not hasattr(self, 'recent_commits_enhanced'):
            return
        
        if not self.git_manager.repo:
            self.recent_commits_enhanced.clear()
            return
        
        try:
            commits = self.git_manager.get_commit_history(max_count=10)
            self.recent_commits_enhanced.clear()
            
            for commit_info in commits:
                hash_short = commit_info['hash'][:8]
                message = commit_info['message']
                author = commit_info['author']
                date = commit_info['date']
                
                item_text = f"{hash_short} - {message} ({author}, {date})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, commit_info['hash'])
                self.recent_commits_enhanced.addItem(item)
                
        except Exception as e:
            print(f"更新增强提交历史时出错: {e}")
    
    def get_file_status_text(self, status_code):
        """获取文件状态文本"""
        status_map = {
            'M': '已修改',
            'A': '新文件',
            'D': '已删除',
            'R': '已重命名',
            'C': '已复制',
            'U': '未合并'
        }
        return status_map.get(status_code, '未知')

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
    
    def show_branch_context_menu(self, position):
        """显示分支右键菜单"""
        if not self.git_manager.repo:
            return
        
        item = self.branch_list.itemAt(position)
        if not item:
            return
        
        # 解析分支名称
        branch_text = item.text()
        branch_name = branch_text.replace('* ', '').replace('  ', '').strip()
        is_current = branch_text.startswith('* ')
        
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        if not is_current:
            # 切换到此分支
            switch_action = menu.addAction('切换到此分支')
            switch_action.triggered.connect(lambda: self.switch_to_branch(branch_name))
        
        # 创建新分支（基于选中分支）
        create_action = menu.addAction('基于此分支创建新分支')
        create_action.triggered.connect(lambda: self.create_branch_from(branch_name))
        
        if not is_current:
            menu.addSeparator()
            
            # 合并到当前分支
            merge_action = menu.addAction('合并到当前分支')
            merge_action.triggered.connect(lambda: self.merge_branch_to_current(branch_name))
            
            # 删除分支
            delete_action = menu.addAction('删除分支')
            delete_action.triggered.connect(lambda: self.delete_branch_by_name(branch_name))
        
        menu.addSeparator()
        
        # 重命名分支
        rename_action = menu.addAction('重命名分支')
        rename_action.triggered.connect(lambda: self.rename_branch(branch_name))
        
        menu.exec(self.branch_list.mapToGlobal(position))
    
    def switch_to_branch_by_item(self, item):
        """双击分支项切换分支"""
        branch_text = item.text()
        branch_name = branch_text.replace('* ', '').replace('  ', '').strip()
        
        # 如果不是当前分支，则切换
        if not branch_text.startswith('* '):
            self.switch_to_branch(branch_name)
    
    def switch_to_branch(self, branch_name):
        """切换到指定分支"""
        if not self.git_manager.repo:
            return
        
        try:
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
                self.statusBar().showMessage(f'已切换到分支: {branch_name}', 3000)
            else:
                QMessageBox.warning(self, '切换失败', f'切换到分支 "{branch_name}" 失败')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'切换分支时出错: {str(e)}')
    
    def create_branch_from(self, base_branch):
        """基于指定分支创建新分支"""
        from PyQt6.QtWidgets import QInputDialog
        
        branch_name, ok = QInputDialog.getText(
            self, '创建新分支', 
            f'基于分支 "{base_branch}" 创建新分支，请输入分支名称:'
        )
        
        if ok and branch_name.strip():
            branch_name = branch_name.strip()
            
            if not self._is_valid_branch_name(branch_name):
                QMessageBox.warning(
                    self, '无效分支名', 
                    '分支名称包含无效字符。\n分支名称不能包含空格、冒号、问号等特殊字符。'
                )
                return
            
            try:
                # 先切换到基础分支
                if self.git_manager.checkout_branch(base_branch):
                    # 然后创建新分支
                    if self.git_manager.create_branch(branch_name, True):
                        self.refresh_repository()
                        self.statusBar().showMessage(f'已创建并切换到新分支: {branch_name}', 3000)
                    else:
                        QMessageBox.warning(self, '创建失败', f'创建分支 "{branch_name}" 失败')
                else:
                    QMessageBox.warning(self, '错误', f'无法切换到基础分支 "{base_branch}"')
                    
            except Exception as e:
                QMessageBox.critical(self, '错误', f'创建分支时出错: {str(e)}')
    
    def delete_branch(self):
        """删除选中的分支"""
        selected_items = self.branch_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, '提示', '请选择要删除的分支')
            return
        
        branch_text = selected_items[0].text()
        branch_name = branch_text.replace('* ', '').replace('  ', '').strip()
        
        # 检查是否为当前分支
        if branch_text.startswith('* '):
            QMessageBox.warning(self, '无法删除', '不能删除当前分支')
            return
        
        self.delete_branch_by_name(branch_name)
    
    def delete_branch_by_name(self, branch_name):
        """删除指定分支"""
        reply = QMessageBox.question(
            self, '确认删除', 
            f'确定要删除分支 "{branch_name}" 吗？\n此操作不可撤销！',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 使用GitPython删除分支
                self.git_manager.repo.delete_head(branch_name)
                self.refresh_repository()
                self.statusBar().showMessage(f'已删除分支: {branch_name}', 3000)
                
            except Exception as e:
                QMessageBox.critical(self, '删除失败', f'删除分支 "{branch_name}" 失败: {str(e)}')
    
    def merge_branch(self):
        """合并选中的分支到当前分支"""
        selected_items = self.branch_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, '提示', '请选择要合并的分支')
            return
        
        branch_text = selected_items[0].text()
        branch_name = branch_text.replace('* ', '').replace('  ', '').strip()
        
        # 检查是否为当前分支
        if branch_text.startswith('* '):
            QMessageBox.warning(self, '无效操作', '不能合并当前分支到自己')
            return
        
        self.merge_branch_to_current(branch_name)
    
    def merge_branch_to_current(self, branch_name):
        """合并指定分支到当前分支"""
        try:
            current_branch = self.git_manager.repo.active_branch.name
            
            reply = QMessageBox.question(
                self, '确认合并', 
                f'确定要将分支 "{branch_name}" 合并到当前分支 "{current_branch}" 吗？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 执行合并
                merge_base = self.git_manager.repo.merge_base(current_branch, branch_name)[0]
                self.git_manager.repo.index.merge_tree(branch_name, base=merge_base)
                
                # 检查是否有冲突
                if self.git_manager.repo.index.conflicts:
                    QMessageBox.warning(
                        self, '合并冲突', 
                        f'合并分支 "{branch_name}" 时发生冲突。\n请手动解决冲突后提交。'
                    )
                else:
                    # 创建合并提交
                    self.git_manager.repo.index.commit(
                        f"Merge branch '{branch_name}' into {current_branch}",
                        parent_commits=(self.git_manager.repo.head.commit, 
                                      self.git_manager.repo.commit(branch_name))
                    )
                    
                    self.refresh_repository()
                    self.statusBar().showMessage(f'已将分支 "{branch_name}" 合并到 "{current_branch}"', 3000)
                    
        except Exception as e:
            QMessageBox.critical(self, '合并失败', f'合并分支时出错: {str(e)}')
    
    def rename_branch(self, old_name):
        """重命名分支"""
        from PyQt6.QtWidgets import QInputDialog
        
        new_name, ok = QInputDialog.getText(
            self, '重命名分支', 
            f'为分支 "{old_name}" 输入新名称:',
            text=old_name
        )
        
        if ok and new_name.strip() and new_name.strip() != old_name:
            new_name = new_name.strip()
            
            if not self._is_valid_branch_name(new_name):
                QMessageBox.warning(
                    self, '无效分支名', 
                    '分支名称包含无效字符。\n分支名称不能包含空格、冒号、问号等特殊字符。'
                )
                return
            
            try:
                # 检查新名称是否已存在
                existing_branches = [ref.name for ref in self.git_manager.repo.heads]
                if new_name in existing_branches:
                    QMessageBox.warning(self, '名称冲突', f'分支 "{new_name}" 已存在')
                    return
                
                # 重命名分支
                branch = self.git_manager.repo.heads[old_name]
                branch.rename(new_name)
                
                self.refresh_repository()
                self.statusBar().showMessage(f'已将分支 "{old_name}" 重命名为 "{new_name}"', 3000)
                
            except Exception as e:
                QMessageBox.critical(self, '重命名失败', f'重命名分支时出错: {str(e)}')
    
    def show_working_files_context_menu(self, position):
        """显示工作区文件右键菜单"""
        item = self.working_files.itemAt(position)
        if not item:
            return
        
        # 解析文件路径
        file_text = item.text()
        file_path = self._parse_file_path(file_text)
        
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        # 添加到暂存区
        stage_action = menu.addAction('📁 添加到暂存区')
        stage_action.triggered.connect(lambda: self.stage_file(file_path))
        
        menu.addSeparator()
        
        # 查看差异
        diff_action = menu.addAction('🔍 查看差异')
        diff_action.triggered.connect(lambda: self.view_file_diff_by_path(file_path))
        
        # 恢复文件
        restore_action = menu.addAction('↩️ 恢复文件')
        restore_action.triggered.connect(lambda: self.restore_file(file_path))
        
        menu.addSeparator()
        
        # 在文件管理器中显示
        show_action = menu.addAction('📂 在文件管理器中显示')
        show_action.triggered.connect(lambda: self.show_in_explorer(file_path))
        
        # 用默认程序打开
        open_action = menu.addAction('📝 用默认程序打开')
        open_action.triggered.connect(lambda: self.open_file_external(file_path))
        
        menu.exec(self.working_files.mapToGlobal(position))
    
    def show_staged_files_context_menu(self, position):
        """显示暂存区文件右键菜单"""
        item = self.staged_files.itemAt(position)
        if not item:
            return
        
        file_path = item.text()
        
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        # 从暂存区移除
        unstage_action = menu.addAction('📤 从暂存区移除')
        unstage_action.triggered.connect(lambda: self.unstage_file(file_path))
        
        menu.addSeparator()
        
        # 查看暂存的差异
        diff_action = menu.addAction('🔍 查看暂存的差异')
        diff_action.triggered.connect(lambda: self.view_staged_diff(file_path))
        
        menu.addSeparator()
        
        # 在文件管理器中显示
        show_action = menu.addAction('📂 在文件管理器中显示')
        show_action.triggered.connect(lambda: self.show_in_explorer(file_path))
        
        # 用默认程序打开
        open_action = menu.addAction('📝 用默认程序打开')
        open_action.triggered.connect(lambda: self.open_file_external(file_path))
        
        menu.exec(self.staged_files.mapToGlobal(position))
    
    def _parse_file_path(self, file_text):
        """从文件列表项文本中解析文件路径"""
        # 去除状态标记，如 "[新文件]", "[已修改]" 等
        import re
        # 匹配 [状态] 文件路径 的格式
        match = re.match(r'\[.*?\]\s*(.+)', file_text)
        if match:
            return match.group(1)
        return file_text
    
    def stage_file(self, file_path):
        """暂存单个文件"""
        try:
            if self.git_manager.add_file(file_path):
                self.refresh_repository()
                self.statusBar().showMessage(f'已添加文件到暂存区: {file_path}', 3000)
            else:
                QMessageBox.warning(self, '操作失败', f'添加文件到暂存区失败: {file_path}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'添加文件时出错: {str(e)}')
    
    def unstage_file(self, file_path):
        """从暂存区移除单个文件"""
        try:
            self.git_manager.repo.index.reset(paths=[file_path])
            self.refresh_repository()
            self.statusBar().showMessage(f'已从暂存区移除文件: {file_path}', 3000)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'移除文件时出错: {str(e)}')
    
    def restore_file(self, file_path):
        """恢复文件到最后提交的状态"""
        reply = QMessageBox.question(
            self, '确认恢复', 
            f'确定要恢复文件 "{file_path}" 吗？\n这将丢失所有未提交的更改！',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.git_manager.repo.index.checkout([file_path], force=True)
                self.refresh_repository()
                self.statusBar().showMessage(f'已恢复文件: {file_path}', 3000)
            except Exception as e:
                QMessageBox.critical(self, '错误', f'恢复文件时出错: {str(e)}')
    
    def view_file_diff(self, item):
        """双击查看文件差异"""
        if item.listWidget() == self.working_files:
            file_path = self._parse_file_path(item.text())
            self.view_file_diff_by_path(file_path)
        elif item.listWidget() == self.staged_files:
            file_path = item.text()
            self.view_staged_diff(file_path)
    
    def view_file_diff_by_path(self, file_path):
        """查看工作区文件的差异"""
        try:
            if not self.git_manager.repo:
                return
            
            # 获取文件差异
            diff = self.git_manager.repo.git.diff(file_path)
            
            if not diff:
                QMessageBox.information(self, '信息', f'文件 "{file_path}" 没有变更')
                return
            
            self.show_diff_dialog(f'文件差异: {file_path}', diff)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查看文件差异时出错: {str(e)}')
    
    def view_staged_diff(self, file_path):
        """查看暂存区文件的差异"""
        try:
            if not self.git_manager.repo:
                return
            
            # 获取暂存区差异
            diff = self.git_manager.repo.git.diff('--cached', file_path)
            
            if not diff:
                QMessageBox.information(self, '信息', f'暂存区文件 "{file_path}" 没有变更')
                return
            
            self.show_diff_dialog(f'暂存区差异: {file_path}', diff)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查看暂存区差异时出错: {str(e)}')
    
    def show_diff_dialog(self, title, diff_content):
        """显示增强的差异对话框"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QTabWidget, QPlainTextEdit
        from PyQt6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QTextDocument
        from PyQt6.QtCore import QRegularExpression
        
        # 创建差异语法高亮器
        class DiffHighlighter(QSyntaxHighlighter):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.highlighting_rules = []
                
                # 添加行格式
                added_format = QTextCharFormat()
                added_format.setBackground(QColor(200, 255, 200))  # 浅绿色
                added_format.setForeground(QColor(0, 100, 0))      # 深绿色
                self.highlighting_rules.append((QRegularExpression(r'^\+.*'), added_format))
                
                removed_format = QTextCharFormat()
                removed_format.setBackground(QColor(255, 200, 200))  # 浅红色
                removed_format.setForeground(QColor(150, 0, 0))      # 深红色
                self.highlighting_rules.append((QRegularExpression(r'^-.*'), removed_format))
                
                # 文件头格式
                header_format = QTextCharFormat()
                header_format.setForeground(QColor(100, 100, 100))   # 灰色
                header_format.setFontWeight(QFont.Weight.Bold)
                self.highlighting_rules.append((QRegularExpression(r'^@@.*@@'), header_format))
                self.highlighting_rules.append((QRegularExpression(r'^diff --git.*'), header_format))
                self.highlighting_rules.append((QRegularExpression(r'^index.*'), header_format))
                self.highlighting_rules.append((QRegularExpression(r'^\+\+\+.*'), header_format))
                self.highlighting_rules.append((QRegularExpression(r'^---.*'), header_format))
            
            def highlightBlock(self, text):
                for pattern, format in self.highlighting_rules:
                    match_iterator = pattern.globalMatch(text)
                    while match_iterator.hasNext():
                        match = match_iterator.next()
                        self.setFormat(match.capturedStart(), match.capturedLength(), format)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.resize(1000, 700)
        
        layout = QVBoxLayout(dialog)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 高亮差异选项卡
        highlighted_diff = QPlainTextEdit()
        highlighted_diff.setPlainText(diff_content)
        highlighted_diff.setReadOnly(True)
        highlighted_diff.setFont(QFont('Consolas', 10))
        
        # 应用语法高亮
        highlighter = DiffHighlighter(highlighted_diff.document())
        
        tab_widget.addTab(highlighted_diff, '🎨 高亮差异')
        
        # 原始差异选项卡
        raw_diff = QTextEdit()
        raw_diff.setPlainText(diff_content)
        raw_diff.setReadOnly(True)
        raw_diff.setFont(QFont('Consolas', 10))
        
        tab_widget.addTab(raw_diff, '📄 原始差异')
        
        # 并排比较选项卡（如果差异内容适合）
        side_by_side_widget = self.create_side_by_side_diff(diff_content)
        if side_by_side_widget:
            tab_widget.addTab(side_by_side_widget, '↔️ 并排比较')
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 复制按钮
        copy_btn = QPushButton('📋 复制差异')
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(diff_content))
        button_layout.addWidget(copy_btn)
        
        # 保存按钮
        save_btn = QPushButton('💾 保存为文件')
        save_btn.clicked.connect(lambda: self.save_diff_to_file(diff_content))
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def create_side_by_side_diff(self, diff_content):
        """创建并排比较视图"""
        try:
            from PyQt6.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QLabel, QVBoxLayout
            
            # 解析差异内容
            lines = diff_content.split('\n')
            old_lines = []
            new_lines = []
            
            for line in lines:
                if line.startswith('-') and not line.startswith('---'):
                    old_lines.append(line[1:])  # 移除 - 前缀
                elif line.startswith('+') and not line.startswith('+++'):
                    new_lines.append(line[1:])  # 移除 + 前缀
                elif line.startswith(' '):
                    # 上下文行，同时添加到两边
                    context_line = line[1:]
                    old_lines.append(context_line)
                    new_lines.append(context_line)
            
            # 如果解析的内容太少，不显示并排比较
            if len(old_lines) < 5 and len(new_lines) < 5:
                return None
            
            widget = QWidget()
            layout = QHBoxLayout(widget)
            
            # 左侧：删除的内容
            left_layout = QVBoxLayout()
            left_label = QLabel('删除的内容')
            left_label.setStyleSheet("background-color: #ffeeee; padding: 5px; font-weight: bold;")
            left_layout.addWidget(left_label)
            
            left_text = QTextEdit()
            left_text.setPlainText('\n'.join(old_lines))
            left_text.setReadOnly(True)
            left_text.setFont(QFont('Consolas', 10))
            left_layout.addWidget(left_text)
            
            # 右侧：添加的内容
            right_layout = QVBoxLayout()
            right_label = QLabel('添加的内容')
            right_label.setStyleSheet("background-color: #eeffee; padding: 5px; font-weight: bold;")
            right_layout.addWidget(right_label)
            
            right_text = QTextEdit()
            right_text.setPlainText('\n'.join(new_lines))
            right_text.setReadOnly(True)
            right_text.setFont(QFont('Consolas', 10))
            right_layout.addWidget(right_text)
            
            # 添加到主布局
            left_widget = QWidget()
            left_widget.setLayout(left_layout)
            right_widget = QWidget()
            right_widget.setLayout(right_layout)
            
            layout.addWidget(left_widget)
            layout.addWidget(right_widget)
            
            return widget
            
        except Exception as e:
            print(f"创建并排比较视图时出错: {e}")
            return None
    
    def copy_to_clipboard(self, content):
        """复制内容到剪贴板"""
        from PyQt6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        self.statusBar().showMessage('差异内容已复制到剪贴板', 3000)
    
    def save_diff_to_file(self, content):
        """保存差异到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存差异文件', 'diff.patch', 'Patch Files (*.patch);;Text Files (*.txt);;All Files (*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.statusBar().showMessage(f'差异已保存到: {file_path}', 3000)
            except Exception as e:
                QMessageBox.critical(self, '保存失败', f'保存差异文件时出错: {str(e)}')

    def show_in_explorer(self, file_path):
        """在文件管理器中显示文件"""
        import os
        import subprocess
        
        try:
            full_path = os.path.join(self.git_manager.repo.working_dir, file_path)
            
            if os.path.exists(full_path):
                # Windows
                subprocess.run(['explorer', '/select,', full_path], check=True)
            else:
                QMessageBox.warning(self, '文件不存在', f'文件 "{file_path}" 不存在')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'打开文件管理器时出错: {str(e)}')
    
    def open_file_external(self, file_path):
        """用默认程序打开文件"""
        import os
        import subprocess
        
        try:
            full_path = os.path.join(self.git_manager.repo.working_dir, file_path)
            
            if os.path.exists(full_path):
                # Windows
                os.startfile(full_path)
            else:
                QMessageBox.warning(self, '文件不存在', f'文件 "{file_path}" 不存在')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'打开文件时出错: {str(e)}')
    
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
