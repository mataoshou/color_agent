# utils/theme_manager.py 分析文档

## 1. 文件概述

**文件路径**: `src/utils/theme_manager.py`
**所属模块**: Utils
**主要功能**: 提供主题加载和动态切换功能，支持QSS样式表的应用
**技术亮点**: 支持明暗两种主题切换，与PyQt6应用程序集成，从配置文件读取主题设置

## 2. 核心实现

### 2.1 ThemeManager类定义

```python
class ThemeManager:
    """
    主题管理器
    
    负责加载和应用 QSS 样式表。
    """
    
    THEME_DIR = "src/resources/styles"
    THEMES = {
        'light': 'light_theme.qss',
        'dark': 'dark_theme.qss'
    }
    
    def __init__(self):
        """初始化主题管理器"""
        self.current_theme: Optional[str] = None
```

**功能**: 管理主题的加载和应用

**设计亮点**:
- 使用常量定义主题目录和可用主题
- 支持明暗两种主题
- 跟踪当前主题状态

### 2.2 主题加载与应用

#### `load_theme(self, theme_name: str) -> bool`
```python
def load_theme(self, theme_name: str) -> bool:
    """
    加载并应用主题
    
    Args:
        theme_name: 主题名称 ('light' 或 'dark')
        
    Returns:
        bool: 是否成功加载主题
    """
    if theme_name not in self.THEMES:
        logger.error(f"未知的主题名称: {theme_name}")
        return False
    
    theme_file = self.THEMES[theme_name]
    theme_path = os.path.join(self.THEME_DIR, theme_file)
    
    if not os.path.exists(theme_path):
        logger.error(f"主题文件不存在: {theme_path}")
        return False
    
    try:
        # 读取 QSS 文件
        with open(theme_path, 'r', encoding='utf-8') as f:
            stylesheet = f.read()
        
        # 应用样式表到应用程序
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)
            self.current_theme = theme_name
            logger.info(f"主题已切换: {theme_name}")
            return True
        else:
            logger.error("无法获取 QApplication 实例")
            return False
            
    except Exception as e:
        logger.error(f"加载主题失败: {e}", exc_info=True)
        return False
```

**功能**: 加载并应用主题

**设计亮点**:
- 验证主题名称的有效性
- 检查主题文件是否存在
- 使用utf-8编码读取QSS文件
- 应用样式表到整个应用程序
- 记录主题切换日志

### 2.3 当前主题获取

#### `get_current_theme(self) -> Optional[str]`
```python
def get_current_theme(self) -> Optional[str]:
    """
    获取当前主题名称
    
    Returns:
        str: 当前主题名称，如果未设置返回 None
    """
    return self.current_theme
```

**功能**: 获取当前主题名称

**设计亮点**:
- 简单直接的接口，返回当前主题名称或None

### 2.4 从配置应用主题

#### `apply_theme_from_config(self, theme_name: str) -> bool`
```python
def apply_theme_from_config(self, theme_name: str) -> bool:
    """
    从配置应用主题
    
    Args:
        theme_name: 主题名称
        
    Returns:
        bool: 是否成功应用主题
    """
    # 验证主题名称
    if theme_name not in self.THEMES:
        logger.warning(f"配置中的主题名称无效: {theme_name}，使用默认主题 'light'")
        theme_name = 'light'
    
    return self.load_theme(theme_name)
```

**功能**: 从配置应用主题，处理无效主题名称

**设计亮点**:
- 验证主题名称的有效性
- 无效主题名称时使用默认主题'light'
- 调用load_theme方法应用主题

## 3. 与其他模块的关系

### 3.1 与Config模块的关系

```
Config
└── ThemeManager
```

**交互方式**:
- Config模块存储用户选择的主题设置
- ThemeManager从Config模块获取主题设置并应用

### 3.2 与UI模块的关系

```
UI Components
└── ThemeManager
    └── QApplication
```

**交互方式**:
- ThemeManager获取QApplication实例并设置样式表
- UI组件自动应用主题样式

### 3.3 与Logger模块的关系

```
Logger
└── ThemeManager
```

**交互方式**:
- ThemeManager使用Logger模块记录主题加载和切换日志

## 4. 代码结构

```python
"""
主题管理模块

提供主题加载和动态切换功能。
"""

import os
import logging
from typing import Optional
from PyQt6.QtWidgets import QApplication


logger = logging.getLogger(__name__)


class ThemeManager:
    """
    主题管理器
    
    负责加载和应用 QSS 样式表。
    """
    
    THEME_DIR = "src/resources/styles"
    THEMES = {
        'light': 'light_theme.qss',
        'dark': 'dark_theme.qss'
    }
    
    def __init__(self):
        """初始化主题管理器"""
        self.current_theme: Optional[str] = None
    
    def load_theme(self, theme_name: str) -> bool:
        """加载并应用主题"""
        # 加载主题代码
    
    def get_current_theme(self) -> Optional[str]:
        """获取当前主题名称"""
        # 获取当前主题代码
    
    def apply_theme_from_config(self, theme_name: str) -> bool:
        """从配置应用主题"""
        # 从配置应用主题代码
```

## 5. 潜在问题或改进点

### 5.1 主题目录配置化

**问题**: 当前主题目录是硬编码的，不够灵活
**建议**: 将主题目录配置化，支持自定义主题目录

```python
class ThemeManager:
    """主题管理器"""
    
    def __init__(self, theme_dir: str = "src/resources/styles"):
        """初始化主题管理器"""
        self.theme_dir = theme_dir
        self.current_theme: Optional[str] = None
        self.themes = {
            'light': 'light_theme.qss',
            'dark': 'dark_theme.qss'
        }
    
    def load_theme(self, theme_name: str) -> bool:
        """加载并应用主题"""
        if theme_name not in self.themes:
            logger.error(f"未知的主题名称: {theme_name}")
            return False
        
        theme_file = self.themes[theme_name]
        theme_path = os.path.join(self.theme_dir, theme_file)
        
        # 其他代码
```

### 5.2 支持动态主题切换

**问题**: 当前主题切换需要重启应用程序才能完全生效
**建议**: 添加动态主题切换支持，实时更新UI样式

```python
class ThemeManager:
    """主题管理器"""
    
    def load_theme(self, theme_name: str) -> bool:
        """加载并应用主题"""
        # 其他代码
        
        try:
            # 读取 QSS 文件
            with open(theme_path, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            
            # 应用样式表到应用程序
            app = QApplication.instance()
            if app:
                # 清除之前的样式表
                app.setStyleSheet("")
                # 应用新的样式表
                app.setStyleSheet(stylesheet)
                self.current_theme = theme_name
                logger.info(f"主题已切换: {theme_name}")
                return True
            else:
                logger.error("无法获取 QApplication 实例")
                return False
                
        except Exception as e:
            logger.error(f"加载主题失败: {e}", exc_info=True)
            return False
```

### 5.3 支持主题预览

**问题**: 当前没有主题预览功能，用户只能应用后才能看到效果
**建议**: 添加主题预览功能，允许用户在切换前预览主题效果

```python
class ThemeManager:
    """主题管理器"""
    
    def preview_theme(self, theme_name: str) -> Optional[str]:
        """
        预览主题，返回QSS样式字符串
        
        Args:
            theme_name: 主题名称
            
        Returns:
            str: QSS样式字符串，如果预览失败返回None
        """
        if theme_name not in self.THEMES:
            logger.error(f"未知的主题名称: {theme_name}")
            return None
        
        theme_file = self.THEMES[theme_name]
        theme_path = os.path.join(self.THEME_DIR, theme_file)
        
        if not os.path.exists(theme_path):
            logger.error(f"主题文件不存在: {theme_path}")
            return None
        
        try:
            # 读取 QSS 文件
            with open(theme_path, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            
            return stylesheet
            
        except Exception as e:
            logger.error(f"预览主题失败: {e}", exc_info=True)
            return None
```

### 5.4 支持自定义主题

**问题**: 当前只支持内置的light和dark主题，不支持自定义主题
**建议**: 添加自定义主题支持，允许用户创建和使用自己的主题

```python
class ThemeManager:
    """主题管理器"""
    
    def __init__(self):
        """初始化主题管理器"""
        self.current_theme: Optional[str] = None
        self.themes = {
            'light': 'light_theme.qss',
            'dark': 'dark_theme.qss'
        }
    
    def add_custom_theme(self, theme_name: str, theme_file: str) -> bool:
        """
        添加自定义主题
        
        Args:
            theme_name: 主题名称
            theme_file: 主题文件路径
            
        Returns:
            bool: 是否成功添加自定义主题
        """
        if theme_name in self.themes:
            logger.error(f"主题名称已存在: {theme_name}")
            return False
        
        if not os.path.exists(theme_file):
            logger.error(f"主题文件不存在: {theme_file}")
            return False
        
        self.themes[theme_name] = theme_file
        logger.info(f"已添加自定义主题: {theme_name}")
        return True
    
    def remove_custom_theme(self, theme_name: str) -> bool:
        """
        移除自定义主题
        
        Args:
            theme_name: 主题名称
            
        Returns:
            bool: 是否成功移除自定义主题
        """
        if theme_name not in self.themes or theme_name in ['light', 'dark']:
            logger.error(f"无法移除主题: {theme_name}")
            return False
        
        del self.themes[theme_name]
        logger.info(f"已移除自定义主题: {theme_name}")
        return True
```

### 5.5 主题切换动画

**问题**: 当前主题切换是瞬间完成的，没有过渡效果
**建议**: 添加主题切换动画，提升用户体验

```python
class ThemeManager:
    """主题管理器"""
    
    def load_theme(self, theme_name: str, animate: bool = True) -> bool:
        """
        加载并应用主题
        
        Args:
            theme_name: 主题名称
            animate: 是否使用动画效果
            
        Returns:
            bool: 是否成功加载主题
        """
        # 其他代码
        
        try:
            # 读取 QSS 文件
            with open(theme_path, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            
            # 应用样式表到应用程序
            app = QApplication.instance()
            if app:
                if animate:
                    # 添加淡入淡出动画
                    self._fade_transition(app, stylesheet)
                else:
                    app.setStyleSheet(stylesheet)
                
                self.current_theme = theme_name
                logger.info(f"主题已切换: {theme_name}")
                return True
            else:
                logger.error("无法获取 QApplication 实例")
                return False
                
        except Exception as e:
            logger.error(f"加载主题失败: {e}", exc_info=True)
            return False
    
    def _fade_transition(self, app: QApplication, new_stylesheet: str) -> None:
        """
        淡入淡出动画效果
        
        Args:
            app: QApplication实例
            new_stylesheet: 新的样式表
        """
        # 实现淡入淡出动画
        # 这需要更复杂的实现，可能需要使用QPropertyAnimation等
        pass
```

### 5.6 主题状态保存

**问题**: 当前主题状态只保存在内存中，应用程序重启后需要重新设置
**建议**: 添加主题状态保存功能，记住用户的主题选择

```python
class ThemeManager:
    """主题管理器"""
    
    def __init__(self, config_manager):
        """初始化主题管理器"""
        self.config_manager = config_manager
        self.current_theme: Optional[str] = None
        self.themes = {
            'light': 'light_theme.qss',
            'dark': 'dark_theme.qss'
        }
    
    def load_theme(self, theme_name: str) -> bool:
        """加载并应用主题"""
        # 其他代码
        
        try:
            # 读取 QSS 文件
            with open(theme_path, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            
            # 应用样式表到应用程序
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
                self.current_theme = theme_name
                
                # 保存主题状态到配置
                self.config_manager.update_settings(theme=theme_name)
                
                logger.info(f"主题已切换: {theme_name}")
                return True
            else:
                logger.error("无法获取 QApplication 实例")
                return False
                
        except Exception as e:
            logger.error(f"加载主题失败: {e}", exc_info=True)
            return False
```

## 6. 总结

utils/theme_manager.py是一个设计简洁的主题管理模块，它提供了主题加载和动态切换功能，支持明暗两种主题。

该模块具有以下特点：

1. **简单易用**：提供了清晰的接口，便于使用
2. **灵活配置**：支持从配置应用主题，处理无效主题名称
3. **日志记录**：详细记录主题加载和切换日志
4. **错误处理**：完善的错误处理机制，确保主题加载失败时不会导致应用程序崩溃

该模块在应用程序架构中扮演着重要角色，为用户提供了个性化的界面体验。

通过进一步优化，可以提高其灵活性、动态性和用户体验，更好地满足应用程序的需求。