"""
模型配置管理模块

提供模型配置的添加、编辑、删除、加载和保存功能。
"""

import logging
from typing import Optional, List, Dict
from src.utils.config import ConfigManager, ModelConfig


logger = logging.getLogger(__name__)


class ModelConfigManager:
    """
    模型配置管理器
    
    负责管理多个 OpenAPI 模型配置，包括添加、编辑、删除、验证和切换功能。
    
    Attributes:
        config_manager: 配置管理器实例
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        初始化模型配置管理器
        
        Args:
            config_manager: 配置管理器实例，如果为 None 则创建新实例
        """
        self.config_manager = config_manager or ConfigManager()
        logger.info("ModelConfigManager 初始化完成")
    
    def add_model(self, model_config: ModelConfig) -> bool:
        """
        添加模型配置
        
        Args:
            model_config: 模型配置对象
            
        Returns:
            bool: 添加成功返回 True，失败返回 False
        """
        try:
            # 验证模型配置
            if not self.validate_model_config(model_config):
                logger.error(f"模型配置验证失败: {model_config.name}")
                return False
            
            # 检查模型 ID 是否已存在
            if self.get_model_config(model_config.id):
                logger.warning(f"模型 ID 已存在: {model_config.id}")
                return False
            
            # 添加模型配置
            self.config_manager.add_model(model_config)
            logger.info(f"成功添加模型配置: {model_config.name} (ID: {model_config.id})")
            
            return True
            
        except Exception as e:
            logger.error(f"添加模型配置失败: {e}", exc_info=True)
            return False
    
    def update_model(self, model_config: ModelConfig) -> bool:
        """
        更新模型配置
        
        Args:
            model_config: 模型配置对象
            
        Returns:
            bool: 更新成功返回 True，失败返回 False
        """
        try:
            # 验证模型配置
            if not self.validate_model_config(model_config):
                logger.error(f"模型配置验证失败: {model_config.name}")
                return False
            
            # 检查模型是否存在
            if not self.get_model_config(model_config.id):
                logger.error(f"模型不存在: {model_config.id}")
                return False
            
            # 更新模型配置（先删除再添加）
            settings = self.config_manager.get_settings()
            settings.models[model_config.id] = model_config.to_dict()
            self.config_manager.save()
            
            logger.info(f"成功更新模型配置: {model_config.name} (ID: {model_config.id})")
            return True
            
        except Exception as e:
            logger.error(f"更新模型配置失败: {e}", exc_info=True)
            return False
    
    def delete_model(self, model_id: str) -> bool:
        """
        删除模型配置
        
        Args:
            model_id: 模型 ID
            
        Returns:
            bool: 删除成功返回 True，失败返回 False
        """
        try:
            # 检查模型是否存在
            if not self.get_model_config(model_id):
                logger.warning(f"模型不存在: {model_id}")
                return False
            
            # 删除模型配置
            self.config_manager.remove_model(model_id)
            logger.info(f"成功删除模型配置: {model_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"删除模型配置失败: {e}", exc_info=True)
            return False
    
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """
        获取模型配置
        
        Args:
            model_id: 模型 ID
            
        Returns:
            ModelConfig: 模型配置对象，如果不存在返回 None
        """
        try:
            return self.config_manager.get_model(model_id)
        except Exception as e:
            logger.error(f"获取模型配置失败: {e}", exc_info=True)
            return None
    
    def get_all_models(self) -> List[ModelConfig]:
        """
        获取所有模型配置
        
        Returns:
            List[ModelConfig]: 模型配置列表
        """
        try:
            settings = self.config_manager.get_settings()
            models = []
            
            for model_id, model_data in settings.models.items():
                try:
                    model = ModelConfig(**model_data)
                    models.append(model)
                except Exception as e:
                    logger.error(f"解析模型配置失败 (ID: {model_id}): {e}")
            
            logger.debug(f"获取到 {len(models)} 个模型配置")
            return models
            
        except Exception as e:
            logger.error(f"获取所有模型配置失败: {e}", exc_info=True)
            return []
    
    def get_active_model(self) -> Optional[ModelConfig]:
        """
        获取当前激活的模型配置
        
        Returns:
            ModelConfig: 当前激活的模型配置，如果没有返回 None
        """
        try:
            return self.config_manager.get_active_model()
        except Exception as e:
            logger.error(f"获取激活模型失败: {e}", exc_info=True)
            return None
    
    def set_active_model(self, model_id: str) -> bool:
        """
        设置当前激活的模型
        
        Args:
            model_id: 模型 ID
            
        Returns:
            bool: 设置成功返回 True，失败返回 False
        """
        try:
            # 检查模型是否存在
            model = self.get_model_config(model_id)
            if not model:
                logger.error(f"模型不存在: {model_id}")
                return False
            
            # 设置激活模型
            self.config_manager.update_settings(active_model_id=model_id)
            logger.info(f"成功切换到模型: {model.name} (ID: {model_id})")
            
            return True
            
        except Exception as e:
            logger.error(f"设置激活模型失败: {e}", exc_info=True)
            return False
    
    def validate_model_config(self, model_config: ModelConfig) -> bool:
        """
        验证模型配置的有效性
        
        Args:
            model_config: 模型配置对象
            
        Returns:
            bool: 验证通过返回 True，否则返回 False
        """
        # 验证必填字段
        if not model_config.id or not model_config.id.strip():
            logger.error("模型 ID 不能为空")
            return False
        
        if not model_config.name or not model_config.name.strip():
            logger.error("模型名称不能为空")
            return False
        
        if not model_config.api_base or not model_config.api_base.strip():
            logger.error("API 端点不能为空")
            return False
        
        if not model_config.api_key or not model_config.api_key.strip():
            logger.error("API 密钥不能为空")
            return False
        
        if not model_config.model_name or not model_config.model_name.strip():
            logger.error("模型标识符不能为空")
            return False
        
        # 验证 API 端点格式
        if not self._validate_api_endpoint(model_config.api_base):
            logger.error(f"API 端点格式无效: {model_config.api_base}")
            return False
        
        logger.debug(f"模型配置验证通过: {model_config.name}")
        return True
    
    def _validate_api_endpoint(self, api_base: str) -> bool:
        """
        验证 API 端点格式
        
        Args:
            api_base: API 端点 URL
            
        Returns:
            bool: 格式有效返回 True，否则返回 False
        """
        # 简单验证：检查是否以 http:// 或 https:// 开头
        api_base = api_base.strip()
        return api_base.startswith('http://') or api_base.startswith('https://')
    
    def get_model_count(self) -> int:
        """
        获取模型配置数量
        
        Returns:
            int: 模型配置数量
        """
        try:
            settings = self.config_manager.get_settings()
            return len(settings.models)
        except Exception as e:
            logger.error(f"获取模型数量失败: {e}", exc_info=True)
            return 0
    
    def has_models(self) -> bool:
        """
        检查是否有已配置的模型
        
        Returns:
            bool: 有模型返回 True，否则返回 False
        """
        return self.get_model_count() > 0
