"""
文本对比视图模块

提供分屏对比组件，用于显示文本修改前后的差异。
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QLabel, QPushButton, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor

logger = logging.getLogger(__name__)


class TextDiffViewer(QDialog):
    """
    文本对比视图对话框
    
    使用分屏布局显示原始文本和修改后的文本，并高亮显示差异。
    """
    
    def __init__(self, original_text: str, modified_text: str, parent: Optional[QWidget] = None):
        """
        初始化文本对比视图
        
        Args:
            original_text: 原始文本
            modified_text: 修改后的文本
            parent: 父组件
        """
        super().__init__(parent)
        
        self.original_text = original_text
        self.modified_text = modified_text
        
        self._init_ui()
        self._highlight_differences()
        
        logger.info("TextDiffViewer 初始化完成")
    
    def _init_ui(self) -> None:
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle("文本对比")
        self.resize(1000, 600)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题区域
        title_layout = QHBoxLayout()
        title_layout.setSpacing(20)
        
        # 原始文本标题
        original_label = QLabel("原始文本")
        original_label.setObjectName("titleLabel")
        original_label.setStyleSheet("""
            QLabel#titleLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
        """)
        title_layout.addWidget(original_label)
        
        title_layout.addStretch()
        
        # 修改后文本标题
        modified_label = QLabel("修改后文本")
        modified_label.setObjectName("titleLabel")
        modified_label.setStyleSheet("""
            QLabel#titleLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
        """)
        title_layout.addWidget(modified_label)
        
        layout.addLayout(title_layout)
        
        # 创建分屏对比组件
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：原始文本
        self.original_text_edit = QTextEdit()
        self.original_text_edit.setObjectName("originalTextEdit")
        self.original_text_edit.setReadOnly(True)
        self.original_text_edit.setPlainText(self.original_text)
        splitter.addWidget(self.original_text_edit)
        
        # 右侧：修改后文本
        self.modified_text_edit = QTextEdit()
        self.modified_text_edit.setObjectName("modifiedTextEdit")
        self.modified_text_edit.setReadOnly(True)
        self.modified_text_edit.setPlainText(self.modified_text)
        splitter.addWidget(self.modified_text_edit)
        
        # 设置初始比例（1:1）
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter, stretch=1)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 统计信息标签
        self.stats_label = QLabel()
        self.stats_label.setObjectName("statsLabel")
        self.stats_label.setStyleSheet("""
            QLabel#statsLabel {
                color: #666;
                font-size: 12px;
            }
        """)
        button_layout.addWidget(self.stats_label)
        
        button_layout.addStretch()
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.setObjectName("closeButton")
        close_button.setMinimumWidth(80)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QTextEdit#originalTextEdit, QTextEdit#modifiedTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
            }
            
            QPushButton#closeButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            
            QPushButton#closeButton:hover {
                background-color: #45a049;
            }
            
            QPushButton#closeButton:pressed {
                background-color: #3d8b40;
            }
        """)
    
    def _highlight_differences(self) -> None:
        """高亮显示文本差异"""
        try:
            # 使用简单的逐字符比较算法
            original_lines = self.original_text.split('\n')
            modified_lines = self.modified_text.split('\n')
            
            # 统计差异
            added_lines = 0
            removed_lines = 0
            modified_lines_count = 0
            
            # 创建高亮格式
            removed_format = QTextCharFormat()
            removed_format.setBackground(QColor(255, 200, 200))  # 浅红色背景
            
            added_format = QTextCharFormat()
            added_format.setBackground(QColor(200, 255, 200))  # 浅绿色背景
            
            # 简单的行级差异检测
            max_lines = max(len(original_lines), len(modified_lines))
            
            for i in range(max_lines):
                original_line = original_lines[i] if i < len(original_lines) else ""
                modified_line = modified_lines[i] if i < len(modified_lines) else ""
                
                if original_line != modified_line:
                    # 高亮原始文本中的删除行
                    if i < len(original_lines) and original_line:
                        cursor = self.original_text_edit.textCursor()
                        cursor.movePosition(QTextCursor.MoveOperation.Start)
                        
                        # 移动到目标行
                        for _ in range(i):
                            cursor.movePosition(QTextCursor.MoveOperation.Down)
                        
                        # 选择整行
                        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                        
                        # 应用格式
                        cursor.setCharFormat(removed_format)
                        
                        if not modified_line:
                            removed_lines += 1
                        else:
                            modified_lines_count += 1
                    
                    # 高亮修改后文本中的添加行
                    if i < len(modified_lines) and modified_line:
                        cursor = self.modified_text_edit.textCursor()
                        cursor.movePosition(QTextCursor.MoveOperation.Start)
                        
                        # 移动到目标行
                        for _ in range(i):
                            cursor.movePosition(QTextCursor.MoveOperation.Down)
                        
                        # 选择整行
                        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                        
                        # 应用格式
                        cursor.setCharFormat(added_format)
                        
                        if not original_line:
                            added_lines += 1
            
            # 更新统计信息
            stats_text = f"添加: {added_lines} 行 | 删除: {removed_lines} 行 | 修改: {modified_lines_count} 行"
            self.stats_label.setText(stats_text)
            
            logger.debug(f"差异高亮完成: {stats_text}")
            
        except Exception as e:
            logger.error(f"高亮差异失败: {e}", exc_info=True)
            self.stats_label.setText("差异分析失败")


def show_text_diff(original_text: str, modified_text: str, parent: Optional[QWidget] = None) -> None:
    """
    显示文本对比对话框
    
    Args:
        original_text: 原始文本
        modified_text: 修改后的文本
        parent: 父组件
    """
    dialog = TextDiffViewer(original_text, modified_text, parent)
    dialog.exec()
