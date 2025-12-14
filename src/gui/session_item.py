"""
会话列表项自定义组件

显示会话名称、时间戳和最新消息预览。
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SessionItemWidget(QWidget):
    """会话列表项自定义组件"""
    
    clicked = pyqtSignal(str)  # 点击信号，携带 session_id
    
    def __init__(self, session_data: Dict[str, Any], parent=None):
        """
        初始化会话列表项
        
        Args:
            session_data: 会话数据字典，包含 session_id, name, updated_at, preview 等
            parent: 父组件
        """
        super().__init__(parent)
        
        self.session_id = session_data.get('session_id', '')
        self.session_name = session_data.get('name', '未命名会话')
        self.updated_at = session_data.get('updated_at', '')
        self.preview = session_data.get('preview', '暂无消息')
        self.is_corrupted = session_data.get('corrupted', False)
        self.is_selected = False
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # 增加边距，让内容有更多空间
        main_layout.setSpacing(4)
        
        # 第一行：会话名称和时间
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)
        
        # 会话名称标签
        self.name_label = QLabel(self.session_name)
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        # 设置自动换行，当内容过长时自动换行显示
        self.name_label.setWordWrap(True)
        self.name_label.setMinimumWidth(0)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # 如果是损坏的会话，显示红色
        if self.is_corrupted:
            self.name_label.setStyleSheet("color: #e74c3c;")
        
        top_layout.addWidget(self.name_label)
        top_layout.addStretch()
        
        # 时间标签
        self.time_label = QLabel(self._format_time(self.updated_at))
        time_font = QFont()
        time_font.setPointSize(9)
        self.time_label.setFont(time_font)
        self.time_label.setStyleSheet("color: #7f8c8d;")
        
        top_layout.addWidget(self.time_label)
        
        main_layout.addLayout(top_layout)
        
        # 第二行：消息预览
        self.preview_label = QLabel(self.preview)
        preview_font = QFont()
        preview_font.setPointSize(10)
        self.preview_label.setFont(preview_font)
        self.preview_label.setStyleSheet("color: #95a5a6;")
        self.preview_label.setWordWrap(True)
        
        main_layout.addWidget(self.preview_label)
        
        self.setLayout(main_layout)
        
        # 设置最小高度，确保内容能完整显示
        self.setMinimumHeight(60)
        
        # 设置默认样式
        self._update_style()
        
        # 设置鼠标光标
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 设置对象名称以便在样式表中使用 ID 选择器
        self.setObjectName("sessionItem")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def _format_time(self, timestamp: str) -> str:
        """
        格式化时间戳
        
        Args:
            timestamp: ISO 格式的时间戳
            
        Returns:
            str: 格式化后的时间字符串
        """
        if not timestamp:
            return ""
        
        try:
            dt = datetime.fromisoformat(timestamp)
            now = datetime.now()
            
            # 计算时间差
            delta = now - dt
            
            # 今天
            if delta.days == 0:
                if delta.seconds < 60:
                    return "刚刚"
                elif delta.seconds < 3600:
                    minutes = delta.seconds // 60
                    return f"{minutes}分钟前"
                else:
                    hours = delta.seconds // 3600
                    return f"{hours}小时前"
            # 昨天
            elif delta.days == 1:
                return "昨天"
            # 一周内
            elif delta.days < 7:
                return f"{delta.days}天前"
            # 更早
            else:
                return dt.strftime("%Y-%m-%d")
                
        except Exception:
            return timestamp
    
    def set_selected(self, selected: bool):
        """
        设置选中状态
        
        Args:
            selected: 是否选中
        """
        logger.info(f"SessionItem {self.session_id}: set_selected({selected})")
        self.is_selected = selected
        self._update_style()
        self.update()  # 强制重绘
        logger.info(f"SessionItem {self.session_id}: 样式更新完成，is_selected={self.is_selected}")
    
    def _update_style(self):
        """更新样式"""
        logger.debug(f"SessionItem {self.session_id}: _update_style called, is_selected={self.is_selected}")
        
        if self.is_selected:
            # 选中状态 - 使用更柔和的蓝色渐变背景
            logger.debug(f"SessionItem {self.session_id}: 应用选中样式")
            self.setStyleSheet("""
                #sessionItem {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 #e3f2fd, stop:1 #bbdefb);
                    border-radius: 8px;
                    border-left: 3px solid #2196F3;
                    padding-left: 7px;
                }
            """)
            self.name_label.setStyleSheet("color: #1565C0; font-weight: bold;")
            self.time_label.setStyleSheet("color: #1976D2;")
            self.preview_label.setStyleSheet("color: #42A5F5;")
        else:
            # 未选中状态
            logger.debug(f"SessionItem {self.session_id}: 应用未选中样式")
            self.setStyleSheet("""
                #sessionItem {
                    background-color: white;
                    border-radius: 8px;
                    border-left: 3px solid transparent;
                    padding-left: 7px;
                }
                #sessionItem:hover {
                    background-color: #f5f5f5;
                    border-left: 3px solid #e0e0e0;
                }
            """)
            
            if self.is_corrupted:
                self.name_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            else:
                self.name_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
            
            self.time_label.setStyleSheet("color: #9e9e9e;")
            self.preview_label.setStyleSheet("color: #bdbdbd;")
        
        # 强制重绘以应用样式
        self.repaint()
        logger.debug(f"SessionItem {self.session_id}: repaint() 调用完成")
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.session_id)
        super().mousePressEvent(event)
    
    def update_data(self, session_data: Dict[str, Any]):
        """
        更新会话数据
        
        Args:
            session_data: 新的会话数据
        """
        self.session_id = session_data.get('session_id', self.session_id)
        self.session_name = session_data.get('name', self.session_name)
        self.updated_at = session_data.get('updated_at', self.updated_at)
        self.preview = session_data.get('preview', self.preview)
        self.is_corrupted = session_data.get('corrupted', False)
        
        # 更新 UI
        self.name_label.setText(self.session_name)
        self.time_label.setText(self._format_time(self.updated_at))
        self.preview_label.setText(self.preview)
        
        # 更新样式
        self._update_style()
