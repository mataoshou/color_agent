"""
通知管理模块

提供系统通知功能，包括：
- 系统托盘通知（QSystemTrayIcon）
- 非阻塞式通知消息框
- 通知历史记录

支持不同级别的通知（信息、警告、错误）。
"""

import logging
from typing import Optional, List
from datetime import datetime
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QWidget
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

logger = logging.getLogger(__name__)


class NotificationLevel:
    """通知级别枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Notification:
    """
    通知数据类
    
    Attributes:
        level: 通知级别
        title: 通知标题
        message: 通知消息
        timestamp: 通知时间戳
    """
    
    def __init__(self, level: str, title: str, message: str):
        self.level = level
        self.title = title
        self.message = message
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{time_str}] [{self.level.upper()}] {self.title}: {self.message}"


class NotificationManager(QObject):
    """
    通知管理器
    
    管理系统托盘通知和非阻塞式通知消息框，
    维护通知历史记录。
    
    Signals:
        notification_clicked: 通知被点击时发出
    """
    
    notification_clicked = pyqtSignal(Notification)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化通知管理器
        
        Args:
            parent: 父窗口（可选）
        """
        super().__init__(parent)
        self.parent_widget = parent
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.notification_history: List[Notification] = []
        self.max_history = 100  # 最多保留 100 条通知历史
        
        logger.info("通知管理器初始化")
    
    def setup_system_tray(self, icon: Optional[QIcon] = None, menu: Optional[QMenu] = None):
        """
        设置系统托盘图标
        
        Args:
            icon: 托盘图标（可选）
            menu: 托盘右键菜单（可选）
        
        Examples:
            >>> manager = NotificationManager()
            >>> manager.setup_system_tray(QIcon("app.png"))
        """
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("系统托盘不可用")
            return
        
        self.tray_icon = QSystemTrayIcon(self.parent_widget)
        
        # 设置图标
        if icon:
            self.tray_icon.setIcon(icon)
        
        # 设置右键菜单
        if menu:
            self.tray_icon.setContextMenu(menu)
        
        # 连接点击信号
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
        
        logger.info("系统托盘图标已设置")
    
    def show_notification(
        self,
        title: str,
        message: str,
        level: str = NotificationLevel.INFO,
        duration: int = 3000,
        use_tray: bool = True
    ):
        """
        显示通知
        
        Args:
            title: 通知标题
            message: 通知消息
            level: 通知级别（info/warning/error）
            duration: 显示时长（毫秒），默认 3000ms
            use_tray: 是否使用系统托盘通知，默认 True
        
        Examples:
            >>> manager.show_notification("成功", "操作完成", NotificationLevel.INFO)
            >>> manager.show_notification("警告", "配置文件不存在", NotificationLevel.WARNING)
        """
        # 创建通知对象
        notification = Notification(level, title, message)
        
        # 添加到历史记录
        self._add_to_history(notification)
        
        # 记录日志
        if level == NotificationLevel.ERROR:
            logger.error(f"通知: {title} - {message}")
        elif level == NotificationLevel.WARNING:
            logger.warning(f"通知: {title} - {message}")
        else:
            logger.info(f"通知: {title} - {message}")
        
        # 显示系统托盘通知
        if use_tray and self.tray_icon and self.tray_icon.isVisible():
            icon = self._get_icon_for_level(level)
            self.tray_icon.showMessage(title, message, icon, duration)
        
        logger.debug(f"显示通知: {title} - {message}")
    
    def show_info(self, title: str, message: str, duration: int = 3000):
        """
        显示信息通知
        
        Args:
            title: 通知标题
            message: 通知消息
            duration: 显示时长（毫秒）
        """
        self.show_notification(title, message, NotificationLevel.INFO, duration)
    
    def show_warning(self, title: str, message: str, duration: int = 5000):
        """
        显示警告通知
        
        Args:
            title: 通知标题
            message: 通知消息
            duration: 显示时长（毫秒）
        """
        self.show_notification(title, message, NotificationLevel.WARNING, duration)
    
    def show_error(self, title: str, message: str, duration: int = 5000):
        """
        显示错误通知
        
        Args:
            title: 通知标题
            message: 通知消息
            duration: 显示时长（毫秒）
        """
        self.show_notification(title, message, NotificationLevel.ERROR, duration)
    
    def get_notification_history(self) -> List[Notification]:
        """
        获取通知历史记录
        
        Returns:
            通知列表，按时间倒序排列
        """
        return list(reversed(self.notification_history))
    
    def clear_history(self):
        """清空通知历史记录"""
        self.notification_history.clear()
        logger.info("通知历史已清空")
    
    def hide_tray_icon(self):
        """隐藏系统托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()
            logger.info("系统托盘图标已隐藏")
    
    def show_tray_icon(self):
        """显示系统托盘图标"""
        if self.tray_icon:
            self.tray_icon.show()
            logger.info("系统托盘图标已显示")
    
    def _add_to_history(self, notification: Notification):
        """
        添加通知到历史记录
        
        Args:
            notification: 通知对象
        """
        self.notification_history.append(notification)
        
        # 限制历史记录数量
        if len(self.notification_history) > self.max_history:
            self.notification_history.pop(0)
    
    def _get_icon_for_level(self, level: str) -> QSystemTrayIcon.MessageIcon:
        """
        根据通知级别获取图标
        
        Args:
            level: 通知级别
        
        Returns:
            QSystemTrayIcon.MessageIcon
        """
        if level == NotificationLevel.ERROR:
            return QSystemTrayIcon.MessageIcon.Critical
        elif level == NotificationLevel.WARNING:
            return QSystemTrayIcon.MessageIcon.Warning
        else:
            return QSystemTrayIcon.MessageIcon.Information
    
    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """
        托盘图标激活事件处理
        
        Args:
            reason: 激活原因
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 单击托盘图标
            logger.debug("托盘图标被点击")
            if self.parent_widget:
                self.parent_widget.show()
                self.parent_widget.activateWindow()
