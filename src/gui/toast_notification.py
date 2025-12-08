"""
非阻塞式通知消息框模块

提供类似 Toast 的非阻塞式通知消息框，
在屏幕右下角显示，自动消失，不影响用户操作。
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPalette, QColor

logger = logging.getLogger(__name__)


class ToastNotification(QWidget):
    """
    非阻塞式通知消息框
    
    在屏幕右下角显示通知消息，支持自动消失和淡入淡出动画。
    不阻塞用户操作，适合显示临时提示信息。
    """
    
    def __init__(
        self,
        title: str,
        message: str,
        level: str = "info",
        duration: int = 3000,
        parent: Optional[QWidget] = None
    ):
        """
        初始化通知消息框
        
        Args:
            title: 通知标题
            message: 通知消息
            level: 通知级别（info/warning/error）
            duration: 显示时长（毫秒）
            parent: 父窗口（可选）
        """
        super().__init__(parent)
        self.duration = duration
        self.level = level
        
        self._init_ui(title, message)
        self._setup_animation()
        
        logger.debug(f"创建 Toast 通知: {title} - {message}")
    
    def _init_ui(self, title: str, message: str):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # 设置固定宽度
        self.setFixedWidth(300)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #FFFFFF;
            }
        """)
        layout.addWidget(title_label)
        
        # 消息
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #FFFFFF;
            }
        """)
        layout.addWidget(message_label)
        
        self.setLayout(layout)
        
        # 设置背景颜色
        self._set_background_color()
    
    def _set_background_color(self):
        """根据通知级别设置背景颜色"""
        if self.level == "error":
            bg_color = "rgba(220, 53, 69, 0.9)"  # 红色
        elif self.level == "warning":
            bg_color = "rgba(255, 193, 7, 0.9)"  # 黄色
        else:
            bg_color = "rgba(40, 167, 69, 0.9)"  # 绿色
        
        self.setStyleSheet(f"""
            ToastNotification {{
                background-color: {bg_color};
                border-radius: 8px;
            }}
        """)
    
    def _setup_animation(self):
        """设置淡入淡出动画"""
        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        # 淡入动画
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # 淡出动画
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_out_animation.finished.connect(self.close)
        
        # 自动关闭定时器
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self._start_fade_out)
    
    def show_notification(self):
        """显示通知"""
        # 计算位置（屏幕右下角）
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.right() - self.width() - 20
            y = parent_geometry.bottom() - self.height() - 20
        else:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = screen.right() - self.width() - 20
            y = screen.bottom() - self.height() - 20
        
        self.move(x, y)
        
        # 显示窗口
        self.show()
        
        # 开始淡入动画
        self.fade_in_animation.start()
        
        # 启动自动关闭定时器
        self.close_timer.start(self.duration)
        
        logger.debug(f"Toast 通知已显示，位置: ({x}, {y})")
    
    def _start_fade_out(self):
        """开始淡出动画"""
        self.fade_out_animation.start()
    
    def mousePressEvent(self, event):
        """鼠标点击事件 - 点击关闭"""
        self._start_fade_out()


class ToastManager:
    """
    Toast 通知管理器
    
    管理多个 Toast 通知的显示位置和队列。
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化 Toast 管理器
        
        Args:
            parent: 父窗口（可选）
        """
        self.parent = parent
        self.active_toasts = []
        self.toast_spacing = 10  # Toast 之间的间距
        
        logger.info("Toast 管理器初始化")
    
    def show_toast(
        self,
        title: str,
        message: str,
        level: str = "info",
        duration: int = 3000
    ):
        """
        显示 Toast 通知
        
        Args:
            title: 通知标题
            message: 通知消息
            level: 通知级别（info/warning/error）
            duration: 显示时长（毫秒）
        """
        toast = ToastNotification(title, message, level, duration, self.parent)
        
        # 计算位置（考虑已有的 Toast）
        self._position_toast(toast)
        
        # 添加到活动列表
        self.active_toasts.append(toast)
        
        # 显示通知
        toast.show_notification()
        
        # 通知关闭时从列表移除
        toast.destroyed.connect(lambda: self._remove_toast(toast))
        
        logger.debug(f"Toast 通知已添加到队列: {title}")
    
    def show_info(self, title: str, message: str, duration: int = 3000):
        """显示信息通知"""
        self.show_toast(title, message, "info", duration)
    
    def show_warning(self, title: str, message: str, duration: int = 5000):
        """显示警告通知"""
        self.show_toast(title, message, "warning", duration)
    
    def show_error(self, title: str, message: str, duration: int = 5000):
        """显示错误通知"""
        self.show_toast(title, message, "error", duration)
    
    def _position_toast(self, toast: ToastNotification):
        """
        计算 Toast 的显示位置
        
        Args:
            toast: Toast 通知对象
        """
        if self.parent:
            parent_geometry = self.parent.geometry()
            base_x = parent_geometry.right() - toast.width() - 20
            base_y = parent_geometry.bottom() - toast.height() - 20
        else:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            base_x = screen.right() - toast.width() - 20
            base_y = screen.bottom() - toast.height() - 20
        
        # 计算垂直偏移（考虑已有的 Toast）
        offset = 0
        for existing_toast in self.active_toasts:
            if existing_toast.isVisible():
                offset += existing_toast.height() + self.toast_spacing
        
        toast.move(base_x, base_y - offset)
    
    def _remove_toast(self, toast: ToastNotification):
        """
        从活动列表移除 Toast
        
        Args:
            toast: Toast 通知对象
        """
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            logger.debug("Toast 通知已从队列移除")
