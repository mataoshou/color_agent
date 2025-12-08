"""
LangChain 工具基类

提供文件操作工具的基础功能。
"""

import os
from typing import Optional
from pathlib import Path


class BaseFileTool:
    """文件操作工具基类"""
    
    def __init__(self, working_directory: str, max_file_size: int = 10 * 1024 * 1024,
                 allowed_formats: Optional[list] = None):
        """
        初始化文件工具
        
        Args:
            working_directory: 工作目录
            max_file_size: 最大文件大小（字节），默认 10MB
            allowed_formats: 允许的文件格式列表
        """
        self.working_directory = os.path.abspath(working_directory)
        self.max_file_size = max_file_size
        self.allowed_formats = allowed_formats or [
            ".txt", ".md", ".py", ".js", ".json", ".yaml", ".yml",
            ".html", ".css", ".xml", ".csv", ".log", ".sh", ".bat"
        ]
    
    def validate_path(self, path: str) -> tuple[bool, str]:
        """
        验证文件路径
        
        Args:
            path: 文件路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        try:
            # 解析为绝对路径
            abs_path = self._resolve_path(path)
            
            # 检查路径是否在工作目录内
            if not abs_path.startswith(self.working_directory):
                return False, f"路径 '{path}' 不在工作目录内"
            
            return True, ""
            
        except Exception as e:
            return False, f"路径验证失败: {str(e)}"
    
    def validate_file_size(self, file_path: str) -> tuple[bool, str]:
        """
        验证文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        try:
            abs_path = self._resolve_path(file_path)
            
            if not os.path.exists(abs_path):
                return True, ""  # 文件不存在时不检查大小
            
            file_size = os.path.getsize(abs_path)
            if file_size > self.max_file_size:
                max_mb = self.max_file_size / (1024 * 1024)
                actual_mb = file_size / (1024 * 1024)
                return False, f"文件大小 {actual_mb:.2f}MB 超过限制 {max_mb:.2f}MB"
            
            return True, ""
            
        except Exception as e:
            return False, f"文件大小检查失败: {str(e)}"
    
    def validate_file_format(self, file_path: str) -> tuple[bool, str]:
        """
        验证文件格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        try:
            _, ext = os.path.splitext(file_path)
            
            if not ext:
                return False, "文件没有扩展名"
            
            if ext.lower() not in self.allowed_formats:
                return False, f"不支持的文件格式 '{ext}'，支持的格式: {', '.join(self.allowed_formats)}"
            
            return True, ""
            
        except Exception as e:
            return False, f"文件格式检查失败: {str(e)}"
    
    def _resolve_path(self, path: str) -> str:
        """
        解析路径为绝对路径
        
        Args:
            path: 相对或绝对路径
            
        Returns:
            str: 绝对路径
        """
        if os.path.isabs(path):
            return os.path.abspath(path)
        
        # 相对于工作目录的路径
        return os.path.abspath(os.path.join(self.working_directory, path))
    
    def _get_relative_path(self, abs_path: str) -> str:
        """
        获取相对于工作目录的相对路径
        
        Args:
            abs_path: 绝对路径
            
        Returns:
            str: 相对路径
        """
        try:
            return os.path.relpath(abs_path, self.working_directory)
        except Exception:
            return abs_path
