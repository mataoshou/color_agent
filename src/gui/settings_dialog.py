"""
设置对话框模块

提供系统设置和模型管理的图形界面。
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QWidget, QListWidget, QListWidgetItem, QPushButton, QComboBox,
    QSlider, QSpinBox, QLabel, QMessageBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from src.services.model_config_manager import ModelConfigManager
from src.gui.model_config_dialog import ModelConfigDialog
from src.utils.config import ModelConfig, ConfigManager
from src.utils.theme_manager import ThemeManager


logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """
    设置对话框
    
    提供模型管理、参数配置和主题设置等功能。
    
    Signals:
        model_changed: 模型切换信号，携带模型 ID
        settings_changed: 设置变更信号
    """
    
    model_changed = pyqtSignal(str)  # 模型 ID
    settings_changed = pyqtSignal()
    theme_changed = pyqtSignal(str)  # 主题名称
    
    def __init__(self, parent=None, config_manager: Optional[ConfigManager] = None):
        """
        初始化设置对话框
        
        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
        """
        super().__init__(parent)
        
        self.config_manager = config_manager or ConfigManager()
        self.model_config_manager = ModelConfigManager(self.config_manager)
        self.theme_manager = ThemeManager()
        
        self._init_ui()
        self._load_settings()
        
        logger.debug("SettingsDialog 初始化完成")
    
    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("设置")
        self.setMinimumSize(700, 500)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 模型管理选项卡
        model_tab = self._create_model_tab()
        tab_widget.addTab(model_tab, "模型管理")
        
        # 参数配置选项卡
        params_tab = self._create_params_tab()
        tab_widget.addTab(params_tab, "参数配置")
        
        # 主题设置选项卡
        theme_tab = self._create_theme_tab()
        tab_widget.addTab(theme_tab, "主题设置")
        
        main_layout.addWidget(tab_widget)
        
        # 添加底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 应用按钮
        apply_button = QPushButton("应用")
        apply_button.clicked.connect(self._on_apply)
        button_layout.addWidget(apply_button)
        
        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def _create_model_tab(self) -> QWidget:
        """
        创建模型管理选项卡
        
        Returns:
            QWidget: 模型管理选项卡组件
        """
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 标题和说明
        title_label = QLabel("OpenAPI 模型配置")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        desc_label = QLabel("管理您的 OpenAPI 模型配置，支持 OpenAI、Azure OpenAI 和自定义服务")
        desc_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(desc_label)
        
        # 模型列表和按钮布局
        list_layout = QHBoxLayout()
        
        # 模型列表
        self.model_list = QListWidget()
        self.model_list.itemSelectionChanged.connect(self._on_model_selection_changed)
        list_layout.addWidget(self.model_list)
        
        # 按钮布局
        button_layout = QVBoxLayout()
        
        self.add_model_button = QPushButton("添加模型")
        self.add_model_button.clicked.connect(self._on_add_model)
        button_layout.addWidget(self.add_model_button)
        
        self.edit_model_button = QPushButton("编辑")
        self.edit_model_button.clicked.connect(self._on_edit_model)
        self.edit_model_button.setEnabled(False)
        button_layout.addWidget(self.edit_model_button)
        
        self.delete_model_button = QPushButton("删除")
        self.delete_model_button.clicked.connect(self._on_delete_model)
        self.delete_model_button.setEnabled(False)
        button_layout.addWidget(self.delete_model_button)
        
        button_layout.addStretch()
        
        list_layout.addLayout(button_layout)
        layout.addLayout(list_layout)
        
        # 当前使用模型选择
        current_model_layout = QFormLayout()
        
        self.current_model_combo = QComboBox()
        self.current_model_combo.currentIndexChanged.connect(self._on_current_model_changed)
        current_model_layout.addRow("当前使用模型:", self.current_model_combo)
        
        # 连接状态指示器
        self.connection_status_label = QLabel("未连接")
        self.connection_status_label.setStyleSheet("color: gray;")
        current_model_layout.addRow("连接状态:", self.connection_status_label)
        
        layout.addLayout(current_model_layout)
        
        tab.setLayout(layout)
        return tab
    
    def _create_params_tab(self) -> QWidget:
        """
        创建参数配置选项卡
        
        Returns:
            QWidget: 参数配置选项卡组件
        """
        tab = QWidget()
        layout = QFormLayout()
        
        # 温度参数
        temp_layout = QHBoxLayout()
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setMinimum(0)
        self.temperature_slider.setMaximum(200)  # 0.0 - 2.0，精度 0.01
        self.temperature_slider.setValue(70)  # 默认 0.7
        self.temperature_slider.valueChanged.connect(self._on_temperature_changed)
        temp_layout.addWidget(self.temperature_slider)
        
        self.temperature_label = QLabel("0.70")
        self.temperature_label.setMinimumWidth(40)
        temp_layout.addWidget(self.temperature_label)
        
        layout.addRow("温度 (Temperature):", temp_layout)
        
        # 添加温度说明
        temp_hint = QLabel("控制输出的随机性。较低的值使输出更确定，较高的值使输出更随机。")
        temp_hint.setStyleSheet("color: gray; font-size: 10px;")
        temp_hint.setWordWrap(True)
        layout.addRow("", temp_hint)
        
        # 最大长度参数
        self.max_tokens_spinbox = QSpinBox()
        self.max_tokens_spinbox.setMinimum(512)
        self.max_tokens_spinbox.setMaximum(4096)
        self.max_tokens_spinbox.setValue(2048)
        self.max_tokens_spinbox.setSuffix(" tokens")
        layout.addRow("最大长度 (Max Tokens):", self.max_tokens_spinbox)
        
        # 添加最大长度说明
        tokens_hint = QLabel("限制模型生成的最大 token 数量。")
        tokens_hint.setStyleSheet("color: gray; font-size: 10px;")
        layout.addRow("", tokens_hint)
        
        tab.setLayout(layout)
        return tab
    
    def _create_theme_tab(self) -> QWidget:
        """
        创建主题设置选项卡
        
        Returns:
            QWidget: 主题设置选项卡组件
        """
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("界面主题")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 说明
        desc_label = QLabel("选择您喜欢的界面主题，更改将立即生效")
        desc_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # 主题选择
        self.theme_group = QButtonGroup()
        
        self.light_theme_radio = QRadioButton("明亮主题")
        self.light_theme_radio.setChecked(True)
        self.light_theme_radio.toggled.connect(self._on_theme_preview)
        self.theme_group.addButton(self.light_theme_radio)
        layout.addWidget(self.light_theme_radio)
        
        light_desc = QLabel("  适合白天使用，清晰明亮的界面风格")
        light_desc.setStyleSheet("color: gray; font-size: 10px; margin-left: 20px;")
        layout.addWidget(light_desc)
        
        layout.addSpacing(10)
        
        self.dark_theme_radio = QRadioButton("暗黑主题")
        self.dark_theme_radio.toggled.connect(self._on_theme_preview)
        self.theme_group.addButton(self.dark_theme_radio)
        layout.addWidget(self.dark_theme_radio)
        
        dark_desc = QLabel("  适合夜间使用，护眼的深色界面风格")
        dark_desc.setStyleSheet("color: gray; font-size: 10px; margin-left: 20px;")
        layout.addWidget(dark_desc)
        
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def _load_settings(self):
        """加载当前设置"""
        try:
            settings = self.config_manager.get_settings()
            
            # 加载模型列表
            self._refresh_model_list()
            
            # 加载参数配置
            self.temperature_slider.setValue(int(settings.temperature * 100))
            self.max_tokens_spinbox.setValue(settings.max_tokens)
            
            # 加载主题设置
            if settings.theme == 'dark':
                self.dark_theme_radio.setChecked(True)
            else:
                self.light_theme_radio.setChecked(True)
            
            logger.debug("设置加载完成")
            
        except Exception as e:
            logger.error(f"加载设置失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"加载设置失败: {e}")
    
    def _refresh_model_list(self):
        """刷新模型列表"""
        try:
            # 清空列表
            self.model_list.clear()
            self.current_model_combo.clear()
            
            # 获取所有模型
            models = self.model_config_manager.get_all_models()
            
            if not models:
                # 没有模型时显示提示
                item = QListWidgetItem("暂无模型配置，请点击\"添加模型\"按钮")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.model_list.addItem(item)
                self.connection_status_label.setText("未配置")
                self.connection_status_label.setStyleSheet("color: gray;")
                return
            
            # 获取当前激活的模型
            active_model = self.model_config_manager.get_active_model()
            active_model_id = active_model.id if active_model else None
            
            # 添加模型到列表
            for model in models:
                # 创建列表项
                display_text = f"{model.name}"
                if model.id == active_model_id:
                    display_text += " (当前使用)"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, model.id)
                self.model_list.addItem(item)
                
                # 添加到下拉菜单
                self.current_model_combo.addItem(model.name, model.id)
            
            # 设置当前选中的模型
            if active_model_id:
                for i in range(self.current_model_combo.count()):
                    if self.current_model_combo.itemData(i) == active_model_id:
                        self.current_model_combo.setCurrentIndex(i)
                        break
                
                # 更新连接状态（简化版，实际应该测试连接）
                self.connection_status_label.setText("已配置")
                self.connection_status_label.setStyleSheet("color: green;")
            else:
                self.connection_status_label.setText("未选择")
                self.connection_status_label.setStyleSheet("color: orange;")
            
            logger.debug(f"模型列表刷新完成，共 {len(models)} 个模型")
            
        except Exception as e:
            logger.error(f"刷新模型列表失败: {e}", exc_info=True)
    
    def _on_model_selection_changed(self):
        """模型列表选择变更处理"""
        has_selection = len(self.model_list.selectedItems()) > 0
        self.edit_model_button.setEnabled(has_selection)
        self.delete_model_button.setEnabled(has_selection)
    
    def _on_add_model(self):
        """添加模型按钮点击处理"""
        try:
            logger.info("打开添加模型对话框...")
            import sys
            sys.stdout.flush()  # 强制刷新标准输出
            
            dialog = ModelConfigDialog(self)
            logger.info("模型配置对话框创建成功")
            sys.stdout.flush()
            
            result = dialog.exec()
            logger.info(f"对话框关闭，结果: {result}")
            
            if result == QDialog.DialogCode.Accepted:
                logger.info("用户确认添加模型")
                model_config = dialog.get_model_config()
                logger.info(f"获取模型配置: {model_config.name}")
                
                # 检查是否是第一个模型
                is_first_model = not self.model_config_manager.has_models()
                logger.info(f"是否为第一个模型: {is_first_model}")
                
                if self.model_config_manager.add_model(model_config):
                    logger.info(f"模型添加到配置管理器成功: {model_config.name}")
                    QMessageBox.information(self, "成功", f"模型 '{model_config.name}' 添加成功")
                    
                    logger.info("刷新模型列表...")
                    self._refresh_model_list()
                    logger.info("模型列表刷新完成")
                    
                    # 如果是第一个模型，自动设置为活动模型并发出信号
                    if is_first_model:
                        logger.info("设置为活动模型...")
                        self.model_config_manager.set_active_model(model_config.id)
                        logger.info("发出模型改变信号...")
                        self.model_changed.emit(model_config.id)
                        logger.info(f"自动设置第一个模型为活动模型完成: {model_config.name}")
                else:
                    logger.error("添加模型到配置管理器失败")
                    QMessageBox.warning(self, "失败", "添加模型失败，请检查配置")
            else:
                logger.info("用户取消添加模型")
                
        except Exception as e:
            logger.error(f"添加模型过程中发生异常: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"添加模型时发生错误: {str(e)}")
    
    def _on_edit_model(self):
        """编辑模型按钮点击处理"""
        selected_items = self.model_list.selectedItems()
        if not selected_items:
            return
        
        # 获取选中的模型 ID
        model_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        model_config = self.model_config_manager.get_model_config(model_id)
        
        if not model_config:
            QMessageBox.warning(self, "错误", "无法加载模型配置")
            return
        
        # 显示编辑对话框
        dialog = ModelConfigDialog(self, model_config)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_config = dialog.get_model_config()
            
            if self.model_config_manager.update_model(updated_config):
                QMessageBox.information(self, "成功", f"模型 '{updated_config.name}' 更新成功")
                self._refresh_model_list()
                logger.info(f"更新模型成功: {updated_config.name}")
            else:
                QMessageBox.warning(self, "失败", "更新模型失败")
    
    def _on_delete_model(self):
        """删除模型按钮点击处理"""
        selected_items = self.model_list.selectedItems()
        if not selected_items:
            return
        
        # 获取选中的模型 ID
        model_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        model_config = self.model_config_manager.get_model_config(model_id)
        
        if not model_config:
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除模型 '{model_config.name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.model_config_manager.delete_model(model_id):
                QMessageBox.information(self, "成功", f"模型 '{model_config.name}' 已删除")
                self._refresh_model_list()
                logger.info(f"删除模型成功: {model_config.name}")
            else:
                QMessageBox.warning(self, "失败", "删除模型失败")
    
    def _on_current_model_changed(self, index: int):
        """当前模型下拉菜单变更处理"""
        if index < 0:
            return
        
        model_id = self.current_model_combo.itemData(index)
        if model_id:
            logger.debug(f"选择模型: {model_id}")
    
    def _on_temperature_changed(self, value: int):
        """温度滑块变更处理"""
        temp = value / 100.0
        self.temperature_label.setText(f"{temp:.2f}")
    
    def _on_theme_preview(self, checked: bool):
        """主题预览处理（实时切换）"""
        if not checked:
            return
        
        # 获取选中的主题
        theme = 'dark' if self.dark_theme_radio.isChecked() else 'light'
        
        # 立即应用主题预览
        if self.theme_manager.load_theme(theme):
            logger.debug(f"主题预览: {theme}")
        else:
            logger.warning(f"主题预览失败: {theme}")
    
    def _on_apply(self):
        """应用按钮点击处理"""
        self._save_settings()
    
    def _on_ok(self):
        """确定按钮点击处理"""
        self._save_settings()
        self.accept()
    
    def _save_settings(self):
        """保存设置"""
        try:
            # 保存当前使用的模型
            current_index = self.current_model_combo.currentIndex()
            if current_index >= 0:
                model_id = self.current_model_combo.itemData(current_index)
                if model_id:
                    old_model = self.model_config_manager.get_active_model()
                    if self.model_config_manager.set_active_model(model_id):
                        # 如果模型发生变化，发出信号
                        if not old_model or old_model.id != model_id:
                            self.model_changed.emit(model_id)
                            logger.info(f"模型已切换: {model_id}")
            
            # 保存参数配置
            temperature = self.temperature_slider.value() / 100.0
            max_tokens = self.max_tokens_spinbox.value()
            
            # 保存主题设置
            new_theme = 'dark' if self.dark_theme_radio.isChecked() else 'light'
            old_theme = self.config_manager.get_settings().theme
            
            # 更新配置
            self.config_manager.update_settings(
                temperature=temperature,
                max_tokens=max_tokens,
                theme=new_theme
            )
            
            # 如果主题发生变化，应用新主题并发出信号
            if new_theme != old_theme:
                if self.theme_manager.load_theme(new_theme):
                    self.theme_changed.emit(new_theme)
                    logger.info(f"主题已切换: {new_theme}")
            
            # 发出设置变更信号
            self.settings_changed.emit()
            
            logger.info("设置保存成功")
            
        except Exception as e:
            logger.error(f"保存设置失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"保存设置失败: {e}")
