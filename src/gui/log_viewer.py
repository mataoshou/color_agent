"""
日志查看器模块

提供日志查看窗口，用于显示和查询系统日志。
支持日志过滤、搜索和导出功能。
"""

import logging
import os
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QComboBox, QLineEdit, QLabel,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QFont

logger = logging.getLogger(__name__)


class LogViewer(QDialog):
    """
    日志查看器窗口
    
    提供日志文件的查看、过滤、搜索和导出功能。
    支持实时刷新和自动滚动。
    """
    
    def __init__(self, log_file_path: str, parent=None):
        """
        初始化日志查看器
        
        Args:
            log_file_path: 日志文件路径
            parent: 父窗口（可选）
        """
        super().__init__(parent)
        self.log_file_path = log_file_path
        self.auto_refresh = False
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_logs)
        
        self._init_ui()
        self._load_logs()
        
        logger.info(f"日志查看器已打开: {log_file_path}")
    
    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("日志查看器")
        self.setMinimumSize(800, 600)
        
        # 主布局
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 日志级别过滤
        toolbar_layout.addWidget(QLabel("级别:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(["全部", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_filter.currentTextChanged.connect(self._apply_filter)
        toolbar_layout.addWidget(self.level_filter)
        
        # 搜索框
        toolbar_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索...")
        self.search_input.textChanged.connect(self._apply_filter)
        toolbar_layout.addWidget(self.search_input)
        
        # 刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_logs)
        toolbar_layout.addWidget(self.refresh_button)
        
        # 自动刷新按钮
        self.auto_refresh_button = QPushButton("自动刷新: 关")
        self.auto_refresh_button.setCheckable(True)
        self.auto_refresh_button.clicked.connect(self._toggle_auto_refresh)
        toolbar_layout.addWidget(self.auto_refresh_button)
        
        # 清空按钮
        self.clear_button = QPushButton("清空显示")
        self.clear_button.clicked.connect(self._clear_display)
        toolbar_layout.addWidget(self.clear_button)
        
        # 导出按钮
        self.export_button = QPushButton("导出日志")
        self.export_button.clicked.connect(self._export_logs)
        toolbar_layout.addWidget(self.export_button)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # 设置等宽字体
        font = QFont("Courier New", 9)
        self.log_text.setFont(font)
        
        layout.addWidget(self.log_text)
        
        # 底部状态栏
        status_layout = QHBoxLayout()
        self.status_label = QLabel(f"日志文件: {self.log_file_path}")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.line_count_label = QLabel("行数: 0")
        status_layout.addWidget(self.line_count_label)
        
        layout.addLayout(status_layout)
        
        # 关闭按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _load_logs(self):
        """加载日志文件内容"""
        try:
            if not os.path.exists(self.log_file_path):
                self.log_text.setPlainText("日志文件不存在")
                self.line_count_label.setText("行数: 0")
                return
            
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.full_log_content = content
            self._apply_filter()
            
            logger.debug(f"日志文件已加载: {len(content)} 字符")
            
        except Exception as e:
            error_msg = f"无法读取日志文件: {str(e)}"
            self.log_text.setPlainText(error_msg)
            logger.error(error_msg, exc_info=e)
    
    def _apply_filter(self):
        """应用过滤条件"""
        if not hasattr(self, 'full_log_content'):
            return
        
        # 获取过滤条件
        level_filter = self.level_filter.currentText()
        search_text = self.search_input.text().lower()
        
        # 按行过滤
        lines = self.full_log_content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # 级别过滤
            if level_filter != "全部":
                if f"[{level_filter}]" not in line:
                    continue
            
            # 关键词搜索
            if search_text and search_text not in line.lower():
                continue
            
            filtered_lines.append(line)
        
        # 显示过滤后的内容
        filtered_content = '\n'.join(filtered_lines)
        self.log_text.setPlainText(filtered_content)
        
        # 更新行数
        self.line_count_label.setText(f"行数: {len(filtered_lines)}")
        
        # 滚动到底部
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
    
    def refresh_logs(self):
        """刷新日志内容"""
        self._load_logs()
        logger.debug("日志已刷新")
    
    def _toggle_auto_refresh(self, checked: bool):
        """切换自动刷新"""
        self.auto_refresh = checked
        
        if checked:
            self.auto_refresh_button.setText("自动刷新: 开")
            self.refresh_timer.start(2000)  # 每 2 秒刷新一次
            logger.info("自动刷新已启用")
        else:
            self.auto_refresh_button.setText("自动刷新: 关")
            self.refresh_timer.stop()
            logger.info("自动刷新已禁用")
    
    def _clear_display(self):
        """清空显示内容"""
        self.log_text.clear()
        self.line_count_label.setText("行数: 0")
        logger.debug("日志显示已清空")
    
    def _export_logs(self):
        """导出日志到文件"""
        try:
            # 打开文件保存对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出日志",
                f"logs_export_{self._get_timestamp()}.txt",
                "文本文件 (*.txt);;所有文件 (*.*)"
            )
            
            if not file_path:
                return
            
            # 保存当前显示的内容
            content = self.log_text.toPlainText()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            QMessageBox.information(
                self,
                "导出成功",
                f"日志已导出到:\n{file_path}"
            )
            
            logger.info(f"日志已导出到: {file_path}")
            
        except Exception as e:
            error_msg = f"导出日志失败: {str(e)}"
            QMessageBox.critical(self, "导出失败", error_msg)
            logger.error(error_msg, exc_info=e)
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止自动刷新
        if self.auto_refresh:
            self.refresh_timer.stop()
        
        logger.info("日志查看器已关闭")
        event.accept()
