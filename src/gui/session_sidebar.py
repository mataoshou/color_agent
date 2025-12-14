"""
会话侧边栏组件

显示会话列表，支持新建、切换、删除和重命名会话。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem, QInputDialog, QMessageBox, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from typing import List, Dict, Any, Optional
import logging

from .session_item import SessionItemWidget

logger = logging.getLogger(__name__)


class SessionSidebar(QWidget):
    """会话侧边栏组件"""
    
    # 信号定义
    session_created = pyqtSignal(str)  # 创建会话信号，携带会话名称
    session_selected = pyqtSignal(str)  # 选择会话信号，携带 session_id
    session_deleted = pyqtSignal(str)  # 删除会话信号，携带 session_id
    session_renamed = pyqtSignal(str, str)  # 重命名会话信号，携带 session_id 和新名称
    
    def __init__(self, parent=None):
        """
        初始化会话侧边栏
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        self.current_session_id: Optional[str] = None
        self.session_widgets: Dict[str, SessionItemWidget] = {}
        
        self._init_ui()
        
        logger.info("SessionSidebar 初始化完成")
    
    def _init_ui(self):
        """初始化 UI"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # 顶部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 5)
        
        # 新建会话按钮
        self.new_session_btn = QPushButton("+ 新建会话")
        self.new_session_btn.setMinimumHeight(35)
        self.new_session_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.new_session_btn.clicked.connect(self._on_new_session_clicked)
        
        button_layout.addWidget(self.new_session_btn)
        
        main_layout.addLayout(button_layout)
        
        # 会话列表
        self.session_list = QListWidget()
        self.session_list.setSpacing(4)
        self.session_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)  # 禁用默认选中
        self.session_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # 禁用焦点
        
        # 设置大小策略，确保列表能够垂直扩展
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.session_list.setSizePolicy(size_policy)
        
        # 启用垂直滚动条
        self.session_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.session_list.setStyleSheet("""
            QListWidget {
                background-color: #fafafa;
                border: none;
                outline: none;
                padding: 5px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
            QListWidget::item:hover {
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
        """)
        
        # 设置右键菜单策略
        self.session_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self._show_context_menu)
        
        # 添加会话列表到布局，并设置垂直拉伸因子为1，确保它占据剩余空间
        main_layout.addWidget(self.session_list, 1)
        
        self.setLayout(main_layout)
        
        # 设置最小宽度
        self.setMinimumWidth(250)
    
    def _on_new_session_clicked(self):
        """新建会话按钮点击事件"""
        # 显示输入对话框
        name, ok = QInputDialog.getText(
            self,
            "新建会话",
            "请输入会话名称:",
            text=f"新会话"
        )
        
        if ok and name.strip():
            logger.info(f"用户创建新会话: {name}")
            self.session_created.emit(name.strip())
    
    def add_session(self, session_data: Dict[str, Any]):
        """
        添加会话到列表
        
        Args:
            session_data: 会话数据字典
        """
        session_id = session_data.get('session_id', '')
        
        # 创建会话项组件
        session_widget = SessionItemWidget(session_data)
        session_widget.clicked.connect(self._on_session_clicked)
        
        # 创建列表项
        item = QListWidgetItem(self.session_list)
        
        # 设置一个合理的最小高度，确保内容能显示完整
        min_height = 80  # 增加最小高度以容纳多行内容
        size_hint = session_widget.sizeHint()
        if size_hint.height() < min_height:
            size_hint.setHeight(min_height)
        
        item.setSizeHint(size_hint)
        item.setData(Qt.ItemDataRole.UserRole, session_id)
        
        # 将组件设置为列表项的 widget
        self.session_list.addItem(item)
        self.session_list.setItemWidget(item, session_widget)
        
        # 强制更新项目大小以适应内容
        session_widget.adjustSize()
        item.setSizeHint(session_widget.sizeHint())
        
        # 保存引用
        self.session_widgets[session_id] = session_widget
        
        logger.debug(f"添加会话到列表: {session_id}")
    
    def load_sessions(self, sessions: List[Dict[str, Any]]):
        """
        加载会话列表
        
        Args:
            sessions: 会话数据列表
        """
        # 清空现有列表
        self.clear_sessions()
        
        # 添加所有会话
        for session_data in sessions:
            self.add_session(session_data)
        
        logger.info(f"加载会话列表: 共 {len(sessions)} 个会话")
        
        # 如果有会话，总是选中第一个会话（无论是新创建的还是已有的）
        if sessions:
            first_session_id = sessions[0].get('session_id', '')
            if first_session_id:
                self.set_selected_session(first_session_id)
                self.session_selected.emit(first_session_id)
                logger.info(f"选中第一个会话: {first_session_id}")
    
    def clear_sessions(self):
        """清空会话列表"""
        self.session_list.clear()
        self.session_widgets.clear()
        self.current_session_id = None
        
        logger.debug("清空会话列表")
    
    def _on_session_clicked(self, session_id: str):
        """
        会话项点击事件
        
        Args:
            session_id: 会话 ID
        """
        # 更新选中状态
        self.set_selected_session(session_id)
        
        # 发出选择信号
        self.session_selected.emit(session_id)
        
        logger.info(f"选择会话: {session_id}")
    
    def set_selected_session(self, session_id: str):
        """
        设置选中的会话
        
        Args:
            session_id: 会话 ID
        """
        # 取消之前的选中状态
        if self.current_session_id and self.current_session_id in self.session_widgets:
            self.session_widgets[self.current_session_id].set_selected(False)
        
        # 设置新的选中状态
        if session_id in self.session_widgets:
            self.session_widgets[session_id].set_selected(True)
            self.current_session_id = session_id
    
    def _show_context_menu(self, position):
        """
        显示右键菜单
        
        Args:
            position: 鼠标位置
        """
        # 获取点击的项
        item = self.session_list.itemAt(position)
        if item is None:
            return
        
        session_id = item.data(Qt.ItemDataRole.UserRole)
        
        # 创建右键菜单
        menu = QMenu(self)
        
        # 重命名操作
        rename_action = menu.addAction("重命名")
        rename_action.triggered.connect(lambda: self._on_rename_session(session_id))
        
        # 删除操作
        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(lambda: self._on_delete_session(session_id))
        
        # 显示菜单
        menu.exec(self.session_list.mapToGlobal(position))
    
    def _on_rename_session(self, session_id: str):
        """
        重命名会话
        
        Args:
            session_id: 会话 ID
        """
        # 获取当前名称
        current_name = ""
        if session_id in self.session_widgets:
            current_name = self.session_widgets[session_id].session_name
        
        # 显示输入对话框
        new_name, ok = QInputDialog.getText(
            self,
            "重命名会话",
            "请输入新的会话名称:",
            text=current_name
        )
        
        if ok and new_name.strip() and new_name.strip() != current_name:
            logger.info(f"重命名会话: {session_id} -> {new_name}")
            self.session_renamed.emit(session_id, new_name.strip())
    
    def _on_delete_session(self, session_id: str):
        """
        删除会话（直接删除，无确认）
        
        Args:
            session_id: 会话 ID
        """
        # 直接删除，不显示确认对话框
        logger.info(f"删除会话: {session_id}")
        self.session_deleted.emit(session_id)
    
    def remove_session(self, session_id: str):
        """
        从列表中移除会话
        
        Args:
            session_id: 会话 ID
        """
        # 查找并移除列表项
        for i in range(self.session_list.count()):
            item = self.session_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == session_id:
                self.session_list.takeItem(i)
                break
        
        # 移除组件引用
        if session_id in self.session_widgets:
            del self.session_widgets[session_id]
        
        # 如果删除的是当前会话，清空当前会话
        if self.current_session_id == session_id:
            self.current_session_id = None
        
        logger.debug(f"从列表移除会话: {session_id}")
    
    def update_session(self, session_data: Dict[str, Any]):
        """
        更新会话信息
        
        Args:
            session_data: 会话数据字典
        """
        session_id = session_data.get('session_id', '')
        
        if session_id in self.session_widgets:
            self.session_widgets[session_id].update_data(session_data)
            logger.debug(f"更新会话信息: {session_id}")
    
    def get_current_session_id(self) -> Optional[str]:
        """
        获取当前选中的会话 ID
        
        Returns:
            str: 当前会话 ID，如果没有返回 None
        """
        return self.current_session_id
