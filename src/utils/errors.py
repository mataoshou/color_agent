"""
错误类定义模块

定义系统中使用的所有自定义错误类型，包括：
- AgentError: 基础错误类
- ModelError: 模型相关错误
- SessionError: 会话相关错误
- FileError: 文件操作相关错误

所有错误类都继承自 AgentError，并自动记录错误日志。
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AgentError(Exception):
    """
    Agent 系统基础错误类
    
    所有自定义错误的基类，提供统一的错误处理和日志记录功能。
    
    Attributes:
        message: 错误消息
        original_exception: 原始异常对象（可选）
    """
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        """
        初始化错误对象
        
        Args:
            message: 错误消息描述
            original_exception: 导致此错误的原始异常（可选）
        """
        self.message = message
        self.original_exception = original_exception
        super().__init__(self.message)
        
        # 自动记录错误日志
        if original_exception:
            logger.error(f"{self.__class__.__name__}: {message}", exc_info=original_exception)
        else:
            logger.error(f"{self.__class__.__name__}: {message}")
    
    def __str__(self) -> str:
        """返回错误的字符串表示"""
        if self.original_exception:
            return f"{self.message} (原因: {str(self.original_exception)})"
        return self.message


class ModelError(AgentError):
    """
    模型相关错误
    
    用于表示与 AI 模型交互过程中发生的错误，包括：
    - 模型连接失败
    - API 调用失败
    - 响应解析失败
    - 模型配置无效
    
    Examples:
        >>> raise ModelError("无法连接到 OpenAI API")
        >>> raise ModelError("API 调用超时", original_exception=timeout_error)
    """
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        """
        初始化模型错误
        
        Args:
            message: 错误消息描述
            original_exception: 导致此错误的原始异常（可选）
        """
        super().__init__(message, original_exception)


class SessionError(AgentError):
    """
    会话相关错误
    
    用于表示会话管理过程中发生的错误，包括：
    - 会话创建失败
    - 会话加载失败
    - 会话保存失败
    - 会话文件损坏
    
    Examples:
        >>> raise SessionError("会话文件不存在")
        >>> raise SessionError("会话保存失败", original_exception=io_error)
    """
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        """
        初始化会话错误
        
        Args:
            message: 错误消息描述
            original_exception: 导致此错误的原始异常（可选）
        """
        super().__init__(message, original_exception)


class FileError(AgentError):
    """
    文件操作相关错误
    
    用于表示文件操作过程中发生的错误，包括：
    - 文件读取失败
    - 文件写入失败
    - 文件权限错误
    - 文件格式不支持
    
    Examples:
        >>> raise FileError("文件不存在: /path/to/file")
        >>> raise FileError("文件权限不足", original_exception=permission_error)
    """
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        """
        初始化文件错误
        
        Args:
            message: 错误消息描述
            original_exception: 导致此错误的原始异常（可选）
        """
        super().__init__(message, original_exception)
