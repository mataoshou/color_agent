"""
模型配置对话框模块

提供添加和编辑 OpenAPI 模型配置的图形界面。
"""

import logging
import uuid
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from src.utils.config import ModelConfig


logger = logging.getLogger(__name__)


class ModelConfigDialog(QDialog):
    """
    模型配置对话框
    
    用于添加或编辑 OpenAPI 模型配置，包含模型名称、API 端点、
    API 密钥、模型标识符和描述等输入字段。
    
    Attributes:
        model_config: 模型配置对象（编辑模式时使用）
        is_edit_mode: 是否为编辑模式
    """
    
    def __init__(self, parent=None, model_config: Optional[ModelConfig] = None):
        """
        初始化模型配置对话框
        
        Args:
            parent: 父窗口
            model_config: 模型配置对象（编辑模式时传入）
        """
        try:
            logger.info("开始初始化 ModelConfigDialog...")
            super().__init__(parent)
            logger.info("QDialog 初始化完成")
            
            self.model_config = model_config
            self.is_edit_mode = model_config is not None
            logger.info(f"编辑模式: {self.is_edit_mode}")
            
            logger.info("初始化 UI...")
            self._init_ui()
            logger.info("UI 初始化完成")
            
            # 如果是编辑模式，填充现有数据
            if self.is_edit_mode:
                logger.info("加载模型数据...")
                self._load_model_data()
                logger.info("模型数据加载完成")
            
            logger.info(f"ModelConfigDialog 初始化完成 (编辑模式: {self.is_edit_mode})")
        except Exception as e:
            logger.error(f"ModelConfigDialog 初始化失败: {e}", exc_info=True)
            raise
    
    def _init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        title = "编辑模型配置" if self.is_edit_mode else "添加模型配置"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # 模型名称输入框
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: OpenAI GPT-4")
        form_layout.addRow("模型名称*:", self.name_input)
        
        # API 端点输入框
        self.api_base_input = QLineEdit()
        self.api_base_input.setPlaceholderText("例如: https://api.openai.com/v1")
        form_layout.addRow("API 端点*:", self.api_base_input)
        
        # API 密钥输入框（带显示/隐藏按钮）
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入 API 密钥")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        show_key_layout = QHBoxLayout()
        show_key_layout.addWidget(self.api_key_input)
        self.show_key_button = QPushButton("显示")
        self.show_key_button.setMaximumWidth(60)
        self.show_key_button.clicked.connect(self._toggle_key_visibility)
        show_key_layout.addWidget(self.show_key_button)
        
        form_layout.addRow("API 密钥*:", show_key_layout)
        
        # 模型标识符输入框
        self.model_name_input = QLineEdit()
        self.model_name_input.setPlaceholderText("例如: gpt-4, gpt-3.5-turbo")
        form_layout.addRow("模型标识符*:", self.model_name_input)
        
        # 描述输入框
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("可选：输入模型描述信息")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("描述:", self.description_input)
        
        # 添加表单布局到主布局
        main_layout.addLayout(form_layout)
        
        # 添加提示标签
        hint_label = QLabel("* 表示必填字段")
        hint_label.setStyleSheet("color: gray; font-size: 10px;")
        main_layout.addWidget(hint_label)
        
        # 添加常见模型模板提示
        if not self.is_edit_mode:
            template_label = QLabel(
                "常见模板:\n"
                "• OpenAI: https://api.openai.com/v1\n"
                "• Azure OpenAI: https://your-resource.openai.azure.com/\n"
                "• 自定义服务: 输入您的 API 端点"
            )
            template_label.setStyleSheet(
                "background-color: #f0f0f0; "
                "padding: 10px; "
                "border-radius: 5px; "
                "font-size: 11px;"
            )
            main_layout.addWidget(template_label)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 保存按钮
        save_button = QPushButton("保存")
        save_button.setDefault(True)
        save_button.clicked.connect(self._on_save)
        button_layout.addWidget(save_button)
        
        main_layout.addLayout(button_layout)
        
        # 设置主布局
        self.setLayout(main_layout)
    
    def _load_model_data(self):
        """加载模型数据到输入框（编辑模式）"""
        if not self.model_config:
            return
        
        self.name_input.setText(self.model_config.name)
        self.api_base_input.setText(self.model_config.api_base)
        self.api_key_input.setText(self.model_config.api_key)
        self.model_name_input.setText(self.model_config.model_name)
        
        if self.model_config.description:
            self.description_input.setPlainText(self.model_config.description)
        
        logger.debug(f"加载模型数据: {self.model_config.name}")
    
    def _toggle_key_visibility(self):
        """切换密钥显示/隐藏"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_button.setText("隐藏")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_button.setText("显示")
    
    def _on_save(self):
        """保存按钮点击处理"""
        # 验证输入
        if not self._validate_input():
            return
        
        # 接受对话框
        self.accept()
        logger.info(f"模型配置已保存: {self.name_input.text()}")
    
    def _validate_input(self) -> bool:
        """
        验证输入的有效性
        
        Returns:
            bool: 验证通过返回 True，否则返回 False
        """
        # 验证模型名称
        name = self.name_input.text().strip()
        if not name:
            self._show_error("模型名称不能为空")
            self.name_input.setFocus()
            return False
        
        # 验证 API 端点
        api_base = self.api_base_input.text().strip()
        if not api_base:
            self._show_error("API 端点不能为空")
            self.api_base_input.setFocus()
            return False
        
        if not (api_base.startswith('http://') or api_base.startswith('https://')):
            self._show_error("API 端点必须以 http:// 或 https:// 开头")
            self.api_base_input.setFocus()
            return False
        
        # 验证 API 密钥
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self._show_error("API 密钥不能为空")
            self.api_key_input.setFocus()
            return False
        
        # 验证模型标识符
        model_name = self.model_name_input.text().strip()
        if not model_name:
            self._show_error("模型标识符不能为空")
            self.model_name_input.setFocus()
            return False
        
        logger.debug("输入验证通过")
        return True
    
    def _show_error(self, message: str):
        """
        显示错误提示对话框
        
        Args:
            message: 错误消息
        """
        QMessageBox.warning(self, "输入错误", message)
        logger.warning(f"输入验证失败: {message}")
    
    def get_model_config(self) -> ModelConfig:
        """
        获取用户输入的模型配置
        
        Returns:
            ModelConfig: 模型配置对象
        """
        # 如果是编辑模式，使用原有的 ID，否则生成新的 UUID
        model_id = self.model_config.id if self.is_edit_mode else str(uuid.uuid4())
        
        return ModelConfig(
            id=model_id,
            name=self.name_input.text().strip(),
            api_base=self.api_base_input.text().strip(),
            api_key=self.api_key_input.text().strip(),
            model_name=self.model_name_input.text().strip(),
            description=self.description_input.toPlainText().strip()
        )
