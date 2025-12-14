# utils/logger.py 分析文档

## 1. 文件概述

**文件路径**: `src/utils/logger.py`
**所属模块**: Utils
**主要功能**: 提供日志配置和初始化功能，支持文件和控制台双输出，实现日志轮转和自动管理
**技术亮点**: 采用单例模式实现日志管理器，支持文件轮转和自动刷新，提供便捷的日志记录接口

## 2. 核心实现

### 2.1 LoggerManager类定义

```python
class LoggerManager:
    """日志管理器"""
    
    _initialized = False
    _logger: Optional[logging.Logger] = None
```

**功能**: 管理日志系统的初始化、配置和状态

**设计亮点**:
- 使用类变量实现单例模式，确保日志系统只初始化一次
- 静态方法提供全局访问接口
- 延迟初始化，提高性能

### 2.2 日志初始化方法

```python
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
```

**功能**: 初始化日志系统，配置日志输出格式和目标

**设计亮点**:
- 默认配置合理，无需额外配置即可使用
- 支持自定义日志文件路径、级别、大小和备份数量
- 自动创建日志目录
- 清除已有handlers避免重复初始化
- 使用RotatingFileHandler实现日志轮转

### 2.3 日志获取与配置

#### `get_logger(self) -> logging.Logger`
```python
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
```

**功能**: 获取日志对象，如果未初始化则自动初始化

**设计亮点**:
- 实现了懒加载，提高性能
- 确保始终返回可用的日志对象

#### `set_level(self, log_level: str) -> None`
```python
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
```

**功能**: 设置日志级别

**设计亮点**:
- 支持动态调整日志级别
- 自动更新所有handlers的级别
- 记录日志级别变更

#### `reset(self) -> None`
```python
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
```

**功能**: 重置日志系统，用于测试场景

**设计亮点**:
- 彻底清理日志系统状态
- 关闭所有handlers，释放资源

### 2.4 便捷函数

#### `get_logger() -> logging.Logger`
```python
def get_logger() -> logging.Logger:
    """
    获取日志对象的便捷函数
    
    Returns:
        logging.Logger: 日志对象
    """
    return LoggerManager.get_logger()
```

**功能**: 获取日志对象的便捷函数

**设计亮点**:
- 简化日志对象的获取，提高代码可读性
- 与LoggerManager.get_logger()功能一致

#### `log_exception(logger: logging.Logger, message: str, exc: Exception) -> None`
```python
def log_exception(logger: logging.Logger, message: str, exc: Exception) -> None:
    """
    记录异常日志（包含堆栈信息）
    
    Args:
        logger: 日志对象
        message: 错误消息
        exc: 异常对象
    """
    logger.error(f"{message}: {str(exc)}", exc_info=True)
```

**功能**: 记录异常日志，包含完整的堆栈信息

**设计亮点**:
- 简化异常日志的记录
- 确保异常信息和堆栈信息都被记录

#### `log_operation(logger: logging.Logger, operation: str, **kwargs) -> None`
```python
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
```

**功能**: 记录操作日志，包含操作名称和参数

**设计亮点**:
- 统一操作日志的格式
- 自动格式化操作参数

## 3. 与其他模块的关系

### 3.1 与Errors模块的关系

```
Logger
└── Errors
    ├── AgentError
    ├── ModelError
    ├── SessionError
    └── FileError
```

**交互方式**:
- Errors模块依赖Logger模块记录错误日志
- AgentError类在初始化时自动调用logger.error记录错误信息
- log_exception函数用于记录详细的异常信息

### 3.2 与Config模块的关系

```
Config
└── Logger
    └── LoggerManager
```

**交互方式**:
- Config模块中的ConfigManager类依赖Logger模块记录配置操作日志
- 例如：配置加载、保存、更新等操作

### 3.3 与ApplicationController模块的关系

```
ApplicationController
└── Logger
    └── LoggerManager
```

**交互方式**:
- ApplicationController依赖Logger模块记录应用程序启动、关闭等重要事件
- 例如：应用程序初始化、配置加载、模块初始化等

## 4. 代码结构

```python
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
        """初始化日志系统"""
        # 初始化代码
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """获取日志对象"""
        # 获取代码
    
    @classmethod
    def set_level(cls, log_level: str) -> None:
        """设置日志级别"""
        # 设置代码
    
    @classmethod
    def reset(cls) -> None:
        """重置日志系统（用于测试）"""
        # 重置代码


def get_logger() -> logging.Logger:
    """获取日志对象的便捷函数"""
    return LoggerManager.get_logger()


def log_exception(logger: logging.Logger, message: str, exc: Exception) -> None:
    """记录异常日志（包含堆栈信息）"""
    # 记录代码


def log_operation(logger: logging.Logger, operation: str, **kwargs) -> None:
    """记录操作日志"""
    # 记录代码
```

## 5. 潜在问题或改进点

### 5.1 日志格式可配置化

**问题**: 当前日志格式固定，不支持自定义
**建议**: 添加日志格式配置选项

```python
@classmethod
def initialize(
    cls,
    log_file: str = "./logs/agent.log",
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    log_format: str = '%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
    date_format: str = '%Y-%m-%d %H:%M:%S'
) -> logging.Logger:
    """初始化日志系统"""
    # 初始化代码
    
    # 创建日志格式
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    
    # 其他代码
```

### 5.2 支持不同模块的日志级别

**问题**: 当前所有模块使用同一个日志级别，不够灵活
**建议**: 支持为不同模块设置不同的日志级别

```python
class LoggerManager:
    # 其他代码
    
    @classmethod
    def set_module_level(cls, module_name: str, log_level: str) -> None:
        """
        设置特定模块的日志级别
        
        Args:
            module_name: 模块名称
            log_level: 日志级别
        """
        logger = logging.getLogger(module_name)
        level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
        # 更新该模块的所有 handlers 的级别
        for handler in logger.handlers:
            handler.setLevel(level)
        
        cls.get_logger().info(f"模块 {module_name} 的日志级别已更新为: {log_level}")
```

### 5.3 支持异步日志记录

**问题**: 当前日志记录是同步的，可能会影响应用程序性能
**建议**: 添加异步日志记录支持

```python
from logging.handlers import QueueHandler, QueueListener
import queue
import threading

class AsyncLoggerManager(LoggerManager):
    """异步日志管理器"""
    
    _queue: Optional[queue.Queue] = None
    _listener: Optional[QueueListener] = None
    
    @classmethod
    def initialize(
        cls,
        log_file: str = "./logs/agent.log",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> logging.Logger:
        """初始化异步日志系统"""
        # 初始化基础日志系统
        logger = super().initialize(log_file, log_level, max_bytes, backup_count)
        
        # 创建队列和异步处理器
        cls._queue = queue.Queue(-1)  # 无界队列
        queue_handler = QueueHandler(cls._queue)
        
        # 移除所有同步处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 添加队列处理器
        logger.addHandler(queue_handler)
        
        # 创建队列监听器
        cls._listener = QueueListener(cls._queue, *logger.handlers)
        cls._listener.start()
        
        return logger
    
    @classmethod
    def reset(cls) -> None:
        """重置异步日志系统"""
        if cls._listener:
            cls._listener.stop()
            cls._listener = None
        
        if cls._queue:
            cls._queue = None
        
        super().reset()
```

### 5.4 日志级别彩色输出

**问题**: 当前控制台日志没有颜色区分，不够直观
**建议**: 添加彩色日志输出支持

```python
class ColoredFormatter(logging.Formatter):
    """彩色日志格式"""
    
    COLORS = {
        'DEBUG': '\033[94m',  # 蓝色
        'INFO': '\033[92m',   # 绿色
        'WARNING': '\033[93m',  # 黄色
        'ERROR': '\033[91m',  # 红色
        'CRITICAL': '\033[95m',  # 紫色
        'RESET': '\033[0m'    # 重置
    }
    
    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            levelname_color = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            record.levelname = levelname_color
        
        return super().format(record)

class LoggerManager:
    # 其他代码
    
    @classmethod
    def initialize(
        cls,
        log_file: str = "./logs/agent.log",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        colored: bool = True
    ) -> logging.Logger:
        """初始化日志系统"""
        # 初始化代码
        
        # 创建日志格式
        formatter_class = ColoredFormatter if colored and os.name != 'nt' else logging.Formatter
        formatter = formatter_class(
            fmt='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 其他代码
```

### 5.5 支持JSON格式日志

**问题**: 当前日志格式为文本格式，不便于机器解析
**建议**: 添加JSON格式日志支持

```python
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON日志格式"""
    
    def format(self, record):
        log_record = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'filename': record.filename,
            'lineno': record.lineno,
            'funcName': record.funcName,
            'process': record.process,
            'thread': record.thread
        }
        
        # 处理异常信息
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        # 处理额外信息
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
        
        return json.dumps(log_record)

class LoggerManager:
    # 其他代码
    
    @classmethod
    def initialize(
        cls,
        log_file: str = "./logs/agent.log",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        format_type: str = 'text'  # 'text' or 'json'
    ) -> logging.Logger:
        """初始化日志系统"""
        # 初始化代码
        
        # 创建日志格式
        if format_type == 'json':
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # 其他代码
```

### 5.6 日志脱敏

**问题**: 当前日志可能包含敏感信息，如API密钥、密码等
**建议**: 添加日志脱敏功能

```python
class SensitiveDataFilter(logging.Filter):
    """敏感数据过滤器"""
    
    SENSITIVE_KEYS = ['api_key', 'password', 'secret', 'token']
    
    def filter(self, record):
        # 脱敏消息
        record.msg = self._mask_sensitive_data(record.msg)
        
        # 脱敏参数
        if hasattr(record, 'args') and record.args:
            record.args = tuple(self._mask_sensitive_data(arg) if isinstance(arg, str) else arg for arg in record.args)
        
        return True
    
    def _mask_sensitive_data(self, data: str) -> str:
        """脱敏敏感数据"""
        if not isinstance(data, str):
            return data
        
        for key in self.SENSITIVE_KEYS:
            import re
            # 匹配类似 'api_key=xxx' 的模式
            pattern = rf'({key}[:=]\s*)([^\s,;}]+)'
            data = re.sub(pattern, r'\1***', data)
        
        return data

class LoggerManager:
    # 其他代码
    
    @classmethod
    def initialize(
        cls,
        log_file: str = "./logs/agent.log",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        mask_sensitive_data: bool = True
    ) -> logging.Logger:
        """初始化日志系统"""
        # 初始化代码
        
        # 添加敏感数据过滤器
        if mask_sensitive_data:
            filter = SensitiveDataFilter()
            logger.addFilter(filter)
            
        # 其他代码
```

## 6. 总结

utils/logger.py是一个设计良好的日志系统模块，它提供了日志配置和初始化功能，支持文件和控制台双输出，实现了日志轮转和自动管理。

该模块具有以下特点：

1. **单例模式设计**：使用类变量实现单例模式，确保日志系统只初始化一次
2. **自动日志管理**：支持日志文件轮转，自动创建日志目录
3. **双输出支持**：同时支持文件和控制台输出
4. **便捷的接口**：提供了简单易用的日志记录接口
5. **可配置性**：支持设置日志级别、文件大小和备份数量等参数

该模块在应用程序架构中扮演着重要角色，为其他模块提供了统一的日志记录机制，有助于调试和监控应用程序的运行状态。

通过进一步优化，可以提高其灵活性、性能和安全性，更好地满足应用程序的需求。