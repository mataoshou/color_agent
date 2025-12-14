"""
日志系统模块

提供日志配置和初始化功能，支持文件和控制台双输出。
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional


class LoggerManager:
    """日志管理器"""
    
    _initialized = False
    _logger: Optional[logging.Logger] = None
    
    @classmethod
    def initialize(
        cls,
        log_file: str = "./logs/agent.log",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> logging.Logger:
        """
        初始化日志系统
        
        Args:
            log_file: 日志文件路径
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: 单个日志文件最大大小（字节）
            backup_count: 保留的备份文件数量
            
        Returns:
            logging.Logger: 日志对象
        """
        if cls._initialized and cls._logger:
            return cls._logger
        
        # 创建日志目录
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 获取根 logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # 清除已有的 handlers（避免重复初始化）
        root_logger.handlers.clear()
        
        # 创建 logger
        logger = logging.getLogger("ChatAgent")
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        logger.propagate = True
        
        # 清除已有的 handlers（避免重复初始化）
        logger.handlers.clear()
        
        # 创建日志格式
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 文件 Handler（使用 RotatingFileHandler）
        try:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            # 创建一个自定义的 emit 方法来确保每次都刷新
            original_emit = file_handler.emit
            def emit_with_flush(record):
                original_emit(record)
                try:
                    file_handler.flush()
                except:
                    pass
            file_handler.emit = emit_with_flush
        except Exception as e:
            print(f"警告: 无法创建日志文件 {log_file}: {e}")
        
        # 控制台 Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # 标记为已初始化
        cls._initialized = True
        cls._logger = logger
        
        # 记录初始化成功
        logger.info("日志系统初始化成功")
        logger.info(f"日志文件: {log_file}")
        logger.info(f"日志级别: {log_level}")
        logger.info(f"最大文件大小: {max_bytes / (1024 * 1024):.1f}MB")
        logger.info(f"备份文件数量: {backup_count}")
        
        return logger
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        获取日志对象
        
        Returns:
            logging.Logger: 日志对象
        """
        if not cls._initialized or cls._logger is None:
            # 如果未初始化，使用默认配置初始化
            return cls.initialize()
        return cls._logger
    
    @classmethod
    def set_level(cls, log_level: str) -> None:
        """
        设置日志级别
        
        Args:
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        logger = cls.get_logger()
        level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
        # 更新所有 handlers 的级别
        for handler in logger.handlers:
            handler.setLevel(level)
        
        logger.info(f"日志级别已更新为: {log_level}")
    
    @classmethod
    def reset(cls) -> None:
        """重置日志系统（用于测试）"""
        if cls._logger:
            # 关闭所有 handlers
            for handler in cls._logger.handlers[:]:
                handler.close()
                cls._logger.removeHandler(handler)
        
        cls._initialized = False
        cls._logger = None


def get_logger() -> logging.Logger:
    """
    获取日志对象的便捷函数
    
    Returns:
        logging.Logger: 日志对象
    """
    return LoggerManager.get_logger()


def log_exception(logger: logging.Logger, message: str, exc: Exception) -> None:
    """
    记录异常日志（包含堆栈信息）
    
    Args:
        logger: 日志对象
        message: 错误消息
        exc: 异常对象
    """
    logger.error(f"{message}: {str(exc)}", exc_info=True)


def log_operation(logger: logging.Logger, operation: str, **kwargs) -> None:
    """
    记录操作日志
    
    Args:
        logger: 日志对象
        operation: 操作名称
        **kwargs: 操作相关的参数
    """
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"操作: {operation} | 参数: {params}")
