"""
消息气泡组件

提供用户和 AI 消息的不同样式展示。
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QTextOption

logger = logging.getLogger(__name__)


class MessageBubble(QWidget):
    """消息气泡组件"""
    
    # 信号定义
    view_diff_requested = pyqtSignal(str, str)  # original_text, modified_text
    
    def __init__(self, role: str, content: str, timestamp: str = "",
                 parent: Optional[QWidget] = None):
        """
        初始化消息气泡组件
        
        Args:
            role: 消息角色 ('user' 或 'assistant')
            content: 消息内容
            timestamp: 时间戳
            parent: 父组件
        """
        super().__init__(parent)
        
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.original_text = None  # 用于存储原始文本（用于对比）
        self.diff_button = None  # 差异按钮引用
        
        self._init_ui()
        
        logger.debug(f"MessageBubble 创建: role={role}, content={content[:30]}...")
    
    def _init_ui(self) -> None:
        """初始化 UI"""
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        
        # 根据角色设置对齐方式
        if self.role == 'user':
            # 用户消息：右对齐
            main_layout.addStretch()
            bubble_widget = self._create_user_bubble()
            main_layout.addWidget(bubble_widget)
        else:
            # AI 消息：左对齐
            bubble_widget = self._create_assistant_bubble()
            main_layout.addWidget(bubble_widget)
            main_layout.addStretch()
    
    def _create_user_bubble(self) -> QWidget:
        """
        创建用户消息气泡
        
        Returns:
            QWidget: 用户消息气泡组件
        """
        bubble = QWidget()
        bubble.setObjectName("userBubble")
        # 移除最大宽度限制，让气泡可以根据内容自适应宽度
        # bubble.setMaximumWidth(500)
        # 设置大小策略，允许高度完全自适应
        bubble.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # 消息内容
        content_edit = QTextEdit()
        content_edit.setObjectName("userContent")
        content_edit.setReadOnly(True)
        content_edit.setPlainText(self.content)
        # 设置换行模式为仅在单词边界换行，避免在单词中间换行
        content_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        # 设置自动换行模式，根据窗口大小自动换行
        content_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        content_edit.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        # 隐藏滚动条
        content_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 设置大小策略，允许高度完全自适应内容
        content_edit.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        # 设置对齐方式
        content_edit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        # 设置缩进和边距
        content_edit.setContentsMargins(0, 0, 0, 0)
        # 设置最小高度
        content_edit.setMinimumHeight(20)
        # 调整文档边距
        content_edit.document().setDocumentMargin(0)
        layout.addWidget(content_edit)
        
        # 时间戳
        if self.timestamp:
            time_label = QLabel(self.timestamp)
            time_label.setObjectName("userTimestamp")
            time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(time_label)
        
        # 样式
        bubble.setStyleSheet("""
            QWidget#userBubble {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #42A5F5, stop:1 #2196F3);
                border-radius: 12px;
                padding: 2px;
            }
            
            QLabel#userContent, QTextEdit#userContent {
                color: white;
                font-size: 14px;
                background: transparent;
                padding: 2px;
                border: none;
                outline: none;
            }
            
            QLabel#userTimestamp {
                color: rgba(255, 255, 255, 0.8);
                font-size: 10px;
                background: transparent;
                padding: 2px;
            }
        """)
        
        return bubble
    
    def _create_assistant_bubble(self) -> QWidget:
        """
        创建 AI 消息气泡
        
        Returns:
            QWidget: AI 消息气泡组件
        """
        bubble = QWidget()
        bubble.setObjectName("assistantBubble")
        # 移除最大宽度限制，让气泡可以根据内容自适应宽度
        # bubble.setMaximumWidth(500)
        # 设置大小策略，允许高度完全自适应
        bubble.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # AI 标识
        ai_label = QLabel("🤖 AI Assistant")
        ai_label.setObjectName("aiLabel")
        layout.addWidget(ai_label)
        
        # 消息内容
        content_edit = QTextEdit()
        content_edit.setObjectName("assistantContent")
        content_edit.setReadOnly(True)
        content_edit.setPlainText(self.content)
        content_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        content_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        content_edit.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        # 隐藏滚动条
        content_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 设置大小策略，允许高度完全自适应内容
        content_edit.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        # 设置对齐方式
        content_edit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        # 设置缩进和边距
        content_edit.setContentsMargins(0, 0, 0, 0)
        # 设置最小高度
        content_edit.setMinimumHeight(20)
        # 调整文档边距
        content_edit.document().setDocumentMargin(0)
        layout.addWidget(content_edit)
        
        # 底部区域（时间戳和按钮）
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)
        
        # 时间戳
        if self.timestamp:
            time_label = QLabel(self.timestamp)
            time_label.setObjectName("assistantTimestamp")
            time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            bottom_layout.addWidget(time_label)
        
        bottom_layout.addStretch()
        
        # 差异按钮（初始隐藏）
        self.diff_button = QPushButton("📊 查看差异")
        self.diff_button.setObjectName("diffButton")
        self.diff_button.setVisible(False)
        self.diff_button.clicked.connect(self._on_view_diff_clicked)
        bottom_layout.addWidget(self.diff_button)
        
        layout.addLayout(bottom_layout)
        
        # 样式
        bubble.setStyleSheet("""
            QWidget#assistantBubble {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 2px;
            }
            
            QLabel#aiLabel {
                color: #2196F3;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                padding: 2px;
            }
            
            QLabel#assistantContent, QTextEdit#assistantContent {
                color: #212121;
                font-size: 14px;
                background: transparent;
                padding: 2px;
                border: none;
                outline: none;
            }
            
            QLabel#assistantTimestamp {
                color: #9e9e9e;
                font-size: 10px;
                background: transparent;
                padding: 2px;
            }
            
            QPushButton#diffButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: bold;
            }
            
            QPushButton#diffButton:hover {
                background-color: #1976D2;
            }
            
            QPushButton#diffButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        return bubble
    
    def update_content(self, content: str) -> None:
        """
        更新消息内容（用于流式响应）
        
        Args:
            content: 新的消息内容
        """
        self.content = content
        
        # 更高效的更新方式：只更新内容，不重新构建整个 UI
        # 获取布局中的气泡组件
        layout = self.layout()
        bubble_widget = None
        
        if self.role == 'user':
            # 用户消息：布局结构是 [stretch, bubble]
            if layout.count() >= 2:
                bubble_widget = layout.itemAt(1).widget()
        else:
            # AI 消息：布局结构是 [bubble, stretch]
            if layout.count() >= 2:
                bubble_widget = layout.itemAt(0).widget()
        
        if bubble_widget:
            # 在气泡组件中找到内容组件并更新
            for i in range(bubble_widget.layout().count()):
                child = bubble_widget.layout().itemAt(i)
                widget = child.widget()
                if widget:
                    if isinstance(widget, QLabel) and widget.objectName() in ["userContent", "assistantContent"]:
                        # 更新QLabel内容
                        widget.setText(content)
                        # 强制重新计算尺寸
                        widget.adjustSize()
                        bubble_widget.adjustSize()
                        break
                    elif isinstance(widget, QTextEdit) and widget.objectName() in ["userContent", "assistantContent"]:
                        # 更新QTextEdit内容
                        # 保存当前光标位置
                        cursor = widget.textCursor()
                        
                        # 更新内容
                        widget.setPlainText(content)
                        
                        # 恢复光标位置
                        widget.setTextCursor(cursor)
                        
                        # 调整文档大小
                        widget.document().adjustSize()
                        
                        # 获取文档的实际宽度
                        doc_width = widget.document().size().width()
                        
                        # 设置QTextEdit的最小宽度为文档宽度
                        widget.setMinimumWidth(int(doc_width))
                        
                        # 调整QTextEdit大小
                        widget.adjustSize()
                        bubble_widget.adjustSize()
                        break
        else:
            # 如果找不到气泡组件，回退到重新构建 UI 的方式
            # 清空当前布局
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # 重新创建气泡
            if self.role == 'user':
                layout.addStretch()
                bubble_widget = self._create_user_bubble()
                layout.addWidget(bubble_widget)
            else:
                bubble_widget = self._create_assistant_bubble()
                layout.addWidget(bubble_widget)
                layout.addStretch()
    
    def enable_diff_view(self, original_text: str) -> None:
        """
        启用差异查看功能
        
        Args:
            original_text: 原始文本（修改前的文本）
        """
        if self.role != 'assistant':
            logger.warning("只有 AI 消息才能启用差异查看")
            return
        
        self.original_text = original_text
        
        # 显示差异按钮
        if self.diff_button:
            self.diff_button.setVisible(True)
            logger.debug("启用差异查看按钮")
    
    def _on_view_diff_clicked(self) -> None:
        """处理查看差异按钮点击"""
        if self.original_text is None:
            logger.warning("没有原始文本，无法查看差异")
            return
        
        # 发出查看差异信号
        self.view_diff_requested.emit(self.original_text, self.content)
        logger.info("请求查看文本差异")
    
    def sizeHint(self) -> QSize:
        """
        自定义大小提示，确保消息气泡正确计算高度和宽度
        """
        # 获取气泡组件
        layout = self.layout()
        bubble_widget = None
        
        if self.role == 'user':
            # 用户消息：布局结构是 [stretch, bubble]
            if layout.count() >= 2:
                bubble_widget = layout.itemAt(1).widget()
        else:
            # AI 消息：布局结构是 [bubble, stretch]
            if layout.count() >= 2:
                bubble_widget = layout.itemAt(0).widget()
        
        if bubble_widget:
            # 先让气泡组件自身调整大小
            bubble_widget.adjustSize()
            
            # 计算气泡内部内容的实际高度
            content_height = 0
            max_content_width = 0
            
            for i in range(bubble_widget.layout().count()):
                item = bubble_widget.layout().itemAt(i)
                widget = item.widget()
                if widget:
                    # 获取组件的大小提示
                    size_hint = widget.sizeHint()
                    
                    if isinstance(widget, QTextEdit):
                        # 对于QTextEdit，确保文档已更新
                        widget.document().adjustSize()
                        # 使用文档高度和宽度
                        doc_size = widget.document().size()
                        content_height += doc_size.height()
                        max_content_width = max(max_content_width, doc_size.width())
                    else:
                        # 对于其他组件，使用其大小提示
                        content_height += size_hint.height()
                        max_content_width = max(max_content_width, size_hint.width())
            
            # 考虑布局的边距和间距
            margins = bubble_widget.layout().contentsMargins()
            content_height += margins.top() + margins.bottom()
            content_height += (bubble_widget.layout().count() - 1) * bubble_widget.layout().spacing()
            
            max_content_width += margins.left() + margins.right()
            
            # 设置最小宽度，确保内容不会被过度压缩
            min_width = 200
            max_content_width = max(max_content_width, min_width)
            
            # 确保高度至少满足最小要求
            min_height = 40  # 最小高度
            content_height = max(content_height, min_height)
            
            # 返回计算后的大小（转换为int类型）
            return QSize(int(max_content_width), int(content_height))
        
        # 如果找不到气泡组件，返回默认大小
        return QSize(200, 40)


class TypingIndicator(QWidget):
    """正在输入指示器"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化正在输入指示器
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        self._init_ui()
        
        logger.debug("TypingIndicator 创建")
    
    def _init_ui(self) -> None:
        """初始化 UI"""
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        
        # 左对齐
        bubble = QWidget()
        bubble.setObjectName("typingBubble")
        bubble.setMaximumWidth(150)
        
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # AI 标识
        ai_label = QLabel("🤖 AI Assistant")
        ai_label.setObjectName("aiLabel")
        layout.addWidget(ai_label)
        
        # 正在输入文本
        typing_label = QLabel("正在输入...")
        typing_label.setObjectName("typingText")
        layout.addWidget(typing_label)
        
        main_layout.addWidget(bubble)
        main_layout.addStretch()
        
        # 样式
        bubble.setStyleSheet("""
            QWidget#typingBubble {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
            }
            
            QLabel#aiLabel {
                color: #4CAF50;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
            }
            
            QLabel#typingText {
                color: #999;
                font-size: 14px;
                font-style: italic;
                background: transparent;
            }
        """)
