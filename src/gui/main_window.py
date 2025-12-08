"""
主窗口模块

提供应用程序的主窗口界面，整合所有 UI 组件。
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QStatusBar, QLabel, QMessageBox, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QShortcut

from .chat_widget import ChatWidget
from .session_sidebar import SessionSidebar
from .file_browser import FileBrowser
from .settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    主窗口
    
    整合聊天界面、会话列表和文件浏览器，提供工具栏和状态栏。
    
    Signals:
        new_session_requested: 请求新建会话
        save_session_requested: 请求保存会话
        settings_requested: 请求打开设置
    """
    
    # 信号定义
    new_session_requested = pyqtSignal()
    save_session_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    model_switch_requested = pyqtSignal(str)  # 模型 ID
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化主窗口
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        # 组件引用
        self.chat_widget: Optional[ChatWidget] = None
        self.session_sidebar: Optional[SessionSidebar] = None
        self.file_browser: Optional[FileBrowser] = None
        self.toolbar: Optional[QToolBar] = None
        self.status_bar: Optional[QStatusBar] = None
        self.model_status_label: Optional[QLabel] = None
        self.connection_status_label: Optional[QLabel] = None
        
        self._init_ui()
        self._create_toolbar()
        self._create_status_bar()
        self._setup_shortcuts()
        
        logger.info("MainWindow 初始化完成")
    
    def _init_ui(self) -> None:
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle("AI Chat Agent")
        self.resize(1200, 800)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建三栏布局（使用 QSplitter）
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：会话列表
        self.session_sidebar = SessionSidebar()
        splitter.addWidget(self.session_sidebar)
        
        # 中间：聊天界面
        self.chat_widget = ChatWidget()
        splitter.addWidget(self.chat_widget)
        
        # 右侧：文件浏览器
        self.file_browser = FileBrowser()
        splitter.addWidget(self.file_browser)
        
        # 设置初始比例（1:3:1）
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)
        
        # 设置最小宽度
        splitter.setChildrenCollapsible(False)
        
        main_layout.addWidget(splitter)
        
        logger.debug("主窗口 UI 初始化完成")
    
    def _create_toolbar(self) -> None:
        """创建工具栏"""
        self.toolbar = QToolBar("主工具栏")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # 新建会话按钮
        new_session_action = QAction("新建会话", self)
        new_session_action.setShortcut(QKeySequence("Ctrl+N"))
        new_session_action.setStatusTip("创建新的对话会话 (Ctrl+N)")
        new_session_action.triggered.connect(self._on_new_session)
        self.toolbar.addAction(new_session_action)
        
        self.toolbar.addSeparator()
        
        # 保存会话按钮
        save_session_action = QAction("保存会话", self)
        save_session_action.setShortcut(QKeySequence("Ctrl+S"))
        save_session_action.setStatusTip("保存当前会话 (Ctrl+S)")
        save_session_action.triggered.connect(self._on_save_session)
        self.toolbar.addAction(save_session_action)
        
        self.toolbar.addSeparator()
        
        # 设置按钮
        settings_action = QAction("设置", self)
        settings_action.setStatusTip("打开设置对话框")
        settings_action.triggered.connect(self._on_settings)
        self.toolbar.addAction(settings_action)
        
        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        self.toolbar.addWidget(spacer)
        
        # 模型选择器
        model_label = QLabel("模型: ")
        self.toolbar.addWidget(model_label)
        
        self.model_selector = QComboBox()
        self.model_selector.setMinimumWidth(200)
        self.model_selector.setToolTip("选择要使用的 AI 模型")
        self.model_selector.currentIndexChanged.connect(self._on_model_selected)
        self.toolbar.addWidget(self.model_selector)
        
        logger.debug("工具栏创建完成")
    
    def _create_status_bar(self) -> None:
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 模型状态标签
        self.model_status_label = QLabel("模型: 未配置")
        self.model_status_label.setStyleSheet("padding: 0 10px;")
        self.status_bar.addPermanentWidget(self.model_status_label)
        
        # 连接状态标签
        self.connection_status_label = QLabel("● 未连接")
        self.connection_status_label.setStyleSheet("color: gray; padding: 0 10px;")
        self.status_bar.addPermanentWidget(self.connection_status_label)
        
        # 默认消息
        self.status_bar.showMessage("就绪", 3000)
        
        logger.debug("状态栏创建完成")
    
    def _setup_shortcuts(self) -> None:
        """设置键盘快捷键"""
        # Ctrl+N: 新建会话
        new_session_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_session_shortcut.activated.connect(self._on_new_session)
        
        # Ctrl+S: 保存会话
        save_session_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_session_shortcut.activated.connect(self._on_save_session)
        
        # Ctrl+Enter: 发送消息（在 ChatWidget 中处理）
        
        logger.debug("键盘快捷键设置完成")
    
    def _on_new_session(self) -> None:
        """新建会话处理"""
        logger.info("触发新建会话")
        self.new_session_requested.emit()
    
    def _on_save_session(self) -> None:
        """保存会话处理"""
        logger.info("触发保存会话")
        self.save_session_requested.emit()
    
    def _on_settings(self) -> None:
        """设置按钮处理"""
        logger.info("触发打开设置")
        self.settings_requested.emit()
    
    def _on_model_selected(self, index: int) -> None:
        """模型选择处理"""
        if index >= 0:
            model_id = self.model_selector.itemData(index)
            if model_id:
                logger.info(f"用户选择模型: {model_id}")
                self.model_switch_requested.emit(model_id)
    
    def get_chat_widget(self) -> ChatWidget:
        """
        获取聊天组件
        
        Returns:
            ChatWidget: 聊天组件实例
        """
        return self.chat_widget
    
    def get_session_sidebar(self) -> SessionSidebar:
        """
        获取会话侧边栏组件
        
        Returns:
            SessionSidebar: 会话侧边栏组件实例
        """
        return self.session_sidebar
    
    def get_file_browser(self) -> FileBrowser:
        """
        获取文件浏览器组件
        
        Returns:
            FileBrowser: 文件浏览器组件实例
        """
        return self.file_browser
    
    def update_model_list(self, models: list, active_model_id: str = None) -> None:
        """
        更新模型列表
        
        Args:
            models: 模型配置列表
            active_model_id: 当前激活的模型 ID
        """
        # 暂时断开信号，避免触发切换
        self.model_selector.blockSignals(True)
        
        self.model_selector.clear()
        
        for model in models:
            self.model_selector.addItem(model.name, model.id)
        
        # 设置当前选中的模型
        if active_model_id:
            for i in range(self.model_selector.count()):
                if self.model_selector.itemData(i) == active_model_id:
                    self.model_selector.setCurrentIndex(i)
                    break
        
        # 恢复信号
        self.model_selector.blockSignals(False)
        
        logger.debug(f"更新模型列表: {len(models)} 个模型")
    
    def update_model_status(self, model_name: str) -> None:
        """
        更新模型状态显示
        
        Args:
            model_name: 模型名称
        """
        self.model_status_label.setText(f"模型: {model_name}")
        logger.debug(f"更新模型状态: {model_name}")
    
    def update_connection_status(self, connected: bool, message: str = "") -> None:
        """
        更新连接状态显示
        
        Args:
            connected: 是否已连接
            message: 状态消息
        """
        if connected:
            self.connection_status_label.setText("● 已连接")
            self.connection_status_label.setStyleSheet("color: green; padding: 0 10px;")
        else:
            status_text = "● 未连接"
            if message:
                status_text = f"● {message}"
            self.connection_status_label.setText(status_text)
            self.connection_status_label.setStyleSheet("color: red; padding: 0 10px;")
        
        logger.debug(f"更新连接状态: connected={connected}, message={message}")
    
    def show_status_message(self, message: str, timeout: int = 3000) -> None:
        """
        在状态栏显示临时消息
        
        Args:
            message: 消息内容
            timeout: 显示时长（毫秒）
        """
        self.status_bar.showMessage(message, timeout)
    
    def show_error_dialog(self, title: str, message: str) -> None:
        """
        显示错误对话框
        
        Args:
            title: 对话框标题
            message: 错误消息
        """
        QMessageBox.critical(self, title, message)
        logger.error(f"显示错误对话框: {title} - {message}")
    
    def show_info_dialog(self, title: str, message: str) -> None:
        """
        显示信息对话框
        
        Args:
            title: 对话框标题
            message: 信息内容
        """
        QMessageBox.information(self, title, message)
        logger.info(f"显示信息对话框: {title} - {message}")
    
    def show_warning_dialog(self, title: str, message: str) -> None:
        """
        显示警告对话框
        
        Args:
            title: 对话框标题
            message: 警告消息
        """
        QMessageBox.warning(self, title, message)
        logger.warning(f"显示警告对话框: {title} - {message}")
    
    def closeEvent(self, event) -> None:
        """
        窗口关闭事件处理
        
        Args:
            event: 关闭事件
        """
        # 可以在这里添加关闭前的确认逻辑
        logger.info("主窗口关闭")
        event.accept()
