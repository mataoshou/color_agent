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
    
    def get_current_theme(self) -> Optional[str]:
        """
        获取当前主题名称
        
        Returns:
            str: 当前主题名称，如果未设置返回 None
        """
        return self.current_theme
    
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
