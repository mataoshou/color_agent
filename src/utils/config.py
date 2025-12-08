"""
配置文件管理模块

提供配置文件的读取、写入、验证和修复功能。
"""

import os
import yaml
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, List
from pathlib import Path


@dataclass
class ModelConfig:
    """模型配置数据类"""
    id: str
    name: str
    api_base: str
    api_key: str
    model_name: str
    description: Optional[str] = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class Settings:
    """系统设置数据类"""
    # 模型配置
    active_model_id: Optional[str] = None
    models: Dict[str, Dict] = field(default_factory=dict)
    
    # LangChain 配置
    temperature: float = 0.7
    max_tokens: int = 2048
    streaming: bool = True
    verbose: bool = False
    
    # 工作目录配置
    working_directory: str = "."
    
    # 会话配置
    storage_path: str = "./sessions"
    auto_save: bool = True
    max_history: int = 100
    
    # 文件操作配置
    allowed_formats: List[str] = field(default_factory=lambda: [
        ".txt", ".md", ".py", ".js", ".json", ".yaml", ".yml", 
        ".html", ".css", ".xml", ".csv", ".log"
    ])
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "./logs/agent.log"
    
    # UI 配置
    theme: str = "light"
    window_width: int = 1200
    window_height: int = 800
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG_PATH = "config.yaml"
    
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.settings: Optional[Settings] = None
    
    def load(self) -> Settings:
        """
        加载配置文件
        
        Returns:
            Settings: 配置对象
        """
        if not os.path.exists(self.config_path):
            # 配置文件不存在，创建默认配置
            self.settings = Settings()
            self.save()
            return self.settings
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            # 从字典创建 Settings 对象
            self.settings = self._dict_to_settings(data)
            
            # 验证和修复配置
            self._validate_and_fix()
            
            return self.settings
            
        except Exception as e:
            # 配置文件损坏，备份并创建新的默认配置
            self._backup_corrupted_config()
            self.settings = Settings()
            self.save()
            raise ValueError(f"配置文件损坏，已创建新的默认配置: {e}")
    
    def save(self) -> None:
        """保存配置到文件"""
        if self.settings is None:
            raise ValueError("配置未加载，无法保存")
        
        # 确保配置目录存在
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        # 转换为字典并保存
        data = self.settings.to_dict()
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)
    
    def get_settings(self) -> Settings:
        """
        获取配置对象
        
        Returns:
            Settings: 配置对象
        """
        if self.settings is None:
            self.load()
        return self.settings
    
    def update_settings(self, **kwargs) -> None:
        """
        更新配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        if self.settings is None:
            self.load()
        
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        
        self._validate_and_fix()
        self.save()
    
    def add_model(self, model_config: ModelConfig) -> None:
        """
        添加模型配置
        
        Args:
            model_config: 模型配置对象
        """
        if self.settings is None:
            self.load()
        
        self.settings.models[model_config.id] = model_config.to_dict()
        self.save()
    
    def remove_model(self, model_id: str) -> None:
        """
        删除模型配置
        
        Args:
            model_id: 模型 ID
        """
        if self.settings is None:
            self.load()
        
        if model_id in self.settings.models:
            del self.settings.models[model_id]
            
            # 如果删除的是当前激活的模型，清空 active_model_id
            if self.settings.active_model_id == model_id:
                self.settings.active_model_id = None
            
            self.save()
    
    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """
        获取模型配置
        
        Args:
            model_id: 模型 ID
            
        Returns:
            ModelConfig: 模型配置对象，如果不存在返回 None
        """
        if self.settings is None:
            self.load()
        
        model_data = self.settings.models.get(model_id)
        if model_data:
            return ModelConfig(**model_data)
        return None
    
    def get_active_model(self) -> Optional[ModelConfig]:
        """
        获取当前激活的模型配置
        
        Returns:
            ModelConfig: 当前激活的模型配置，如果没有返回 None
        """
        if self.settings is None:
            self.load()
        
        if self.settings.active_model_id:
            return self.get_model(self.settings.active_model_id)
        return None
    
    def _dict_to_settings(self, data: Dict) -> Settings:
        """
        从字典创建 Settings 对象
        
        Args:
            data: 配置字典
            
        Returns:
            Settings: 配置对象
        """
        # 创建默认配置
        settings = Settings()
        
        # 更新配置值
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        return settings
    
    def _validate_and_fix(self) -> None:
        """验证配置并修复无效值"""
        if self.settings is None:
            return
        
        # 验证温度参数
        if not (0.0 <= self.settings.temperature <= 2.0):
            self.settings.temperature = 0.7
        
        # 验证 max_tokens
        if not (512 <= self.settings.max_tokens <= 4096):
            self.settings.max_tokens = 2048
        
        # 验证工作目录
        if not os.path.exists(self.settings.working_directory):
            self.settings.working_directory = "."
        
        # 验证主题
        if self.settings.theme not in ['light', 'dark']:
            self.settings.theme = 'light'
        
        # 验证 active_model_id
        if self.settings.active_model_id and self.settings.active_model_id not in self.settings.models:
            self.settings.active_model_id = None
        
        # 验证日志级别
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.settings.log_level not in valid_log_levels:
            self.settings.log_level = 'INFO'
    
    def _backup_corrupted_config(self) -> None:
        """备份损坏的配置文件"""
        if os.path.exists(self.config_path):
            backup_path = f"{self.config_path}.backup"
            try:
                os.rename(self.config_path, backup_path)
            except Exception:
                pass
    
    @staticmethod
    def create_default_config(config_path: str = DEFAULT_CONFIG_PATH) -> None:
        """
        创建默认配置文件
        
        Args:
            config_path: 配置文件路径
        """
        manager = ConfigManager(config_path)
        manager.settings = Settings()
        manager.save()
