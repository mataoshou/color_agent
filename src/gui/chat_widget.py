"""
聊天界面组件

提供消息列表展示、消息输入框和发送按钮。
"""

import logging
from typing import Optional
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QTextEdit, QPushButton, QLabel, QListWidgetItem, QToolBar, QMenu, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QPoint
from PyQt6.QtGui import QKeyEvent, QAction, QCursor

from .message_bubble import MessageBubble, TypingIndicator
from .tool_call_widget import ToolCallWidget
from .text_diff_viewer import show_text_diff

logger = logging.getLogger(__name__)


class ChatWidget(QWidget):
    """聊天界面组件"""
    
    # 信号定义
    message_sent = pyqtSignal(str)  # 消息发送信号
    rollback_requested = pyqtSignal(int)  # 回滚请求信号（携带消息序号）
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化聊天界面组件
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        # 流式响应相关
        self._streaming_buffer = []  # 缓冲区
        self._streaming_item = None  # 当前流式响应的列表项
        self._streaming_bubble = None  # 当前流式响应的气泡
        self._update_timer = QTimer()  # 批量更新定时器
        self._update_timer.timeout.connect(self._flush_streaming_buffer)
        self._typing_indicator_item = None  # 正在输入指示器项
        
        # 工具调用相关
        self._active_tool_widgets = {}  # 活动的工具调用组件 {tool_name: (item, widget)}
        
        # 浮动工具栏
        self._floating_toolbar = None
        self._selected_text = ""
        
        self._init_ui()
        self._connect_signals()
        
        logger.info("ChatWidget 初始化完成")
    
    def _init_ui(self) -> None:
        """初始化 UI"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 消息列表展示区域
        self.message_list = QListWidget()
        self.message_list.setObjectName("messageList")
        self.message_list.setAlternatingRowColors(True)
        self.message_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.message_list.setSpacing(8)
        self.message_list.setContentsMargins(10, 10, 10, 10)  # 添加边距，让气泡有空间扩展
        self.message_list.setWordWrap(True)
        self.message_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.message_list.customContextMenuRequested.connect(self._show_message_context_menu)
        self.message_list.viewport().installEventFilter(self)
        
        # 设置大小策略，让列表可以自由扩展
        from PyQt6.QtWidgets import QSizePolicy
        self.message_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 确保列表项能够自动调整大小
        self.message_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        
        # 设置滚动模式，确保大文本内容滚动流畅
        self.message_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.message_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 确保列表项能够自动调整高度
        self.message_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        
        # 设置列表项的布局模式，确保内容完全显示
        self.message_list.setLayoutMode(QListWidget.LayoutMode.Batched)
        self.message_list.setBatchSize(10000)  # 增大批处理大小，减少布局更新次数
        
        layout.addWidget(self.message_list, stretch=1)
        
        # 创建浮动工具栏（初始隐藏）
        self._create_floating_toolbar()
        
        # 输入区域容器
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(10, 5, 10, 10)
        input_layout.setSpacing(5)
        
        # 文本处理功能区域
        text_processing_layout = QHBoxLayout()
        text_processing_layout.setSpacing(10)
        
        # 文本处理下拉菜单
        from PyQt6.QtWidgets import QComboBox
        self.text_processing_combo = QComboBox()
        self.text_processing_combo.setObjectName("textProcessingCombo")
        self.text_processing_combo.addItem("选择文本处理功能...", "")
        self.text_processing_combo.addItem("✨ 润色文本", "polish")
        self.text_processing_combo.addItem("📝 扩写内容", "expand")
        self.text_processing_combo.addItem("📋 缩写总结", "summarize")
        self.text_processing_combo.addItem("🌐 翻译为英文", "translate_en")
        self.text_processing_combo.addItem("🌐 翻译为中文", "translate_zh")
        text_processing_layout.addWidget(self.text_processing_combo)
        
        text_processing_layout.addStretch()
        input_layout.addLayout(text_processing_layout)
        
        # 消息输入框
        self.input_text = QTextEdit()
        self.input_text.setObjectName("inputText")
        self.input_text.setPlaceholderText("输入消息... (Enter 发送, Ctrl+Enter 换行)")
        self.input_text.setMaximumHeight(120)
        self.input_text.setMinimumHeight(60)
        input_layout.addWidget(self.input_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 字数统计标签
        self.char_count_label = QLabel("0 字")
        self.char_count_label.setObjectName("charCountLabel")
        button_layout.addWidget(self.char_count_label)
        
        button_layout.addStretch()
        
        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setObjectName("sendButton")
        self.send_button.setMinimumWidth(80)
        self.send_button.setMinimumHeight(32)
        button_layout.addWidget(self.send_button)
        
        input_layout.addLayout(button_layout)
        
        layout.addWidget(input_container)
        
        # 设置样式
        self.setStyleSheet("""
            QListWidget#messageList {
                background-color: #f5f5f5;
                border: none;
                outline: none;
            }
            
            QTextEdit#inputText {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            
            QTextEdit#inputText:focus {
                border: 1px solid #4CAF50;
            }
            
            QPushButton#sendButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton#sendButton:hover {
                background-color: #45a049;
            }
            
            QPushButton#sendButton:pressed {
                background-color: #3d8b40;
            }
            
            QPushButton#sendButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QLabel#charCountLabel {
                color: #666;
                font-size: 12px;
            }
        """)
    
    def _connect_signals(self) -> None:
        """连接信号槽"""
        # 发送按钮点击
        self.send_button.clicked.connect(self._on_send_clicked)
        
        # 输入框文本变化
        self.input_text.textChanged.connect(self._on_text_changed)
        
        # 文本处理功能选择
        self.text_processing_combo.currentIndexChanged.connect(self._on_text_processing_selected)
        
        # 为输入框安装事件过滤器
        self.input_text.installEventFilter(self)
    
    def _on_send_clicked(self) -> None:
        """发送按钮点击处理"""
        self.send_message()
    
    def _on_text_changed(self) -> None:
        """输入框文本变化处理"""
        # 更新字数统计
        text = self.input_text.toPlainText()
        char_count = len(text.strip())
        self.char_count_label.setText(f"{char_count} 字")
        
        # 更新发送按钮状态
        self.send_button.setEnabled(char_count > 0)
    
    def _on_text_processing_selected(self, index: int) -> None:
        """
        文本处理功能选择处理
        
        Args:
            index: 选中的索引
        """
        if index <= 0:
            return
        
        # 获取选中的功能
        function_type = self.text_processing_combo.itemData(index)
        
        # 获取当前输入框的文本
        current_text = self.input_text.toPlainText().strip()
        
        # 根据功能类型生成提示模板
        template = self._get_text_processing_template(function_type, current_text)
        
        # 填充到输入框
        self.input_text.setPlainText(template)
        
        # 重置下拉菜单
        self.text_processing_combo.setCurrentIndex(0)
        
        # 聚焦到输入框
        self.input_text.setFocus()
        
        logger.debug(f"应用文本处理模板: {function_type}")
    
    def resizeEvent(self, event) -> None:
        """
        窗口大小变化事件处理
        当窗口大小变化时，重新计算所有消息气泡的宽度
        """
        super().resizeEvent(event)
        
        # 重新计算所有消息气泡的宽度
        for i in range(self.message_list.count()):
            item = self.message_list.item(i)
            bubble = self.message_list.itemWidget(item)
            if hasattr(bubble, 'update_width'):
                bubble.update_width()
                
                # 调用MessageBubble的update_content方法，确保尺寸计算正确执行
                if hasattr(bubble, 'content'):
                    bubble.update_content(bubble.content.toPlainText()) if hasattr(bubble.content, 'toPlainText') else None
                
                # 更新列表项大小
                size_hint = bubble.sizeHint()
                item.setSizeHint(size_hint)
                # 使用size_hint的高度作为气泡的最小高度，确保气泡之间有足够的间距
                bubble.setMinimumHeight(size_hint.height())
        
        # 强制刷新整个消息列表的布局
        self.message_list.updateGeometry()
        self.message_list.viewport().update()
    
    def _get_text_processing_template(self, function_type: str, text: str) -> str:
        """
        获取文本处理提示模板
        
        Args:
            function_type: 功能类型
            text: 原始文本
            
        Returns:
            str: 提示模板
        """
        templates = {
            'polish': f"请帮我润色以下文本，使其更加流畅、专业：\n\n{text}",
            'expand': f"请帮我扩写以下内容，增加更多细节和说明：\n\n{text}",
            'summarize': f"请帮我总结以下内容，提取关键要点：\n\n{text}",
            'translate_en': f"请将以下文本翻译为英文：\n\n{text}",
            'translate_zh': f"请将以下文本翻译为中文：\n\n{text}",
        }
        
        return templates.get(function_type, text)
    
    def _create_floating_toolbar(self) -> None:
        """创建浮动工具栏"""
        self._floating_toolbar = QToolBar(self)
        self._floating_toolbar.setObjectName("floatingToolbar")
        self._floating_toolbar.setWindowFlags(
            Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint
        )
        self._floating_toolbar.hide()
        
        # 添加操作按钮
        polish_action = QAction("✨ 润色", self)
        polish_action.triggered.connect(lambda: self._apply_text_processing('polish'))
        self._floating_toolbar.addAction(polish_action)
        
        expand_action = QAction("📝 扩写", self)
        expand_action.triggered.connect(lambda: self._apply_text_processing('expand'))
        self._floating_toolbar.addAction(expand_action)
        
        summarize_action = QAction("📋 缩写", self)
        summarize_action.triggered.connect(lambda: self._apply_text_processing('summarize'))
        self._floating_toolbar.addAction(summarize_action)
        
        translate_action = QAction("🌐 翻译", self)
        translate_action.triggered.connect(lambda: self._apply_text_processing('translate_en'))
        self._floating_toolbar.addAction(translate_action)
        
        # 样式
        self._floating_toolbar.setStyleSheet("""
            QToolBar#floatingToolbar {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 2px;
            }
            
            QToolBar#floatingToolbar QToolButton {
                background-color: transparent;
                border: none;
                padding: 4px 8px;
                margin: 2px;
                border-radius: 3px;
            }
            
            QToolBar#floatingToolbar QToolButton:hover {
                background-color: #f0f0f0;
            }
        """)
    
    def _apply_text_processing(self, function_type: str) -> None:
        """
        应用文本处理功能到选中的文本
        
        Args:
            function_type: 功能类型
        """
        if not self._selected_text:
            return
        
        # 生成提示模板
        template = self._get_text_processing_template(function_type, self._selected_text)
        
        # 填充到输入框
        self.input_text.setPlainText(template)
        
        # 隐藏浮动工具栏
        self._floating_toolbar.hide()
        
        # 聚焦到输入框
        self.input_text.setFocus()
        
        logger.debug(f"应用文本处理到选中文本: {function_type}")
    
    def eventFilter(self, obj, event) -> bool:
        """
        事件过滤器，用于检测文本选择和处理输入框键盘事件
        
        Args:
            obj: 事件对象
            event: 事件
            
        Returns:
            bool: 是否处理了事件
        """
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QMouseEvent
        
        # 处理输入框的键盘事件
        # 首先检查 self.input_text 是否存在，避免初始化顺序问题
        if hasattr(self, 'input_text') and obj == self.input_text and event.type() == QEvent.Type.KeyPress:
            # Enter 键发送消息
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                if event.modifiers() != Qt.KeyboardModifier.ControlModifier:
                    self.send_message()
                    return True
                # Ctrl+Enter 换行，使用默认行为
                else:
                    return False
        
        # 处理消息列表的鼠标事件
        elif hasattr(self, 'message_list') and obj == self.message_list.viewport():
            if event.type() == QEvent.Type.MouseButtonRelease:
                # 检查是否有选中的文本
                self._check_text_selection()
        
        return super().eventFilter(obj, event)
    
    def _check_text_selection(self) -> None:
        """检查文本选择并显示浮动工具栏"""
        # 获取当前选中的项
        current_item = self.message_list.currentItem()
        if not current_item:
            self._floating_toolbar.hide()
            return
        
        # 获取项的组件
        widget = self.message_list.itemWidget(current_item)
        if not widget:
            self._floating_toolbar.hide()
            return
        
        # 尝试获取选中的文本（这里简化处理，实际需要更复杂的逻辑）
        # 由于 QLabel 不支持直接获取选中文本，这里使用简化方案
        # 在实际应用中，可能需要使用 QTextEdit 或其他支持文本选择的组件
        
        # 暂时隐藏工具栏（完整实现需要更复杂的文本选择检测）
        self._floating_toolbar.hide()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        键盘事件处理
        
        Args:
            event: 键盘事件
        """
        # 所有键盘事件现在通过eventFilter处理
        super().keyPressEvent(event)
    
    def send_message(self) -> None:
        """发送消息"""
        # 获取输入文本
        text = self.input_text.toPlainText().strip()
        
        if not text:
            logger.debug("消息为空，不发送")
            return
        
        logger.info(f"用户输入: {text}")
        
        # 发送信号
        self.message_sent.emit(text)
        
        # 清空输入框
        self.input_text.clear()
        
        # 重置字数统计
        self.char_count_label.setText("0 字")
    
    def clear_messages(self) -> None:
        """清空消息列表"""
        # 停止流式响应定时器
        if self._update_timer.isActive():
            self._update_timer.stop()
        
        # 清空流式响应相关引用
        self._streaming_bubble = None
        self._streaming_item = None
        self._streaming_buffer.clear()
        self._typing_indicator_item = None
        
        # 清空消息列表
        self.message_list.clear()
        logger.debug("清空消息列表")
    
    def set_input_enabled(self, enabled: bool) -> None:
        """
        设置输入框和发送按钮是否可用
        
        Args:
            enabled: 是否可用
        """
        self.input_text.setEnabled(enabled)
        self.send_button.setEnabled(enabled and len(self.input_text.toPlainText().strip()) > 0)
    
    def get_message_list(self) -> QListWidget:
        """
        获取消息列表组件
        
        Returns:
            QListWidget: 消息列表组件
        """
        return self.message_list
    
    def add_user_message(self, content: str, timestamp: Optional[str] = None) -> None:
        """
        添加用户消息
        
        Args:
            content: 消息内容
            timestamp: 时间戳，如果为 None 则使用当前时间
        """
        logger.info(f"=== 开始添加用户消息 ===")
        logger.info(f"消息内容: {content[:50]}{'...' if len(content) > 50 else ''}")
        logger.info(f"消息列表当前尺寸: 宽度={self.message_list.width()}, 高度={self.message_list.height()}")
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 创建消息气泡
        bubble = MessageBubble('user', content, timestamp)
        logger.info(f"创建用户气泡完成，初始尺寸: {bubble.sizeHint().width()}x{bubble.sizeHint().height()}")
        
        # 创建列表项
        item = QListWidgetItem(self.message_list)
        
        # 添加到列表
        self.message_list.addItem(item)
        self.message_list.setItemWidget(item, bubble)
        logger.info(f"气泡添加到列表完成")
        
        # 强制更新大小 - 使用QTimer延迟更新以确保布局完成
        from PyQt6.QtCore import QTimer
        def update_size():
            logger.info(f"开始更新消息大小，角色: {bubble.role}, 当前气泡尺寸: {bubble.size()}")
            
            # 先更新气泡宽度，确保使用最新的父容器宽度计算
            if hasattr(bubble, 'update_width'):
                bubble.update_width()
                logger.info(f"已更新消息气泡宽度")
            
            # 调用MessageBubble的update_content方法，确保尺寸计算和日志记录正确执行
            bubble.update_content(content)
            
            # 获取调整后的大小提示
            size_hint = bubble.sizeHint()
            logger.info(f"气泡调整后sizeHint: {size_hint}")
            
            # 设置列表项的大小
            item.setSizeHint(size_hint)
            logger.info(f"列表项大小更新完成，新尺寸: {size_hint}")
            
            # 强制刷新整个消息列表的布局
            self.message_list.updateGeometry()
            self.message_list.viewport().update()
            
            # 滚动到底部，确保最新内容可见
            self.message_list.scrollToBottom()
            logger.info(f"消息列表布局已强制刷新并滚动到底部")
        
        # 增加延迟时间，确保气泡完全渲染
        QTimer.singleShot(200, update_size)
        
        logger.info(f"=== 用户消息添加完成 ===")
    
    def add_assistant_message(self, content: str, timestamp: Optional[str] = None, 
                             original_text: Optional[str] = None) -> None:
        """
        添加 AI 消息
        
        Args:
            content: 消息内容
            timestamp: 时间戳，如果为 None 则使用当前时间
            original_text: 原始文本（用于差异对比），如果提供则显示"查看差异"按钮
        """
        logger.info(f"=== 开始添加AI助手消息 ===")
        logger.info(f"消息内容: {content[:50]}{'...' if len(content) > 50 else ''}")
        logger.info(f"消息列表当前尺寸: 宽度={self.message_list.width()}, 高度={self.message_list.height()}")
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 创建消息气泡
        bubble = MessageBubble('assistant', content, timestamp)
        logger.info(f"创建AI气泡完成，初始尺寸: {bubble.sizeHint().width()}x{bubble.sizeHint().height()}")
        
        # 如果提供了原始文本，启用差异查看
        if original_text:
            bubble.enable_diff_view(original_text)
            # 连接差异查看信号
            bubble.view_diff_requested.connect(self._show_text_diff)
            logger.info(f"气泡差异查看功能已启用")
        
        # 创建列表项
        item = QListWidgetItem(self.message_list)
        
        # 添加到列表
        self.message_list.addItem(item)
        self.message_list.setItemWidget(item, bubble)
        logger.info(f"气泡添加到列表完成")
        
        # 强制更新大小 - 使用QTimer延迟更新以确保布局完成
        from PyQt6.QtCore import QTimer
        def update_size():
            logger.info(f"开始更新AI气泡尺寸，当前气泡尺寸: {bubble.sizeHint().width()}x{bubble.sizeHint().height()}")
            
            # 先更新气泡宽度，确保使用最新的父容器宽度计算
            if hasattr(bubble, 'update_width'):
                bubble.update_width()
                logger.info(f"已更新AI消息气泡宽度")
            
            # 调用MessageBubble的update_content方法，确保尺寸计算和日志记录正确执行
            bubble.update_content(content)
            
            # 再获取调整后的大小提示
            size_hint = bubble.sizeHint()
            logger.info(f"气泡调整后sizeHint: {size_hint}")
            
            # 确保获取到的尺寸足够大
            min_height = 40  # 最小高度
            if size_hint.height() < min_height:
                size_hint.setHeight(min_height)
                logger.info(f"调整sizeHint高度到最小高度: {min_height}")
            
            # 设置列表项的大小
            # 使用sizeHint高度而不是实际高度，确保列表项高度与气泡内部计算的合适高度一致
            item.setSizeHint(size_hint)
            logger.info(f"更新AI消息列表项大小: {size_hint} (使用sizeHint高度)")
            
            # 强制刷新整个消息列表的布局
            self.message_list.updateGeometry()
            self.message_list.viewport().update()
            logger.info(f"消息列表布局已强制刷新")
            
            # 滚动到底部，确保最新内容可见
            self.message_list.scrollToBottom()
            logger.info(f"消息列表已滚动到底部")
        
        # 增加延迟时间，确保气泡完全渲染
        QTimer.singleShot(200, update_size)
        
        logger.info(f"=== AI助手消息添加完成 ===")
    
    def show_typing_indicator(self) -> None:
        """显示正在输入指示器"""
        # 如果已经有指示器，不重复添加
        if self._typing_indicator_item is not None:
            return
        
        # 创建正在输入指示器
        indicator = TypingIndicator()
        
        # 创建列表项
        item = QListWidgetItem(self.message_list)
        item.setSizeHint(indicator.sizeHint())
        
        # 添加到列表
        self.message_list.addItem(item)
        self.message_list.setItemWidget(item, indicator)
        
        # 保存引用
        self._typing_indicator_item = item
        
        # 滚动到底部
        self.message_list.scrollToBottom()
        
        logger.debug("显示正在输入指示器")
    
    def hide_typing_indicator(self) -> None:
        """隐藏正在输入指示器"""
        if self._typing_indicator_item is None:
            return
        
        # 从列表中移除
        row = self.message_list.row(self._typing_indicator_item)
        if row >= 0:
            self.message_list.takeItem(row)
        
        # 清空引用
        self._typing_indicator_item = None
        
        logger.debug("隐藏正在输入指示器")
    
    def start_streaming_response(self, timestamp: Optional[str] = None) -> None:
        """
        开始流式响应
        
        Args:
            timestamp: 时间戳，如果为 None 则使用当前时间
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 如果已经有流式响应在进行，先完成它
        if self._streaming_bubble is not None or self._update_timer.isActive():
            logger.warning("检测到未完成的流式响应，先完成它")
            self.finish_streaming_response()
        
        # 隐藏正在输入指示器
        self.hide_typing_indicator()
        
        # 创建初始的空消息气泡
        self._streaming_bubble = MessageBubble('assistant', '', timestamp)
        
        # 创建列表项
        self._streaming_item = QListWidgetItem(self.message_list)
        self._streaming_item.setSizeHint(self._streaming_bubble.sizeHint())
        
        # 添加到列表
        self.message_list.addItem(self._streaming_item)
        self.message_list.setItemWidget(self._streaming_item, self._streaming_bubble)
        
        # 清空缓冲区
        self._streaming_buffer = []
        
        # 启动定时器（每 100ms 更新一次）
        self._update_timer.start(100)
        
        logger.debug("开始流式响应")
    
    def append_streaming_chunk(self, chunk: str) -> None:
        """
        追加流式响应文本块
        
        Args:
            chunk: 文本块
        """
        if self._streaming_bubble is None:
            logger.warning("流式响应未开始，忽略文本块")
            return
        
        # 添加到缓冲区
        self._streaming_buffer.append(chunk)
    
    def _flush_streaming_buffer(self) -> None:
        """刷新流式响应缓冲区"""
        if not self._streaming_buffer or self._streaming_bubble is None:
            return
        
        # 检查对象是否仍然有效
        try:
            # 尝试访问对象，如果已删除会抛出 RuntimeError
            _ = self._streaming_bubble.layout()
        except RuntimeError:
            # 对象已被删除，停止定时器并清理
            self._update_timer.stop()
            self._streaming_bubble = None
            self._streaming_item = None
            self._streaming_buffer.clear()
            return
        
        # 合并缓冲区内容
        chunk = ''.join(self._streaming_buffer)
        self._streaming_buffer.clear()
        
        # 更新气泡内容
        current_content = self._streaming_bubble.content.toPlainText() if hasattr(self._streaming_bubble.content, 'toPlainText') else str(self._streaming_bubble.content)
        new_content = current_content + chunk
        self._streaming_bubble.update_content(new_content)
        
        # 流式响应过程中跳过尺寸更新，将在响应结束后统一处理
        logger.debug(f"[流式响应] 更新内容长度: {len(new_content)}，跳过尺寸调整")
        
        # 滚动到底部
        self.message_list.scrollToBottom()
    
    def finish_streaming_response(self) -> None:
        """完成流式响应"""
        print(f"[DEBUG] [完成响应] finish_streaming_response方法被调用")
        # 停止定时器
        self._update_timer.stop()
        
        # 刷新剩余缓冲区
        self._flush_streaming_buffer()
        
        # 在响应结束后进行最终的尺寸调整
        if self._streaming_bubble and self._streaming_item:
            print(f"[DEBUG] [完成响应] 检测到_streaming_bubble和_streaming_item，准备设置最终尺寸调整")
            # 保存当前引用，避免定时器回调时引用已被清除
            bubble_ref = self._streaming_bubble
            item_ref = self._streaming_item
            
            def final_size_update():
                """流式响应结束后执行最终的尺寸调整"""
                print(f"[DEBUG] [流式响应完成] 开始最终尺寸调整，气泡对象: {bubble_ref}, 列表项: {item_ref}")
                logger.info(f"[详细调试] [流式响应完成] 开始最终尺寸调整，气泡对象: {bubble_ref}, 列表项: {item_ref}")
                try:
                    # 检查对象是否仍然有效
                    _ = bubble_ref.layout()
                    
                    # 记录初始状态
                    initial_size_hint = bubble_ref.sizeHint()
                    initial_actual_size = bubble_ref.size()
                    print(f"[DEBUG] [流式响应完成] 初始状态 - sizeHint: {initial_size_hint}, actual size: {initial_actual_size}")
                    logger.info(f"[详细调试] [流式响应完成] 初始状态 - sizeHint: {initial_size_hint}, actual size: {initial_actual_size}")
                    
                    # 第一步：强制气泡组件本身执行完整的尺寸计算
                    bubble_ref.updateGeometry()
                    bubble_ref.adjustSize()
                    after_adjust_size = bubble_ref.size()
                    print(f"[DEBUG] [流式响应完成] 气泡组件初步调整后尺寸: {after_adjust_size}")
                    logger.info(f"[详细调试] [流式响应完成] 气泡组件初步调整后尺寸: {after_adjust_size}")
                    
                    # 第二步：使用sizeHint方法获取气泡的完整高度（包括所有边距）
                    size_hint = bubble_ref.sizeHint()
                    print(f"[DEBUG] [流式响应完成] 使用sizeHint获取的完整高度: {size_hint}")
                    logger.info(f"[详细调试] [流式响应完成] 使用sizeHint获取的完整高度: {size_hint}")
                    
                    # 设置气泡的最小高度为sizeHint的高度，确保所有边距都被包含
                    bubble_ref.setMinimumHeight(size_hint.height())
                    print(f"[DEBUG] [流式响应完成] 使用sizeHint高度设置气泡最小高度: {size_hint.height()}")
                    logger.info(f"[详细调试] [流式响应完成] 使用sizeHint高度设置气泡最小高度: {size_hint.height()}")
                    
                    # 第三步：让气泡组件内部的最终调整逻辑重新执行
                    # 这会触发message_bubble内部的尺寸计算
                    if hasattr(bubble_ref, 'content') and hasattr(bubble_ref.content, 'toPlainText'):
                        current_content = bubble_ref.content.toPlainText()
                        print(f"[DEBUG] [流式响应完成] 准备重新触发尺寸计算，当前内容长度: {len(current_content)}, 行数: {current_content.count(chr(10)) + 1}")
                        logger.info(f"[详细调试] [流式响应完成] 准备重新触发尺寸计算，当前内容长度: {len(current_content)}, 行数: {current_content.count(chr(10)) + 1}")
                        bubble_ref.update_content(current_content)  # 用相同内容触发完整尺寸计算
                    print(f"[DEBUG] [流式响应完成] 重新触发气泡组件的尺寸计算完成")
                    logger.info(f"[详细调试] [流式响应完成] 重新触发气泡组件的尺寸计算完成")
                    
                    # 第四步：获取气泡组件的sizeHint，确保内容完整显示
                    size_hint = bubble_ref.sizeHint()
                    print(f"[DEBUG] [流式响应完成] 使用sizeHint获取的完整尺寸: {size_hint}")
                    logger.info(f"[详细调试] [流式响应完成] 使用sizeHint获取的完整尺寸: {size_hint}")
                    
                    # 第五步：设置列表项大小为气泡的sizeHint
                    # 直接使用气泡的sizeHint，确保所有边距都被包含
                    item_ref.setSizeHint(size_hint)
                    print(f"[DEBUG] [流式响应完成] 更新列表项大小: {size_hint} (使用sizeHint)")
                    logger.info(f"[详细调试] [流式响应完成] 更新列表项大小: {size_hint} (使用sizeHint)")
                    
                    # 第六步：强制刷新整个消息列表的布局
                    self.message_list.viewport().update()
                    self.message_list.updateGeometry()
                    self.message_list.layout().invalidate()
                    self.message_list.layout().update()
                    print(f"[DEBUG] [流式响应完成] 消息列表布局已强制刷新")
                    logger.info(f"[详细调试] [流式响应完成] 消息列表布局已强制刷新")
                    
                    # 第七步：再次调整气泡大小和列表项大小，确保所有尺寸更新都生效
                    bubble_ref.updateGeometry()
                    bubble_ref.adjustSize()
                    final_size_hint = bubble_ref.sizeHint()
                    item_ref.setSizeHint(final_size_hint)
                    print(f"[DEBUG] [流式响应完成] 再次确认并更新列表项大小: {final_size_hint}")
                    logger.info(f"[详细调试] [流式响应完成] 再次确认并更新列表项大小: {final_size_hint}")
                    
                    # 记录最终状态
                    final_actual_size = bubble_ref.size()
                    print(f"[DEBUG] [流式响应完成] 最终状态 - sizeHint: {final_size_hint}, actual size: {final_actual_size}, 列表项大小: {item_ref.sizeHint()}")
                    logger.info(f"[详细调试] [流式响应完成] 最终状态 - sizeHint: {final_size_hint}, actual size: {final_actual_size}, 列表项大小: {item_ref.sizeHint()}")
                    
                    # 最后滚动到底部确保完整显示
                    self.message_list.scrollToBottom()
                    print(f"[DEBUG] [流式响应完成] 已滚动到底部")
                    logger.info(f"[详细调试] [流式响应完成] 已滚动到底部")
                except RuntimeError:
                    # 对象已被删除，跳过尺寸调整
                    print(f"[DEBUG] [流式响应完成] 对象已被删除，跳过尺寸调整")
                    logger.debug(f"[详细调试] [流式响应完成] 对象已被删除，跳过尺寸调整")
                
                print(f"[DEBUG] [流式响应完成] 最终尺寸调整完成")
                logger.info(f"[详细调试] [流式响应完成] 最终尺寸调整完成")
            
            # 使用更长的延迟时间(1000ms)，确保message_bubble内部的定时器先完成调整
            # 解决只有最后一个气泡显示不全的问题
            from PyQt6.QtCore import QTimer
            print(f"[DEBUG] [完成响应] 设置1000ms定时器执行final_size_update")
            QTimer.singleShot(1000, final_size_update)
        
        # 清空引用
        self._streaming_bubble = None
        self._streaming_item = None
        
        logger.debug("完成流式响应")
    
    def load_messages(self, messages: list, rollback_point: Optional[int] = None) -> None:
        """
        加载消息列表
        
        Args:
            messages: 消息列表，每个消息包含 role, content, timestamp
            rollback_point: 回滚点序号，如果不为 None 则应用回滚效果
        """
        # 清空当前消息
        self.clear_messages()
        
        # 添加所有消息
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            # 格式化时间戳（如果是 ISO 格式）
            if 'T' in timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%H:%M:%S")
                except:
                    pass
            
            if role == 'user':
                self.add_user_message(content, timestamp)
            else:
                self.add_assistant_message(content, timestamp)
        
        # 如果有回滚点，应用回滚效果
        if rollback_point is not None:
            self.apply_rollback(rollback_point)
        
        logger.info(f"加载 {len(messages)} 条消息")
    
    def add_tool_call_start(self, tool_name: str, input_str: str) -> None:
        """
        添加工具调用开始
        
        Args:
            tool_name: 工具名称
            input_str: 工具输入参数
        """
        # 创建工具调用组件
        tool_widget = ToolCallWidget(tool_name, input_str)
        
        # 创建列表项
        item = QListWidgetItem(self.message_list)
        item.setSizeHint(tool_widget.sizeHint())
        
        # 添加到列表
        self.message_list.addItem(item)
        self.message_list.setItemWidget(item, tool_widget)
        
        # 保存引用
        self._active_tool_widgets[tool_name] = (item, tool_widget)
        
        # 滚动到底部
        self.message_list.scrollToBottom()
        
        logger.debug(f"添加工具调用开始: {tool_name}")
    
    def add_tool_call_finish(self, tool_name: str, output_str: str) -> None:
        """
        添加工具调用完成
        
        Args:
            tool_name: 工具名称
            output_str: 工具输出结果
        """
        # 查找对应的工具调用组件
        if tool_name in self._active_tool_widgets:
            item, tool_widget = self._active_tool_widgets[tool_name]
            
            # 更新输出结果
            tool_widget.set_output(output_str)
            
            # 更新列表项大小
            item.setSizeHint(tool_widget.sizeHint())
            
            # 从活动列表中移除
            del self._active_tool_widgets[tool_name]
            
            # 滚动到底部
            self.message_list.scrollToBottom()
            
            logger.debug(f"添加工具调用完成: {tool_name}")
        else:
            logger.warning(f"未找到工具调用开始记录: {tool_name}")
    
    def _show_message_context_menu(self, pos: QPoint) -> None:
        """
        显示消息右键菜单
        
        Args:
            pos: 鼠标位置
        """
        # 获取点击的项
        item = self.message_list.itemAt(pos)
        if not item:
            return
        
        # 获取项的索引
        row = self.message_list.row(item)
        
        # 获取项的组件
        widget = self.message_list.itemWidget(item)
        if not widget or not isinstance(widget, MessageBubble):
            return
        
        # 创建上下文菜单
        menu = QMenu(self)
        
        # 添加"回滚到此处"选项
        rollback_action = QAction("🔄 回滚到此处", self)
        rollback_action.triggered.connect(lambda: self._request_rollback(row))
        menu.addAction(rollback_action)
        
        # 显示菜单
        menu.exec(self.message_list.mapToGlobal(pos))
    
    def _request_rollback(self, message_index: int) -> None:
        """
        请求回滚到指定消息
        
        Args:
            message_index: 消息索引（在列表中的位置）
        """
        # 显示确认对话框
        reply = QMessageBox.question(
            self,
            "确认回滚",
            f"确定要回滚到第 {message_index + 1} 条消息吗？\n\n"
            "此操作将标记该消息之后的所有消息为半透明显示，"
            "表示这些消息已被回滚。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 发出回滚请求信号
            self.rollback_requested.emit(message_index)
            logger.info(f"请求回滚到消息索引: {message_index}")
    
    def apply_rollback(self, rollback_index: int) -> None:
        """
        应用回滚效果（将指定索引之后的消息设置为半透明）
        
        Args:
            rollback_index: 回滚点索引
        """
        total_items = self.message_list.count()
        
        # 将回滚点之后的所有消息设置为半透明
        for i in range(rollback_index + 1, total_items):
            item = self.message_list.item(i)
            if not item:
                continue
            
            widget = self.message_list.itemWidget(item)
            if widget and isinstance(widget, MessageBubble):
                # 设置半透明效果
                widget.setStyleSheet(widget.styleSheet() + "\nQWidget { opacity: 0.5; }")
                widget.setEnabled(False)  # 禁用交互
        
        logger.info(f"应用回滚效果: 从索引 {rollback_index + 1} 到 {total_items - 1}")
    
    def clear_rollback_effect(self) -> None:
        """清除所有回滚效果"""
        total_items = self.message_list.count()
        
        for i in range(total_items):
            item = self.message_list.item(i)
            if not item:
                continue
            
            widget = self.message_list.itemWidget(item)
            if widget and isinstance(widget, MessageBubble):
                # 恢复正常状态
                widget.setEnabled(True)
                # 重新应用原始样式（移除 opacity 设置）
                original_style = widget.styleSheet().replace("\nQWidget { opacity: 0.5; }", "")
                widget.setStyleSheet(original_style)
        
        logger.debug("清除所有回滚效果")
    
    def load_session_messages(self, session_data: dict) -> None:
        """
        加载会话消息（从会话数据）
        
        Args:
            session_data: 会话数据字典，包含 messages 和 rollback_point
        """
        messages = session_data.get('messages', [])
        rollback_point = session_data.get('rollback_point')
        
        self.load_messages(messages, rollback_point)
        
        logger.info(f"从会话数据加载消息，回滚点: {rollback_point}")
    
    def _show_text_diff(self, original_text: str, modified_text: str) -> None:
        """
        显示文本差异对比
        
        Args:
            original_text: 原始文本
            modified_text: 修改后的文本
        """
        show_text_diff(original_text, modified_text, self)
        logger.info("显示文本差异对比")
