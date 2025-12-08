"""
系统上下文提供者模块

提供系统信息，包括工作目录、操作系统类型和版本、Python 版本等。
"""

import os
import sys
import platform
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class SystemContext:
    """系统上下文数据类"""
    working_directory: str
    os_type: str
    os_version: str
    python_version: str
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'working_directory': self.working_directory,
            'os_type': self.os_type,
            'os_version': self.os_version,
            'python_version': self.python_version
        }
    
    def to_prompt_text(self) -> str:
        """转换为 Prompt 文本"""
        return f"""系统上下文信息：
- 当前工作目录: {self.working_directory}
- 操作系统: {self.os_type} {self.os_version}
- Python 版本: {self.python_version}"""


class SystemContextProvider:
    """系统上下文提供者"""
    
    def __init__(self, working_directory: Optional[str] = None):
        """
        初始化系统上下文提供者
        
        Args:
            working_directory: 工作目录路径，如果为 None 则使用当前目录
        """
        self._working_directory = working_directory or os.getcwd()
        self._os_type = self._get_os_type()
        self._os_version = self._get_os_version()
        self._python_version = self._get_python_version()
    
    def get_context(self) -> SystemContext:
        """
        获取系统上下文
        
        Returns:
            SystemContext: 系统上下文对象
        """
        return SystemContext(
            working_directory=self._working_directory,
            os_type=self._os_type,
            os_version=self._os_version,
            python_version=self._python_version
        )
    
    def get_working_directory(self) -> str:
        """
        获取当前工作目录
        
        Returns:
            str: 工作目录路径
        """
        return self._working_directory
    
    def set_working_directory(self, directory: str) -> bool:
        """
        设置工作目录
        
        Args:
            directory: 新的工作目录路径
            
        Returns:
            bool: 设置是否成功
        """
        # 验证目录是否存在
        if not os.path.exists(directory):
            return False
        
        if not os.path.isdir(directory):
            return False
        
        # 转换为绝对路径
        abs_path = os.path.abspath(directory)
        self._working_directory = abs_path
        
        return True
    
    def get_os_info(self) -> tuple[str, str]:
        """
        获取操作系统信息
        
        Returns:
            tuple: (操作系统类型, 操作系统版本)
        """
        return self._os_type, self._os_version
    
    def get_python_version(self) -> str:
        """
        获取 Python 版本
        
        Returns:
            str: Python 版本
        """
        return self._python_version
    
    def _get_os_type(self) -> str:
        """
        获取操作系统类型
        
        Returns:
            str: 操作系统类型 (Darwin, Linux, Windows)
        """
        return platform.system()
    
    def _get_os_version(self) -> str:
        """
        获取操作系统版本
        
        Returns:
            str: 操作系统版本
        """
        try:
            if platform.system() == 'Darwin':
                # macOS
                return f"macOS {platform.mac_ver()[0]}"
            elif platform.system() == 'Linux':
                # Linux
                return f"{platform.system()} {platform.release()}"
            elif platform.system() == 'Windows':
                # Windows
                return f"Windows {platform.release()}"
            else:
                return platform.release()
        except Exception:
            return "Unknown"
    
    def _get_python_version(self) -> str:
        """
        获取 Python 版本
        
        Returns:
            str: Python 版本
        """
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def validate_path(self, path: str) -> bool:
        """
        验证路径是否在工作目录内
        
        Args:
            path: 要验证的路径
            
        Returns:
            bool: 路径是否有效
        """
        try:
            # 转换为绝对路径
            abs_path = os.path.abspath(path)
            abs_working_dir = os.path.abspath(self._working_directory)
            
            # 检查路径是否在工作目录内
            return abs_path.startswith(abs_working_dir)
        except Exception:
            return False
    
    def resolve_path(self, path: str) -> str:
        """
        解析相对路径为绝对路径
        
        Args:
            path: 相对或绝对路径
            
        Returns:
            str: 绝对路径
        """
        if os.path.isabs(path):
            return path
        
        # 相对于工作目录的路径
        return os.path.join(self._working_directory, path)
    
    def get_relative_path(self, abs_path: str) -> str:
        """
        获取相对于工作目录的相对路径
        
        Args:
            abs_path: 绝对路径
            
        Returns:
            str: 相对路径
        """
        try:
            return os.path.relpath(abs_path, self._working_directory)
        except Exception:
            return abs_path
