"""
错误对话框模块

提供统一的错误提示对话框，用于向用户显示错误信息和提供操作选项。
支持不同类型的错误显示和自定义操作按钮。
"""

import logging
from typing import Optional, Callable
from PyQt6.QtWidgets import QMessageBox, QPushButton
from PyQt6.QtCore import Qt

from src.utils.errors import AgentError, ModelError, SessionError, FileError

logger = logging.getLogger(__name__)


class ErrorDialog:
    """
    错误对话框管理类
    
    提供静态方法用于显示不同类型的错误对话框，
    支持自定义按钮和回调函数。
    """
    
    @staticmethod
    def show_error(
        parent,
        title: str,
        message: str,
        detailed_text: Optional[str] = None,
        buttons: Optional[dict] = None
    ) -> str:
        """
        显示通用错误对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 错误消息
            detailed_text: 详细错误信息（可选）
            buttons: 自定义按钮字典 {按钮文本: 按钮角色}（可选）
        
        Returns:
            用户点击的按钮文本
        
        Examples:
            >>> ErrorDialog.show_error(
            ...     parent=self,
            ...     title="错误",
            ...     message="操作失败",
            ...     detailed_text="详细错误信息"
            ... )
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if detailed_text:
            msg_box.setDetailedText(detailed_text)
        
        # 添加自定义按钮
        if buttons:
            for button_text, button_role in buttons.items():
                msg_box.addButton(button_text, button_role)
        else:
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        msg_box.exec()
        clicked_button = msg_box.clickedButton()
        return clicked_button.text() if clicked_button else ""
    
    @staticmethod
    def show_model_error(
        parent,
        error: ModelError,
        retry_callback: Optional[Callable] = None,
        switch_model_callback: Optional[Callable] = None
    ) -> str:
        """
        显示模型错误对话框
        
        专门用于显示模型连接或调用失败的错误，
        提供"重试"和"选择其他模型"操作选项。
        
        Args:
            parent: 父窗口
            error: ModelError 错误对象
            retry_callback: 重试回调函数（可选）
            switch_model_callback: 切换模型回调函数（可选）
        
        Returns:
            用户点击的按钮文本
        
        Examples:
            >>> ErrorDialog.show_model_error(
            ...     parent=self,
            ...     error=model_error,
            ...     retry_callback=self.retry_connection,
            ...     switch_model_callback=self.open_model_settings
            ... )
        """
        logger.error(f"显示模型错误对话框: {error.message}")
        
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("模型连接失败")
        msg_box.setText(f"无法连接到 AI 模型服务\n\n{error.message}")
        
        # 添加详细错误信息
        if error.original_exception:
            msg_box.setDetailedText(str(error.original_exception))
        
        # 添加操作按钮
        retry_button = None
        switch_button = None
        
        if retry_callback:
            retry_button = msg_box.addButton("重试", QMessageBox.ButtonRole.AcceptRole)
        
        if switch_model_callback:
            switch_button = msg_box.addButton("选择其他模型", QMessageBox.ButtonRole.ActionRole)
        
        close_button = msg_box.addButton("关闭", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        clicked_button = msg_box.clickedButton()
        
        # 执行相应的回调函数
        if clicked_button == retry_button and retry_callback:
            retry_callback()
            return "重试"
        elif clicked_button == switch_button and switch_model_callback:
            switch_model_callback()
            return "选择其他模型"
        
        return "关闭"
    
    @staticmethod
    def show_session_error(
        parent,
        error: SessionError,
        session_name: Optional[str] = None
    ) -> str:
        """
        显示会话错误对话框
        
        用于显示会话加载、保存或恢复失败的错误。
        
        Args:
            parent: 父窗口
            error: SessionError 错误对象
            session_name: 会话名称（可选）
        
        Returns:
            用户点击的按钮文本
        
        Examples:
            >>> ErrorDialog.show_session_error(
            ...     parent=self,
            ...     error=session_error,
            ...     session_name="我的会话"
            ... )
        """
        logger.error(f"显示会话错误对话框: {error.message}")
        
        title = "会话错误"
        message = error.message
        
        if session_name:
            message = f"会话 '{session_name}' 操作失败\n\n{message}"
        
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if error.original_exception:
            msg_box.setDetailedText(str(error.original_exception))
        
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
        return "Ok"
    
    @staticmethod
    def show_file_error(
        parent,
        error: FileError,
        file_path: Optional[str] = None
    ) -> str:
        """
        显示文件错误对话框
        
        用于显示文件操作失败的错误。
        
        Args:
            parent: 父窗口
            error: FileError 错误对象
            file_path: 文件路径（可选）
        
        Returns:
            用户点击的按钮文本
        
        Examples:
            >>> ErrorDialog.show_file_error(
            ...     parent=self,
            ...     error=file_error,
            ...     file_path="/path/to/file.txt"
            ... )
        """
        logger.error(f"显示文件错误对话框: {error.message}")
        
        title = "文件操作失败"
        message = error.message
        
        if file_path:
            message = f"文件操作失败: {file_path}\n\n{message}"
        
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if error.original_exception:
            msg_box.setDetailedText(str(error.original_exception))
        
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
        return "Ok"
    
    @staticmethod
    def show_network_error(
        parent,
        message: str,
        retry_callback: Optional[Callable] = None
    ) -> str:
        """
        显示网络错误对话框
        
        用于显示网络连接失败或超时的错误，提供重试选项。
        
        Args:
            parent: 父窗口
            message: 错误消息
            retry_callback: 重试回调函数（可选）
        
        Returns:
            用户点击的按钮文本
        
        Examples:
            >>> ErrorDialog.show_network_error(
            ...     parent=self,
            ...     message="网络连接超时",
            ...     retry_callback=self.retry_request
            ... )
        """
        logger.error(f"显示网络错误对话框: {message}")
        
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("网络错误")
        msg_box.setText(f"网络连接失败\n\n{message}")
        
        # 添加操作按钮
        retry_button = None
        if retry_callback:
            retry_button = msg_box.addButton("重试", QMessageBox.ButtonRole.AcceptRole)
        
        close_button = msg_box.addButton("关闭", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        clicked_button = msg_box.clickedButton()
        
        # 执行重试回调
        if clicked_button == retry_button and retry_callback:
            retry_callback()
            return "重试"
        
        return "关闭"
    
    @staticmethod
    def show_warning(
        parent,
        title: str,
        message: str,
        detailed_text: Optional[str] = None
    ) -> str:
        """
        显示警告对话框
        
        用于显示警告信息，不影响正常运行但需要用户注意。
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 警告消息
            detailed_text: 详细信息（可选）
        
        Returns:
            用户点击的按钮文本
        """
        logger.warning(f"显示警告对话框: {message}")
        
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if detailed_text:
            msg_box.setDetailedText(detailed_text)
        
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
        return "Ok"
