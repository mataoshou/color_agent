"""
文件浏览器组件

提供文件树展示、工作目录选择和文件查看功能。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTreeView, QFileDialog, QDialog, QTextEdit, QLabel,
    QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QDir, QMimeData, QUrl
from PyQt6.QtGui import QFileSystemModel, QAction, QDragEnterEvent, QDropEvent
import os
import logging

logger = logging.getLogger(__name__)


class FileViewerDialog(QDialog):
    """文件查看对话框"""
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.init_ui()
        self.load_file()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle(f"查看文件 - {os.path.basename(self.file_path)}")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # 文件路径标签
        path_label = QLabel(f"文件路径: {self.file_path}")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        # 文本编辑器（只读）
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.text_edit)
        
        # 关闭按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_file(self):
        """加载文件内容"""
        try:
            # 尝试以文本方式读取文件
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_edit.setPlainText(content)
            logger.info(f"成功加载文件: {self.file_path}")
        except UnicodeDecodeError:
            # 如果 UTF-8 解码失败，尝试其他编码
            try:
                with open(self.file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                self.text_edit.setPlainText(content)
                logger.info(f"使用 GBK 编码加载文件: {self.file_path}")
            except Exception as e:
                error_msg = f"无法读取文件（可能是二进制文件）: {str(e)}"
                self.text_edit.setPlainText(error_msg)
                logger.error(f"文件读取失败: {self.file_path}, 错误: {str(e)}")
        except Exception as e:
            error_msg = f"读取文件时出错: {str(e)}"
            self.text_edit.setPlainText(error_msg)
            logger.error(f"文件读取失败: {self.file_path}, 错误: {str(e)}")


class FileBrowser(QWidget):
    """
    文件浏览器组件
    
    提供文件树展示、工作目录选择和文件查看功能。
    
    Signals:
        directory_changed: 工作目录变更信号，携带新目录路径
        file_selected: 文件选中信号，携带文件路径
        ai_read_requested: 请求 AI 阅读文件信号，携带文件路径
        ai_modify_requested: 请求 AI 修改文件信号，携带文件路径
    """
    
    # 信号定义
    directory_changed = pyqtSignal(str)  # 工作目录变更
    file_selected = pyqtSignal(str)  # 文件选中
    ai_read_requested = pyqtSignal(str)  # 请求 AI 阅读文件
    ai_modify_requested = pyqtSignal(str)  # 请求 AI 修改文件
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_directory = os.getcwd()
        self.file_system_model = None
        self.tree_view = None
        
        # 启用拖放
        self.setAcceptDrops(True)
        
        self.init_ui()
        logger.info("FileBrowser 初始化完成")
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        
        # 工作目录选择按钮
        self.select_dir_button = QPushButton("选择目录")
        self.select_dir_button.clicked.connect(self.on_select_directory)
        toolbar_layout.addWidget(self.select_dir_button)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 当前目录标签
        self.dir_label = QLabel(f"当前目录: {self.current_directory}")
        self.dir_label.setWordWrap(True)
        layout.addWidget(self.dir_label)
        
        # 文件树视图
        self.tree_view = QTreeView()
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        
        # 启用右键菜单
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # 设置文件系统模型
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())
        self.tree_view.setModel(self.file_system_model)
        
        # 设置根目录
        self.set_root_directory(self.current_directory)
        
        # 隐藏不需要的列（只显示名称列）
        self.tree_view.setColumnWidth(0, 250)
        for i in range(1, self.file_system_model.columnCount()):
            self.tree_view.hideColumn(i)
        
        # 双击事件
        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.tree_view)
        
        self.setLayout(layout)
    
    def set_root_directory(self, directory: str):
        """
        设置根目录
        
        Args:
            directory: 目录路径
        """
        if os.path.isdir(directory):
            self.current_directory = os.path.abspath(directory)
            index = self.file_system_model.setRootPath(self.current_directory)
            self.tree_view.setRootIndex(index)
            self.dir_label.setText(f"当前目录: {self.current_directory}")
            logger.info(f"设置根目录: {self.current_directory}")
        else:
            logger.warning(f"无效的目录路径: {directory}")
    
    def on_select_directory(self):
        """选择工作目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择工作目录",
            self.current_directory,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            old_directory = self.current_directory
            self.set_root_directory(directory)
            
            # 发出目录变更信号
            self.directory_changed.emit(self.current_directory)
            logger.info(f"工作目录从 {old_directory} 变更为 {self.current_directory}")
    
    def on_item_double_clicked(self, index):
        """
        处理项目双击事件
        
        Args:
            index: 模型索引
        """
        file_path = self.file_system_model.filePath(index)
        
        # 如果是文件，打开查看对话框
        if os.path.isfile(file_path):
            logger.info(f"双击文件: {file_path}")
            self.file_selected.emit(file_path)
            self.show_file_viewer(file_path)
        else:
            logger.debug(f"双击目录: {file_path}")
    
    def show_file_viewer(self, file_path: str):
        """
        显示文件查看对话框
        
        Args:
            file_path: 文件路径
        """
        try:
            dialog = FileViewerDialog(file_path, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"无法打开文件: {str(e)}"
            )
            logger.error(f"打开文件查看器失败: {file_path}, 错误: {str(e)}")
    
    def get_current_directory(self) -> str:
        """
        获取当前工作目录
        
        Returns:
            当前工作目录路径
        """
        return self.current_directory
    
    def show_context_menu(self, position):
        """
        显示右键上下文菜单
        
        Args:
            position: 鼠标位置
        """
        # 获取选中的索引
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
        
        file_path = self.file_system_model.filePath(index)
        
        # 只为文件显示菜单
        if not os.path.isfile(file_path):
            return
        
        # 创建上下文菜单
        menu = QMenu(self)
        
        # 添加"让 AI 阅读"菜单项
        read_action = QAction("让 AI 阅读", self)
        read_action.triggered.connect(lambda: self.on_ai_read_file(file_path))
        menu.addAction(read_action)
        
        # 添加"让 AI 修改"菜单项
        modify_action = QAction("让 AI 修改", self)
        modify_action.triggered.connect(lambda: self.on_ai_modify_file(file_path))
        menu.addAction(modify_action)
        
        # 显示菜单
        menu.exec(self.tree_view.viewport().mapToGlobal(position))
        logger.debug(f"显示文件上下文菜单: {file_path}")
    
    def on_ai_read_file(self, file_path: str):
        """
        处理"让 AI 阅读"操作
        
        Args:
            file_path: 文件路径
        """
        logger.info(f"请求 AI 阅读文件: {file_path}")
        self.ai_read_requested.emit(file_path)
    
    def on_ai_modify_file(self, file_path: str):
        """
        处理"让 AI 修改"操作
        
        Args:
            file_path: 文件路径
        """
        logger.info(f"请求 AI 修改文件: {file_path}")
        self.ai_modify_requested.emit(file_path)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        处理拖拽进入事件
        
        Args:
            event: 拖拽事件
        """
        # 检查是否包含文件 URL
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            logger.debug("接受文件拖拽")
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """
        处理拖放事件
        
        Args:
            event: 拖放事件
        """
        # 获取拖放的文件
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            urls = mime_data.urls()
            for url in urls:
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    logger.info(f"拖放文件: {file_path}")
                    # 发出 AI 阅读请求信号
                    self.ai_read_requested.emit(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()
