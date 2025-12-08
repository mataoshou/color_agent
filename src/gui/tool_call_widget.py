"""
工具调用可视化组件

显示工具调用的名称、参数和结果。
"""

import logging
import json
from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class ToolCallWidget(QWidget):
    """工具调用可视化组件"""
    
    def __init__(self, tool_name: str, input_str: str = "",
                 parent: Optional[QWidget] = None):
        """
        初始化工具调用组件
        
        Args:
            tool_name: 工具名称
            input_str: 工具输入参数
            parent: 父组件
        """
        super().__init__(parent)
        
        self.tool_name = tool_name
        self.input_str = input_str
        self.output_str = ""
        self.is_finished = False
        
        # 动画相关
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._update_animation)
        self._animation_dots = 0
        
        self._init_ui()
        
        logger.debug(f"ToolCallWidget 创建: tool_name={tool_name}")

    def _init_ui(self) -> None:
        """初始化 UI"""
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        
        # 左对齐
        bubble = QWidget()
        bubble.setObjectName("toolCallBubble")
        bubble.setMaximumWidth(500)
        
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)
        
        # 工具图标和名称
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        icon_label = QLabel("🔧")
        icon_label.setObjectName("toolIcon")
        header_layout.addWidget(icon_label)
        
        self.tool_label = QLabel(f"调用工具: {self.tool_name}")
        self.tool_label.setObjectName("toolName")
        font = QFont()
        font.setBold(True)
        self.tool_label.setFont(font)
        header_layout.addWidget(self.tool_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 输入参数（如果有）
        if self.input_str:
            input_label = QLabel("参数:")
            input_label.setObjectName("paramLabel")
            layout.addWidget(input_label)
            
            self.input_content = QLabel(self._format_input(self.input_str))
            self.input_content.setObjectName("paramContent")
            self.input_content.setWordWrap(True)
            self.input_content.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            layout.addWidget(self.input_content)
        
        # 状态标签
        self.status_label = QLabel("执行中...")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)
        
        # 输出结果（初始隐藏）
        self.output_label = QLabel("结果:")
        self.output_label.setObjectName("resultLabel")
        self.output_label.hide()
        layout.addWidget(self.output_label)
        
        self.output_content = QLabel("")
        self.output_content.setObjectName("resultContent")
        self.output_content.setWordWrap(True)
        self.output_content.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.output_content.hide()
        layout.addWidget(self.output_content)
        
        main_layout.addWidget(bubble)
        main_layout.addStretch()
        
        # 样式
        self._apply_style()
        
        # 启动动画
        self._animation_timer.start(500)

    def _apply_style(self) -> None:
        """应用样式"""
        if self.is_finished:
            # 完成状态：绿色边框
            style = """
                QWidget#toolCallBubble {
                    background-color: #f0f9ff;
                    border: 2px solid #4CAF50;
                    border-radius: 12px;
                }
            """
        else:
            # 执行中状态：蓝色边框
            style = """
                QWidget#toolCallBubble {
                    background-color: #f0f9ff;
                    border: 2px solid #2196F3;
                    border-radius: 12px;
                }
            """
        
        style += """
            QLabel#toolIcon {
                font-size: 18px;
                background: transparent;
            }
            
            QLabel#toolName {
                color: #1976D2;
                font-size: 14px;
                background: transparent;
            }
            
            QLabel#paramLabel, QLabel#resultLabel {
                color: #666;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
            }
            
            QLabel#paramContent, QLabel#resultContent {
                color: #333;
                font-size: 13px;
                background-color: #e3f2fd;
                padding: 6px;
                border-radius: 4px;
            }
            
            QLabel#statusLabel {
                color: #2196F3;
                font-size: 12px;
                font-style: italic;
                background: transparent;
            }
        """
        
        self.setStyleSheet(style)
    
    def _format_input(self, input_str: str) -> str:
        """
        格式化输入参数
        
        Args:
            input_str: 输入参数字符串
            
        Returns:
            str: 格式化后的字符串
        """
        try:
            # 尝试解析为 JSON
            data = json.loads(input_str)
            # 格式化 JSON
            formatted = json.dumps(data, ensure_ascii=False, indent=2)
            # 限制长度
            if len(formatted) > 200:
                formatted = formatted[:200] + "..."
            return formatted
        except:
            # 如果不是 JSON，直接返回（限制长度）
            if len(input_str) > 200:
                return input_str[:200] + "..."
            return input_str

    def _format_output(self, output_str: str) -> str:
        """
        格式化输出结果
        
        Args:
            output_str: 输出结果字符串
            
        Returns:
            str: 格式化后的字符串
        """
        try:
            # 尝试解析为 JSON
            data = json.loads(output_str)
            # 格式化 JSON
            formatted = json.dumps(data, ensure_ascii=False, indent=2)
            # 限制长度
            if len(formatted) > 300:
                formatted = formatted[:300] + "..."
            return formatted
        except:
            # 如果不是 JSON，直接返回（限制长度）
            if len(output_str) > 300:
                return output_str[:300] + "..."
            return output_str
    
    def _update_animation(self) -> None:
        """更新动画效果"""
        if self.is_finished:
            self._animation_timer.stop()
            return
        
        # 更新点数（0-3）
        self._animation_dots = (self._animation_dots + 1) % 4
        dots = "." * self._animation_dots
        self.status_label.setText(f"执行中{dots}")
    
    def set_output(self, output_str: str) -> None:
        """
        设置工具输出结果
        
        Args:
            output_str: 输出结果字符串
        """
        self.output_str = output_str
        self.is_finished = True
        
        # 停止动画
        self._animation_timer.stop()
        
        # 更新状态
        self.status_label.setText("✓ 执行完成")
        self.status_label.setStyleSheet("color: #4CAF50;")
        
        # 显示输出结果
        self.output_label.show()
        self.output_content.setText(self._format_output(output_str))
        self.output_content.show()
        
        # 更新样式
        self._apply_style()
        
        logger.debug(f"工具调用完成: {self.tool_name}")
