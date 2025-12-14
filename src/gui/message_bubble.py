"""
消息气泡组件

提供用户和 AI 消息的不同样式展示。
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
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
        
        # 流式响应相关属性
        self.is_streaming = False
        self._streaming_content = ""
        
        logger.info(f"=== 开始初始化消息气泡 ({self.role}) ===")
        logger.info(f"父容器信息: {type(parent).__name__ if parent else '无'}, 宽度: {parent.width() if parent else '无'}")
        logger.info(f"初始内容: {content[:50]}{'...' if len(content) > 50 else ''}")
        
        self._init_ui()
        
        logger.info(f"=== MessageBubble 初始化完成 ({self.role}) ===")
        logger.info(f"气泡初始尺寸: {self.sizeHint().width()}x{self.sizeHint().height()}")
        logger.debug(f"MessageBubble 创建: role={role}, content={content[:30]}...")
    
    def _init_ui(self) -> None:
        """
        初始化UI
        """
        # 设置尺寸策略，确保高度根据内容自适应
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
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
        # 设置最大宽度为父容器宽度的80%，允许气泡自适应页面宽度
        max_width = int(self.parent().width() * 0.8) if self.parent() else 800
        bubble.setMaximumWidth(max_width)
        logger.info(f"初始化用户气泡宽度: {max_width}, 父容器宽度: {self.parent().width() if self.parent() else '无'}")
        
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # 消息内容
        content_edit = QTextEdit()
        content_edit.setObjectName("userContent")
        content_edit.setReadOnly(True)
        content_edit.setPlainText(self.content)
        # 更新self.content为QTextEdit组件
        self.content = content_edit
        logger.info(f"创建内容编辑框，初始内容: {content_edit.toPlainText()}")
        
        # 设置换行模式为仅在单词边界换行，避免在单词中间换行
        content_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        logger.info(f"设置换行模式: {content_edit.wordWrapMode()}")
        
        # 设置自动换行模式，根据窗口大小自动换行
        content_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        logger.info(f"设置自动换行模式: {content_edit.lineWrapMode()}")
        
        content_edit.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        
        # 禁用垂直滚动条，让内容完全展开
        content_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 设置对齐方式
        content_edit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # 设置缩进和边距
        content_edit.setContentsMargins(0, 0, 0, 0)
        logger.info(f"设置控件边距: {content_edit.contentsMargins()}")
        
        # 设置最小高度，确保基本内容显示
        content_edit.setMinimumHeight(40)
        logger.info(f"设置最小高度: 40")
        
        # 移除最大高度限制，让内容完全自适应
        content_edit.setMaximumHeight(16777215)  # Qt默认的最大高度值，相当于无限制
        logger.info(f"移除最大高度限制")
        
        # 调整文档边距
        content_edit.document().setDocumentMargin(8)
        logger.info(f"设置文档边距: {content_edit.document().documentMargin()}")
        
        # 确保内容编辑框能够自动调整高度以适应内容
        # 移除固定高度设置，让组件根据内容自动扩展
        content_edit.setSizeAdjustPolicy(QTextEdit.SizeAdjustPolicy.AdjustToContents)
        logger.info(f"设置自动调整大小策略: {content_edit.sizeAdjustPolicy()}")
        
        # 添加到布局
        layout.addWidget(content_edit)
        
        # 文档宽度必须与内容编辑框宽度匹配，否则会导致高度计算错误
        # 延迟设置文档宽度，确保布局已经完成初步调整
        QTimer.singleShot(0, lambda: self._adjust_document_width(content_edit))
        
        logger.info(f"添加到布局后的初始尺寸: {content_edit.sizeHint()}")
        logger.info(f"文档初始尺寸: {content_edit.document().size()}")
        
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
        # 设置最大宽度为父容器宽度的80%，允许气泡自适应页面宽度
        max_width = int(self.parent().width() * 0.8) if self.parent() else 800
        bubble.setMaximumWidth(max_width)
        logger.info(f"初始化AI气泡宽度: {max_width}, 父容器宽度: {self.parent().width() if self.parent() else '无'}")
        
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
        # 更新self.content为QTextEdit组件
        self.content = content_edit
        logger.info(f"创建AI内容编辑框，初始内容: {content_edit.toPlainText()}")
        
        # 设置换行模式为仅在单词边界换行，避免在单词中间换行
        content_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        logger.info(f"设置AI内容换行模式: {content_edit.wordWrapMode()}")
        
        # 设置自动换行模式，根据窗口大小自动换行
        content_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        logger.info(f"设置AI内容自动换行模式: {content_edit.lineWrapMode()}")
        
        content_edit.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        
        # 禁用垂直滚动条，让内容完全展开
        content_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 设置大小策略，水平方向优先使用可用空间，垂直方向完全扩展以显示所有内容
        content_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        logger.info(f"设置大小策略: {content_edit.sizePolicy()}")
        
        # 设置对齐方式
        content_edit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # 设置缩进和边距
        content_edit.setContentsMargins(0, 0, 0, 0)
        logger.info(f"设置AI内容控件边距: {content_edit.contentsMargins()}")
        
        # 设置最小高度，确保基本内容显示
        content_edit.setMinimumHeight(40)
        logger.info(f"设置AI内容最小高度: 40")
        
        # 移除最大高度限制，让内容完全自适应
        content_edit.setMaximumHeight(16777215)  # Qt默认的最大高度值，相当于无限制
        logger.info(f"移除AI内容最大高度限制")
        
        # 调整文档边距
        content_edit.document().setDocumentMargin(8)
        logger.info(f"设置AI内容文档边距: {content_edit.document().documentMargin()}")
        
        # 确保内容编辑框能够自动调整高度以适应内容
        # 移除固定高度设置，让组件根据内容自动扩展
        content_edit.setSizeAdjustPolicy(QTextEdit.SizeAdjustPolicy.AdjustToContents)
        logger.info(f"设置AI内容自动调整大小策略: {content_edit.sizeAdjustPolicy()}")
        
        layout.addWidget(content_edit)
        
        # 同样为AI消息添加文档宽度调整
        QTimer.singleShot(0, lambda: self._adjust_document_width(content_edit))
        
        logger.info(f"添加到布局后的AI内容初始尺寸: {content_edit.sizeHint()}")
        logger.info(f"AI内容文档初始尺寸: {content_edit.document().size()}")
        
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
        # 记录更新前的详细尺寸信息
        before_size = self.sizeHint()
        before_actual_size = self.size()
        logger.info(f"[详细调试] 消息气泡更新前 - sizeHint: {before_size}, actual size: {before_actual_size}, 角色={self.role}, 内容长度={len(content)}")
        
        # 记录内容变化
        old_content = self.content.toPlainText() if hasattr(self.content, "toPlainText") else str(self.content)
        content_change = f"{old_content[:30]}..." if len(old_content) > 30 else old_content
        new_content_preview = f"{content[:30]}..." if len(content) > 30 else content
        logger.info(f"[详细调试] 内容更新: {content_change} -> {new_content_preview}, 角色={self.role}, 新内容总行数={content.count(chr(10)) + 1}")
        
        # 记录当前气泡对象标识，帮助跟踪哪个气泡在处理
        logger.info(f"[详细调试] 处理的气泡对象: {self}, 内容组件: {self.content}, 内容类型: {type(self.content).__name__}")
        
        # 不要将self.content设置为字符串，保留QTextEdit组件引用
        
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
            logger.info(f"找到气泡组件: {bubble_widget.objectName()}, 尺寸: {bubble_widget.size()}, 角色={self.role}")
            
            # 在气泡组件中找到内容组件并更新
            content_widget = None
            for i in range(bubble_widget.layout().count()):
                child = bubble_widget.layout().itemAt(i)
                widget = child.widget()
                if widget:
                    if isinstance(widget, (QLabel, QTextEdit)) and widget.objectName() in ["userContent", "assistantContent"]:
                        content_widget = widget
                        break
            
            if content_widget:
                logger.info(f"找到内容组件: {content_widget.objectName()}, 类型: {type(content_widget).__name__}, 尺寸: {content_widget.size()}")
                
                if isinstance(content_widget, QLabel):
                    # 更新QLabel内容
                    content_widget.setText(content)
                    logger.info(f"更新QLabel内容，更新后尺寸: {content_widget.size()}")
                    # 强制重新计算尺寸
                    content_widget.adjustSize()
                    bubble_widget.adjustSize()
                elif isinstance(content_widget, QTextEdit):
                    # 更新QTextEdit内容
                    # 保存当前光标位置
                    cursor = content_widget.textCursor()
                    
                    # 更新内容
                    content_widget.setPlainText(content)
                    
                    # 恢复光标位置
                    content_widget.setTextCursor(cursor)
                    
                    # 记录内容更新后的文档状态
                    doc = content_widget.document()
                    doc_height_before = doc.size().height()
                    logger.info(f"QTextEdit内容更新后，文档高度: {doc_height_before}, 行数: {content.count(chr(10)) + 1}")
                    
                    # 设置合适的最大宽度（与气泡最大宽度一致，减去边距）
                    # 动态计算气泡最大宽度为父容器宽度的80%
                    parent_width = self.parent().width() if self.parent() else 0
                    max_bubble_width = int(parent_width * 0.8) if self.parent() else 800
                    max_content_width = max_bubble_width - 24  # 减去左右边距各12
                    content_widget.setMaximumWidth(max_content_width)
                    content_widget.setMinimumWidth(0)  # 清除最小宽度限制
                    logger.info(f"父容器宽度: {parent_width}, 设置内容组件最大宽度: {max_content_width}, 气泡最大宽度: {max_bubble_width}")
                    
                    # 禁用垂直滚动条，让内容完全展开
                    content_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                    logger.info(f"内容组件滚动条策略: {content_widget.verticalScrollBarPolicy()}")
                    
                    # 手动设置文档宽度，确保高度计算准确
                    doc = content_widget.document()
                    bubble_margins = bubble_widget.layout().contentsMargins()
                    content_margins = content_widget.contentsMargins()
                    doc_margin = doc.documentMargin()
                    
                    logger.info(f"详细尺寸计算 - 气泡边距: 左={bubble_margins.left()}, 上={bubble_margins.top()}, 右={bubble_margins.right()}, 下={bubble_margins.bottom()}")
                    logger.info(f"详细尺寸计算 - 内容边距: 左={content_margins.left()}, 上={content_margins.top()}, 右={content_margins.right()}, 下={content_margins.bottom()}")
                    logger.info(f"详细尺寸计算 - 文档边距: {doc_margin}")
                    logger.info(f"详细尺寸计算 - 最大气泡宽度: {max_bubble_width}")
                    
                    # 计算文档应该有的宽度
                    doc_width = max_bubble_width - bubble_margins.left() - bubble_margins.right() - content_margins.left() - content_margins.right() - doc_margin * 2
                    doc_width = max(doc_width, 200)  # 确保至少200px宽度
                    
                    logger.info(f"详细尺寸计算 - 计算文档宽度: {max_bubble_width} - {bubble_margins.left()} - {bubble_margins.right()} - {content_margins.left()} - {content_margins.right()} - {doc_margin * 2} = {doc_width}")
                    
                    # 设置文档宽度
                    doc.setTextWidth(doc_width)
                    doc_height = doc.size().height()
                    logger.info(f"[详细调试] 手动设置文档宽度: {doc_width}, 文档高度: {doc_height}, 文档行数: {len(doc.toPlainText().splitlines())}, 最大高度: {content_widget.maximumHeight()}")
                    
                    # 计算实际需要的高度（包括文档边距和内容边距）
                    calculated_height = doc_height + doc_margin * 2 + content_margins.top() + content_margins.bottom()
                    logger.info(f"[详细调试] 计算高度: 文档高度({doc_height}) + 文档边距*2({doc_margin*2}) + 内容边距({content_margins.top() + content_margins.bottom()}) = {calculated_height}")
                    
                    # 记录文档的最后几行内容，验证是否完整
                    doc_lines = doc.toPlainText().splitlines()
                    logger.info(f"[详细调试] 文档最后5行: {doc_lines[-5:] if len(doc_lines) > 5 else doc_lines}")
                    
                    # 记录文档内容行数和最后几行，帮助调试
                    doc_lines = doc.toPlainText().splitlines()
                    logger.info(f"文档内容信息 - 总行数: {len(doc_lines)}, 最后5行内容: {doc_lines[-5:]}")
                    
                    # 设置内容组件自动调整大小策略
                    content_widget.setSizeAdjustPolicy(QTextEdit.SizeAdjustPolicy.AdjustToContents)
                    logger.info(f"设置内容组件自动调整大小策略: AdjustToContents")
                    
                    # 确保内容组件能够根据内容自动调整大小
                    content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                    logger.info(f"设置内容组件大小策略为Expanding")
                    
                    # 移除所有高度限制，让组件完全根据内容调整
                    content_widget.setMinimumHeight(40)  # 仅保留基本最小高度
                    content_widget.setMaximumHeight(16777215)  # Qt默认的最大高度值，相当于无限制
                    logger.info(f"移除内容组件所有高度限制")
                    
                    # 确保文档宽度正确设置，这样文档高度计算才会准确
                    doc_margin = doc.documentMargin()
                    content_margins = content_widget.contentsMargins()
                    
                    # 动态计算文档宽度，确保内容能够正确换行
                    bubble_margins = bubble_widget.layout().contentsMargins()
                    max_bubble_width = max_bubble_width if max_bubble_width > 0 else 800
                    
                    # 准确计算文档宽度，考虑所有边距和内边距
                    doc_width = max_bubble_width - \
                               bubble_margins.left() - bubble_margins.right() - \
                               content_margins.left() - content_margins.right() - \
                               doc_margin * 2
                    doc_width = max(doc_width, 200)  # 确保至少200px宽度
                    
                    logger.info(f"准确计算文档宽度: 气泡最大宽度({max_bubble_width}) - 气泡边距({bubble_margins.left() + bubble_margins.right()}) - 内容边距({content_margins.left() + content_margins.right()}) - 文档边距*2({doc_margin * 2}) = {doc_width}")
                    
                    # 设置文档宽度
                    doc.setTextWidth(doc_width)
                    logger.info(f"设置文档宽度为: {doc_width}")
                    
                    # 重新计算文档高度
                    doc_height = doc.size().height()
                    logger.info(f"重新计算文档高度: {doc_height}")
                    
                    # 计算内容组件的实际所需高度
                    actual_content_height = doc_height + (doc_margin * 2) + content_margins.top() + content_margins.bottom()
                    logger.info(f"计算实际内容高度: 文档高度({doc_height}) + 文档边距*2({doc_margin*2}) + 内容边距({content_margins.top() + content_margins.bottom()}) = {actual_content_height}")
                    
                    # 确保内容组件能够显示所有内容
                    content_widget.setMinimumHeight(int(actual_content_height))
                    logger.info(f"设置内容组件最小高度为: {int(actual_content_height)}")
                    
                    # 强制重新计算尺寸
                    content_widget.updateGeometry()
                    content_widget.adjustSize()
                    logger.info(f"强制内容组件重新计算尺寸")
                    
                    # 确保内容组件可见
                    content_widget.show()
                    
                    # 记录内容组件的最终状态
                    final_size = content_widget.size()
                    final_doc_height = doc.size().height()
                    logger.info(f"内容组件最终状态 - 尺寸: {final_size}, 文档高度: {final_doc_height}, 可见性: {content_widget.isVisible()}")
                    
                    # 只在内容稳定后执行一次最终尺寸调整
                    # 取消之前可能存在的更新定时器
                    if hasattr(self, '_update_timer'):
                        self._update_timer.stop()
                        delattr(self, '_update_timer')
                    
                    # 创建新的定时器，设置较短的延迟，确保它在chat_widget的定时器执行之后再执行
                    from PyQt6.QtCore import QTimer
                    self._update_timer = QTimer(self)
                    self._update_timer.setSingleShot(True)
                    self._update_timer.setInterval(300)  # 调整为300ms，确保在chat_widget的200ms定时器之后执行
                    
                    def final_size_adjustment():
                        # 确保定时器只执行一次
                        if not hasattr(self, '_update_timer'):
                            return
                        
                        logger.info("=== 开始执行最终尺寸调整 ===")
                        
                        # 更新文档宽度 - 确保使用气泡组件的实际可用宽度
                        if hasattr(content_widget, 'document'):
                            doc = content_widget.document()
                            
                            # 获取气泡组件的最大可用宽度
                            bubble_margins = bubble_widget.layout().contentsMargins() if bubble_widget.layout() else (0, 0, 0, 0)
                            content_margins = content_widget.contentsMargins()
                            doc_margin = doc.documentMargin()
                            
                            # 使用气泡的最大宽度而不是当前宽度，确保内容充分利用可用空间
                            bubble_max_width = bubble_widget.maximumWidth()
                            
                            # 计算文档可用宽度（气泡最大宽度减去所有边距）
                            available_doc_width = bubble_max_width - bubble_margins.left() - bubble_margins.right() - content_margins.left() - content_margins.right() - doc_margin * 2
                            available_doc_width = max(200, available_doc_width)
                            
                            doc.setTextWidth(available_doc_width)
                            logger.info(f"最终 - 文档宽度: {available_doc_width}, 文档高度: {doc.size().height()}")
                            logger.info(f"最终 - 计算依据: 气泡宽度={bubble_widget.width()}, 气泡边距={bubble_margins}, 内容边距={content_margins}, 文档边距={doc_margin}")
                        
                        # 强制重新计算尺寸
                        content_widget.updateGeometry()
                        content_widget.adjustSize()
                        logger.info(f"最终 - 内容组件调整后尺寸: {content_widget.size()}, 最小高度: {content_widget.minimumHeight()}, 最大高度: {content_widget.maximumHeight()}")
                        
                        # 更新气泡组件尺寸
                        bubble_widget.updateGeometry()
                        bubble_widget.adjustSize()
                        logger.info(f"最终 - 气泡组件调整后尺寸: {bubble_widget.size()}")
                        
                        # 确保整个消息气泡调整到正确大小
                        self.updateGeometry()
                        self.adjustSize()
                        logger.info(f"最终 - 消息气泡调整后尺寸: {self.size()}, sizeHint: {self.sizeHint()}")
                        
                        # 确保消息气泡的高度不小于sizeHint返回的高度，以保证气泡之间有足够的间距
                        if self.size().height() < self.sizeHint().height():
                            logger.info(f"调整消息气泡高度为sizeHint高度: {self.sizeHint().height()}")
                            self.setMinimumHeight(self.sizeHint().height())
                            self.updateGeometry()
                            self.adjustSize()
                        
                        # 请求父组件更新，确保布局正确
                        if self.parent():
                            self.parent().updateGeometry()
                            if hasattr(self.parent(), 'viewport') and hasattr(self.parent().viewport(), 'update'):
                                self.parent().viewport().update()
                            logger.info(f"最终 - 请求父组件({type(self.parent()).__name__})更新")
                        
                        # 再次检查内容是否完全可见
                        viewport = content_widget.viewport()
                        viewport_rect = viewport.rect()
                        content_rect = content_widget.contentsRect()
                        logger.info(f"最终可见性检查 - 视口尺寸: {viewport_rect.size()}, 内容尺寸: {content_rect.size()}, 文档高度: {doc.size().height()}")
                        
                        # 详细记录内容的可见性状态
                        if isinstance(content_widget, QTextEdit):
                            doc = content_widget.document()
                            doc_height = doc.size().height()
                            doc_margin = doc.documentMargin()
                            total_content_height = doc_height + (doc_margin * 2)
                            logger.info(f"最终内容分析 - 文档高度: {doc_height}, 文档边距*2: {doc_margin*2}, 总内容高度: {total_content_height}")
                        
                        # 如果内容仍未完全可见，进行进一步调整
                        if content_rect.height() > viewport_rect.height():
                            logger.error(f"[最终修复] 内容仍未完全可见！进行额外调整")
                            logger.info(f"[最终修复] 视口高度: {viewport_rect.height()}, 内容高度: {content_rect.height()}, 差值: {content_rect.height() - viewport_rect.height()}")
                            
                            # 计算需要增加的高度
                            additional_height = content_rect.height() - viewport_rect.height() + 30  # 增加额外的安全余量
                            new_min_height = content_widget.minimumHeight() + additional_height
                            
                            # 记录调整前的状态
                            logger.info(f"[最终修复] 调整前 - 内容组件最小高度: {content_widget.minimumHeight()}, 实际高度: {content_widget.height()}")
                            
                            # 进行调整
                            content_widget.setMinimumHeight(new_min_height)
                            logger.info(f"[最终修复] 调整后 - 内容组件最小高度: {new_min_height}")
                            
                            # 再次调整所有组件
                            content_widget.updateGeometry()
                            content_widget.adjustSize()
                            logger.info(f"[最终修复] 内容组件调整后尺寸: {content_widget.size()}")
                            
                            bubble_widget.updateGeometry()
                            bubble_widget.adjustSize()
                            logger.info(f"[最终修复] 气泡组件调整后尺寸: {bubble_widget.size()}")
                            
                            self.updateGeometry()
                            self.adjustSize()
                            logger.info(f"[最终修复] 消息气泡调整后尺寸: {self.size()}")
                            
                            # 再次检查可见性
                            viewport_rect_after = viewport.rect()
                            content_rect_after = content_widget.contentsRect()
                            logger.info(f"[最终修复] 调整后可见性 - 视口高度: {viewport_rect_after.height()}, 内容高度: {content_rect_after.height()}")
                            
                            if content_rect_after.height() > viewport_rect_after.height():
                                logger.error(f"[最终修复] 内容仍然不完全可见！视口高度: {viewport_rect_after.height()}, 内容高度: {content_rect_after.height()}")
                            else:
                                logger.info(f"[最终修复] 内容现在完全可见")
                            
                            # 更新父组件
                            if self.parent():
                                self.parent().updateGeometry()
                                if hasattr(self.parent(), 'viewport') and hasattr(self.parent().viewport(), 'update'):
                                    self.parent().viewport().update()
                        
                        logger.info("=== 最终尺寸调整完成 ===")
                        
                        # 清理定时器
                        if hasattr(self, '_update_timer'):
                            self._update_timer.stop()
                            delattr(self, '_update_timer')
                    
                    # 连接定时器信号并启动
                    self._update_timer.timeout.connect(final_size_adjustment)
                    self._update_timer.start()
                    
                    # 检查内容是否完全可见
                    viewport = content_widget.viewport()
                    viewport_rect = viewport.rect()
                    content_rect = content_widget.contentsRect()
                    logger.info(f"内容可见性检查 - 视口尺寸: {viewport_rect.size()}, 内容尺寸: {content_rect.size()}, 文档高度: {doc.size().height()}")
                    if content_rect.height() > viewport_rect.height():
                        logger.warning(f"内容未完全可见！视口高度: {viewport_rect.height()}, 内容高度: {content_rect.height()}")
                        
                        # 内容未完全可见，进行额外的尺寸调整
                        logger.info(f"[内容修复] 开始执行额外的尺寸调整")
                        
                        # 再次强制设置文档宽度
                        doc_width = max(200, doc.idealWidth())
                        doc.setTextWidth(doc_width)
                        logger.info(f"[内容修复] 重新设置文档宽度: {doc_width}")
                        
                        # 强制重新计算内容组件尺寸
                        content_widget.updateGeometry()
                        content_widget.adjustSize()
                        logger.info(f"[内容修复] 重新调整内容组件尺寸: {content_widget.size()}")
                        
                        # 强制重新计算气泡组件尺寸
                        bubble_widget.updateGeometry()
                        bubble_widget.adjustSize()
                        logger.info(f"[内容修复] 重新调整气泡组件尺寸: {bubble_widget.size()}")
                        
                        # 确保整个消息气泡调整到正确大小
                        self.updateGeometry()
                        self.adjustSize()
                        logger.info(f"[内容修复] 重新调整整个消息气泡尺寸: {self.size()}")
                    else:
                        logger.info(f"内容完全可见，视口高度: {viewport_rect.height()}, 内容高度: {content_rect.height()}")
                    
                    # 强制触发布局更新，确保尺寸变化传播到父组件
                    self.updateGeometry()
                    self.adjustSize()  # 确保整个消息气泡调整到正确大小
                    self.repaint()
                    logger.info(f"已强制触发布局更新，确保尺寸变化传播")
                    logger.info(f"气泡组件更新几何信息后尺寸: {bubble_widget.size()}")
                    logger.info(f"整个消息气泡调整后尺寸: {self.size()}")
        else:
            logger.warning(f"未找到气泡组件，回退到重新构建 UI, 角色={self.role}")
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
        
        # 强制更新当前组件的尺寸
        self.updateGeometry()
        self.adjustSize()
        
        # 记录更新后的详细尺寸信息
        after_size = self.sizeHint()
        after_actual_size = self.size()
        logger.info(f"消息气泡更新后 - sizeHint: {after_size}, actual size: {after_actual_size}, 角色={self.role}")
        logger.info(f"消息气泡尺寸变化 - sizeHint: {before_size} -> {after_size}, actual: {before_actual_size} -> {after_actual_size}, 角色={self.role}")
        
        # 输出底部留白分析
        if hasattr(self.content, 'document'):
            doc = self.content.document()
        
        # 直接执行一次额外的尺寸调整，确保最后一个气泡完全显示
        self._extra_size_adjustment()
    
    def _extra_size_adjustment(self) -> None:
        """
        执行额外的尺寸调整，确保最后一个气泡完全显示
        """
        logger.info("=== 开始执行额外尺寸调整 ===")
        
        # 直接获取父组件（message_list）
        parent_widget = self.parent()
        if not parent_widget:
            logger.warning("没有父组件，无法执行额外尺寸调整")
            return
        
        logger.info(f"父组件类型: {type(parent_widget).__name__}, 尺寸: {parent_widget.size()}")
        
        # 详细记录当前气泡的状态
        logger.info(f"当前气泡信息 - 尺寸: {self.size()}, sizeHint: {self.sizeHint()}, 角色: {self.role}")
        
        # 获取气泡中的内容组件
        content_widget = None
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
            logger.info(f"气泡组件: {bubble_widget}, 尺寸: {bubble_widget.size()}")
            
            # 在气泡组件中找到内容组件
            for i in range(bubble_widget.layout().count()):
                child = bubble_widget.layout().itemAt(i)
                widget = child.widget()
                if widget:
                    if isinstance(widget, (QLabel, QTextEdit)) and widget.objectName() in ["userContent", "assistantContent"]:
                        content_widget = widget
                        break
        
        if content_widget:
            logger.info(f"内容组件: {content_widget}, 类型: {type(content_widget).__name__}, 尺寸: {content_widget.size()}")
            
            # 记录内容组件的详细信息
            if isinstance(content_widget, QTextEdit):
                doc = content_widget.document()
                doc_height = doc.size().height()
                doc_width = doc.textWidth()
                logger.info(f"QTextEdit文档信息 - 高度: {doc_height}, 宽度: {doc_width}, 总行数: {len(doc.toPlainText().splitlines())}")
                
                # 记录视口和内容尺寸
                viewport = content_widget.viewport()
                viewport_rect = viewport.rect()
                content_rect = content_widget.contentsRect()
                logger.info(f"视口与内容尺寸 - 视口: {viewport_rect.size()}, 内容: {content_rect.size()}")
                
                # 检查内容是否完全可见
                if content_rect.height() > viewport_rect.height():
                    logger.warning(f"内容未完全可见！视口高度: {viewport_rect.height()}, 内容高度: {content_rect.height()}")
                else:
                    logger.info(f"内容完全可见，视口高度: {viewport_rect.height()}, 内容高度: {content_rect.height()}")
            
            elif isinstance(content_widget, QLabel):
                logger.info(f"QLabel内容 - 文本长度: {len(content_widget.text())}, 行数: {content_widget.text().count(chr(10)) + 1}")
        
        # 强制父组件更新布局
        parent_widget.updateGeometry()
        parent_widget.adjustSize()
        logger.info(f"父组件调整后尺寸: {parent_widget.size()}")
        
        # 如果父组件有viewport，更新它
        if hasattr(parent_widget, 'viewport') and hasattr(parent_widget.viewport(), 'update'):
            parent_widget.viewport().update()
            logger.info("已更新父组件viewport")
        
        # 如果父组件是QListWidget，尝试重新计算所有项目的尺寸
        from PyQt6.QtWidgets import QListWidget
        if isinstance(parent_widget, QListWidget):
            logger.info("父组件是QListWidget，尝试重新计算所有项目尺寸")
            
            # 遍历所有项目，重新设置它们的尺寸
            for i in range(parent_widget.count()):
                item = parent_widget.item(i)
                widget = parent_widget.itemWidget(item)
                if widget:
                    # 确保widget可见
                    widget.show()
                    
                    # 强制调整widget大小
                    widget.updateGeometry()
                    widget.adjustSize()
                    
                    # 重新设置item的尺寸
                    item.setSizeHint(widget.size())
                    logger.info(f"重新设置项目{i}的尺寸: {widget.size()}, sizeHint: {widget.sizeHint()}")
            
            # 再次更新父组件
            parent_widget.updateGeometry()
            parent_widget.adjustSize()
            logger.info(f"QListWidget最终调整后尺寸: {parent_widget.size()}")
        
        logger.info("=== 额外尺寸调整完成 ===")
        
        # 输出底部留白分析
        if hasattr(self.content, 'document'):
            doc = self.content.document()
            doc_height = doc.size().height()
            doc_margin = doc.documentMargin()
            content_margins = self.content.contentsMargins()
            calculated_content_height = doc_height + doc_margin * 2 + content_margins.top() + content_margins.bottom()
            actual_content_height = self.content.height()
            bubble_height = self.size().height()
            
            logger.info(f"内容分析 - 文档高度: {doc_height}, 文档边距: {doc_margin}, 内容边距: {content_margins}")
            logger.info(f"内容分析 - 计算内容高度: {calculated_content_height}, 实际内容高度: {actual_content_height}")
            logger.info(f"内容分析 - 气泡总高度: {bubble_height}, 内容高度占比: {actual_content_height / bubble_height if bubble_height > 0 else 0:.2f}")
            
            if bubble_height > actual_content_height * 1.2:
                logger.warning(f"可能存在底部留白 - 气泡高度: {bubble_height}, 内容高度: {actual_content_height}")
            
            # 检查内容是否真的完全可见
            if isinstance(self.content, QTextEdit):
                viewport = self.content.viewport()
                viewport_rect = viewport.rect()
                content_rect = self.content.contentsRect()
                logger.info(f"最终内容可见性检查 - 视口高度: {viewport_rect.height()}, 内容高度: {content_rect.height()}, 文档高度: {doc_height}")
                
                if content_rect.height() > viewport_rect.height():
                    logger.error(f"[严重问题] 即使在额外调整后，内容仍未完全可见！缺少高度: {content_rect.height() - viewport_rect.height()}")
                else:
                    logger.info(f"[修复成功] 内容现在完全可见")
        
        # 记录父组件的更新请求
        if self.parent():
            logger.info(f"请求父组件更新几何信息，父组件类型: {type(self.parent()).__name__}")
            self.parent().updateGeometry()
            if hasattr(self.parent(), 'viewport') and hasattr(self.parent().viewport(), 'update'):
                self.parent().viewport().update()
                logger.info("请求父组件视口更新")
        
        logger.info("=== 额外尺寸调整最终完成 ===")
        

    
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
    
    def _adjust_document_width(self, content_edit):
        """
        调整文档宽度以匹配气泡的最大宽度，确保准确的高度计算
        """
        if content_edit and content_edit.document():
            # 动态计算气泡最大宽度为父容器宽度的80%
            max_bubble_width = int(self.parent().width() * 0.8) if self.parent() else 800
            
            # 计算气泡内部可用宽度（减去气泡边距）
            bubble_widget = self.findChild(QWidget, "userBubble" if self.role == "user" else "assistantBubble")
            if bubble_widget:
                bubble_margins = bubble_widget.layout().contentsMargins()
            else:
                bubble_margins = self.layout().itemAt(0).widget().layout().contentsMargins() if self.role == 'assistant' else self.layout().itemAt(1).widget().layout().contentsMargins()
            
            available_width = max_bubble_width - bubble_margins.left() - bubble_margins.right()
            
            # 内容组件的边距和文档边距
            content_margins = content_edit.contentsMargins()
            document_margin = content_edit.document().documentMargin()
            
            # 计算实际可用的文档宽度
            doc_width = available_width - content_margins.left() - content_margins.right() - document_margin * 2
            
            # 确保可用宽度大于0，且至少为200px（避免过窄）
            doc_width = max(doc_width, 200)
            
            # 设置文档宽度，这会影响自动换行和高度计算
            content_edit.document().setTextWidth(doc_width)
            logger.info(f"调整文档宽度，气泡最大宽度={max_bubble_width}, 气泡边距={bubble_margins}, 内容边距={content_margins}, 文档边距={document_margin}, 设置文档宽度={doc_width}")
            
            # 强制内容编辑框重新计算尺寸
            content_edit.updateGeometry()
            self.parent().updateGeometry()
        
    def update_width(self) -> None:
        """
        更新气泡宽度，根据父容器大小重新调整
        """
        logger.info(f"=== 开始更新消息气泡宽度 ({self.role}) ===")
        
        # 记录父容器信息
        parent_info = f"类型: {type(self.parent()).__name__}, 宽度: {self.parent().width()}, 高度: {self.parent().height()}" if self.parent() else "无"
        logger.info(f"父容器信息: {parent_info}")
        
        # 动态计算气泡最大宽度为父容器宽度的80%
        max_width = int(self.parent().width() * 0.8) if self.parent() else 800
        logger.info(f"计算的最大宽度: {max_width} (父容器宽度的80%)")
        
        # 获取气泡组件
        bubble_widget = self.findChild(QWidget, "userBubble" if self.role == "user" else "assistantBubble")
        if bubble_widget:
            logger.info(f"找到气泡组件: {bubble_widget.objectName()}")
            logger.info(f"气泡当前最大宽度: {bubble_widget.maximumWidth()}, 当前宽度: {bubble_widget.width()}")
            
            # 更新气泡组件的最大宽度
            bubble_widget.setMaximumWidth(max_width)
            logger.info(f"更新气泡最大宽度: {max_width}")
            
            # 直接使用self.content作为内容组件
            if hasattr(self, 'content'):
                logger.info(f"self.content 属性存在: {type(self.content).__name__}")
                if isinstance(self.content, QTextEdit):
                    content_widget = self.content
                    logger.info(f"内容组件为QTextEdit: {content_widget.objectName()}")
                    logger.info(f"内容组件当前最大宽度: {content_widget.maximumWidth()}, 当前宽度: {content_widget.width()}")
                    
                    # 获取气泡组件的边距信息
                    bubble_margins = bubble_widget.layout().contentsMargins() if bubble_widget.layout() else (0, 0, 0, 0)
                    content_margins = content_widget.contentsMargins()
                    
                    # 更新内容组件的最大宽度（气泡最大宽度减去气泡边距）
                    max_content_width = max_width - bubble_margins.left() - bubble_margins.right()
                    content_widget.setMaximumWidth(max_content_width)
                    logger.info(f"气泡边距: {bubble_margins}, 内容边距: {content_margins}")
                    logger.info(f"更新内容组件最大宽度: {max_content_width}")
                    
                    # 重新计算文档宽度
                    doc = content_widget.document()
                    if doc:
                        doc_margin = doc.documentMargin()
                        # 计算文档可用宽度（内容最大宽度减去内容边距和文档边距）
                        doc_width = max_content_width - content_margins.left() - content_margins.right() - doc_margin * 2
                        doc_width = max(doc_width, 200)
                        logger.info(f"文档边距: {doc_margin}, 内容边距: {content_margins}")
                        logger.info(f"计算文档宽度: {max_content_width} - {content_margins.left()} - {content_margins.right()} - {doc_margin*2} = {doc_width}")
                        doc.setTextWidth(doc_width)
                        logger.info(f"重新设置文档宽度: {doc_width}")
                    
                    # 更新自动换行模式
                    content_widget.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
                    logger.info(f"设置内容组件换行模式: {content_widget.lineWrapMode()}")
                else:
                    logger.warning(f"self.content 不是QTextEdit类型: {type(self.content).__name__}")
            else:
                logger.warning("self.content 属性不存在")
            
            # 强制重新计算尺寸
            logger.info("开始强制重新计算尺寸...")
            
            # 设置气泡组件的最小宽度为内容实际需要的宽度，确保内容不会被过度压缩
            if hasattr(self, 'content') and isinstance(self.content, QTextEdit):
                doc = self.content.document()
                if doc:
                    # 获取内容实际需要的宽度
                    content_actual_width = min(doc.idealWidth() + content_margins.left() + content_margins.right() + doc_margin * 2, max_content_width)
                    logger.info(f"内容实际需要宽度: {content_actual_width}, 最大可用宽度: {max_content_width}")
                    
                    # 设置气泡组件的最小宽度，确保内容能够正确显示
                    bubble_min_width = content_actual_width + bubble_margins.left() + bubble_margins.right()
                    # 将float转换为int，避免TypeError
                    bubble_widget.setMinimumWidth(int(bubble_min_width))
                    logger.info(f"设置气泡最小宽度: {bubble_min_width} (转换为int: {int(bubble_min_width)})")
            
            # 强制气泡组件使用最大宽度
            bubble_widget.updateGeometry()
            bubble_widget.adjustSize()
            logger.info(f"气泡调整后尺寸: 宽度={bubble_widget.width()}, 高度={bubble_widget.height()}")
            
            # 如果气泡宽度仍然小于最大宽度，手动设置为最大宽度
            if bubble_widget.width() < max_width:
                logger.info(f"气泡宽度({bubble_widget.width()})小于最大宽度({max_width})，手动设置为最大宽度")
                # 将float转换为int，避免TypeError
                bubble_widget.setMinimumWidth(int(max_width))
                bubble_widget.updateGeometry()
                bubble_widget.adjustSize()
                logger.info(f"气泡手动调整后尺寸: 宽度={bubble_widget.width()}, 高度={bubble_widget.height()}")
            
            # 强制计算气泡高度
            if hasattr(self, 'content') and hasattr(self.content, 'document'):
                doc = self.content.document()
                if doc:
                    # 确保文档宽度正确设置
                    doc_width = doc.textWidth()
                    logger.info(f"当前文档宽度: {doc_width}")
                    
                    # 触发文档重新计算高度
                    doc.setTextWidth(doc_width)
                    logger.info(f"文档高度: {doc.size().height()}")
                    
                    # 计算并设置气泡总高度
                    doc_height = doc.size().height()
                    doc_margin = doc.documentMargin()
                    content_margins = self.content.contentsMargins()
                    bubble_margins = bubble_widget.layout().contentsMargins()
                    
                    # 计算内容总高度
                    content_total_height = doc_height + doc_margin * 2 + content_margins.top() + content_margins.bottom()
                    
                    # 计算气泡总高度
                    ai_label_height = 8 if self.role == 'assistant' else 0  # AI标识高度
                    timestamp_height = 8  # 时间戳高度
                    internal_padding = 4  # 内部边距
                    total_height = ai_label_height + content_total_height + timestamp_height + internal_padding
                    
                    logger.info(f"计算气泡总高度: AI标识({ai_label_height}) + 内容({content_total_height}) + 时间戳({timestamp_height}) + 内部边距({internal_padding}) = {total_height}")
                    
                    # 设置气泡最小高度，允许内容自动扩展
                    self.setMinimumHeight(int(total_height))
                    bubble_widget.setMinimumHeight(int(total_height))
                    logger.info(f"设置气泡最小高度: {int(total_height)}")
            
            self.updateGeometry()
            self.adjustSize()
            logger.info(f"整体气泡调整后尺寸: 宽度={self.width()}, 高度={self.height()}")
        else:
            logger.warning(f"未找到气泡组件: {'userBubble' if self.role == 'user' else 'assistantBubble'}")
        
        # 记录最终状态
        logger.info(f"最终气泡最大宽度: {self.findChild(QWidget, 'userBubble' if self.role == 'user' else 'assistantBubble').maximumWidth() if bubble_widget else '无'}")
        logger.info(f"最终内容最大宽度: {self.content.maximumWidth() if hasattr(self, 'content') and isinstance(self.content, QTextEdit) else '无'}")
        logger.info(f"=== 消息气泡宽度更新完成 ({self.role}) ===")
    
    def sizeHint(self):
        """
        重写sizeHint方法，确保消息气泡的高度能够正确计算，避免底部留白问题。
        """
        # 获取父容器宽度，动态计算气泡最大宽度为父容器宽度的80%
        max_bubble_width = 800  # 默认最大宽度
        if self.parent():
            parent_width = self.parent().width()
            max_bubble_width = int(parent_width * 0.8)
            # 确保最小宽度为400，避免在小窗口下气泡过窄
            if max_bubble_width < 400:
                max_bubble_width = 400
        
        # 确保内容组件存在且为QTextEdit类型
        if hasattr(self, 'content') and isinstance(self.content, QTextEdit) and self.content.document():
            doc = self.content.document()
            content_margins = self.content.contentsMargins()
            doc_margin = doc.documentMargin()
            
            # 获取气泡组件以计算可用宽度
            bubble_widget = self.findChild(QWidget, "userBubble" if self.role == "user" else "assistantBubble")
            
            # 计算文档可用宽度
            if bubble_widget and bubble_widget.layout():
                bubble_margins = bubble_widget.layout().contentsMargins()
                doc_width = max_bubble_width - bubble_margins.left() - bubble_margins.right() - content_margins.left() - content_margins.right() - doc_margin * 2
            else:
                doc_width = max_bubble_width - 40  # 默认边距
            
            doc_width = max(doc_width, 200)
            
            # 调整文档宽度以确保准确的高度计算
            current_doc_width = doc.textWidth()
            if abs(doc_width - current_doc_width) > 1:
                doc.setTextWidth(doc_width)
            
            # 计算内容总高度（包含文档边距和组件边距）
            doc_height = doc.size().height()
            content_total_height = doc_height + doc_margin * 2 + content_margins.top() + content_margins.bottom()
            
            # 计算气泡总高度，确保有足够的最小高度
            ai_label_height = 20 if self.role == 'assistant' else 0  # AI标识高度
            timestamp_height = 15 if self.timestamp else 0  # 时间戳高度
            button_height = 25 if self.diff_button and self.diff_button.isVisible() else 0  # 按钮高度
            spacing = 12  # 布局间距
            main_layout_margins = 10  # 主布局上下边距总和(5+5)
            bubble_margins = 16  # 气泡布局上下边距总和(8+8)
            
            # 计算总高度，包含所有元素和边距
            total_height = ai_label_height + content_total_height + timestamp_height + button_height + spacing + main_layout_margins + bubble_margins
            min_height = 80  # 确保基本内容显示完整
            total_height = max(total_height, min_height)
            
            # 返回最终尺寸
            return QSize(int(max_bubble_width), int(total_height))
        
        # 默认尺寸
        return QSize(800, 80)
    

    



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
