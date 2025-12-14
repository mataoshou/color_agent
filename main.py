"""
AI Chat Agent 应用程序入口

提供应用程序的初始化、配置检查、首次使用引导和主窗口启动功能。
"""

import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from src.utils.config import ConfigManager, Settings
from src.utils.logger import LoggerManager
from src.services.system_context import SystemContextProvider
from src.services.application_controller import ApplicationController
from src.services.model_config_manager import ModelConfigManager
from src.gui.main_window import MainWindow
from src.gui.model_config_dialog import ModelConfigDialog
from src.gui.settings_dialog import SettingsDialog
from src.utils.theme_manager import ThemeManager


def create_directory_structure():
    """
    创建必要的目录结构
    
    创建 sessions/ 和 logs/ 目录（如果不存在）
    """
    directories = ['sessions', 'logs']
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"创建目录: {directory}")


def check_and_create_config() -> ConfigManager:
    """
    检查配置文件是否存在，如果不存在则创建默认配置
    
    Returns:
        ConfigManager: 配置管理器实例
    """
    config_manager = ConfigManager()
    
    if not os.path.exists(ConfigManager.DEFAULT_CONFIG_PATH):
        print("配置文件不存在，创建默认配置...")
        config_manager.settings = Settings()
        config_manager.save()
        print(f"默认配置文件已创建: {ConfigManager.DEFAULT_CONFIG_PATH}")
    else:
        print(f"加载配置文件: {ConfigManager.DEFAULT_CONFIG_PATH}")
        try:
            config_manager.load()
        except ValueError as e:
            print(f"警告: {e}")
    
    return config_manager


def initialize_logging(config_manager: ConfigManager) -> logging.Logger:
    """
    初始化日志系统
    
    Args:
        config_manager: 配置管理器实例
        
    Returns:
        logging.Logger: 日志对象
    """
    settings = config_manager.get_settings()
    
    # 初始化日志系统
    logger = LoggerManager.initialize(
        log_file=settings.log_file,
        log_level=settings.log_level,
        max_bytes=10 * 1024 * 1024,  # 10MB
        backup_count=5
    )
    
    # 记录系统信息
    logger.info("=" * 60)
    logger.info("AI Chat Agent 启动")
    logger.info("=" * 60)
    
    # 记录 Python 版本和平台信息
    import platform
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"操作系统: {platform.system()} {platform.release()}")
    logger.info(f"平台: {platform.platform()}")
    
    return logger


def show_first_time_guide(parent=None) -> bool:
    """
    显示首次使用引导对话框
    
    Args:
        parent: 父窗口
        
    Returns:
        bool: 用户是否完成了模型配置
    """
    # 显示欢迎对话框
    welcome_msg = (
        "欢迎使用 AI Chat Agent！\n\n"
        "这是您第一次使用本应用。\n"
        "在开始之前，您需要添加至少一个 AI 模型配置。\n\n"
        "支持的模型服务：\n"
        "- OpenAI (GPT-4, GPT-3.5-turbo 等)\n"
        "- Azure OpenAI\n"
        "- 其他 OpenAPI 兼容服务\n\n"
        "点击\"确定\"开始配置您的第一个模型。"
    )
    
    reply = QMessageBox.information(
        parent,
        "欢迎使用",
        welcome_msg,
        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
    )
    
    if reply == QMessageBox.StandardButton.Cancel:
        return False
    
    # 显示模型配置对话框
    dialog = ModelConfigDialog(parent)
    if dialog.exec() == ModelConfigDialog.DialogCode.Accepted:
        return True
    
    return False


def add_first_model(config_manager: ConfigManager, parent=None) -> bool:
    """
    引导用户添加第一个模型配置
    
    Args:
        config_manager: 配置管理器实例
        parent: 父窗口
        
    Returns:
        bool: 是否成功添加模型
    """
    logger = logging.getLogger(__name__)
    
    # 显示首次使用引导
    if not show_first_time_guide(parent):
        logger.warning("用户取消了首次使用引导")
        return False
    
    # 获取模型配置
    dialog = ModelConfigDialog(parent)
    if dialog.exec() != ModelConfigDialog.DialogCode.Accepted:
        logger.warning("用户取消了模型配置")
        return False
    
    model_config = dialog.get_model_config()
    
    # 添加模型配置
    model_manager = ModelConfigManager(config_manager)
    if not model_manager.add_model(model_config):
        QMessageBox.critical(
            parent,
            "添加失败",
            "添加模型配置失败，请检查输入信息。"
        )
        logger.error("添加模型配置失败")
        return False
    
    # 设置为激活模型
    if not model_manager.set_active_model(model_config.id):
        logger.warning("设置激活模型失败")
    
    QMessageBox.information(
        parent,
        "配置成功",
        f"模型配置已添加：{model_config.name}\n\n"
        "您现在可以开始使用 AI Chat Agent 了！"
    )
    
    logger.info(f"首次模型配置完成: {model_config.name}")
    return True


def setup_application_connections(app_controller: ApplicationController, main_window: MainWindow):
    """
    设置应用程序的信号槽连接
    
    Args:
        app_controller: 应用程序控制器
        main_window: 主窗口
    """
    logger = logging.getLogger(__name__)
    
    # 获取 GUI 组件
    chat_widget = main_window.get_chat_widget()
    session_sidebar = main_window.get_session_sidebar()
    file_browser = main_window.get_file_browser()
    
    # ========== 消息相关连接 ==========
    # 用户发送消息
    def on_message_sent(message: str):
        """处理用户发送消息"""
        # 添加用户消息到界面
        chat_widget.add_user_message(message)
        # 显示正在输入指示器
        chat_widget.show_typing_indicator()
        # 发送到控制器处理
        app_controller.on_send_message(message)
    
    chat_widget.message_sent.connect(on_message_sent)
    
    # AI 响应流式显示
    # 使用标志跟踪是否已启动流式响应
    streaming_started = [False]
    
    def on_message_chunk(chunk: str):
        """处理响应块"""
        if not streaming_started[0]:
            # 第一个块，启动流式显示
            chat_widget.start_streaming_response()
            streaming_started[0] = True
            logger.debug("启动流式响应显示")
        
        # 追加文本块
        chat_widget.append_streaming_chunk(chunk)
    
    app_controller.message_chunk.connect(on_message_chunk)
    
    def on_message_complete(response: str):
        """处理消息完成"""
        # 如果流式响应已启动，完成它
        if streaming_started[0]:
            chat_widget.finish_streaming_response()
            streaming_started[0] = False
            logger.debug("完成流式响应显示")
        else:
            # 如果没有收到任何chunk（流式响应未启动），直接添加完整消息
            logger.warning("未收到流式响应chunk，直接添加完整消息")
            chat_widget.add_assistant_message(response)
        
        # 验证消息是否正确显示
        message_list = chat_widget.get_message_list()
        if message_list.count() > 0:
            last_item = message_list.item(message_list.count() - 1)
            last_widget = message_list.itemWidget(last_item)
            
            from src.gui.message_bubble import MessageBubble
            # 如果最后一个不是AI消息气泡，或者内容为空，说明有问题
            if not isinstance(last_widget, MessageBubble):
                logger.error("最后一个组件不是消息气泡")
                # 添加完整消息作为备份
                chat_widget.add_assistant_message(response)
            elif last_widget.role != 'assistant':
                logger.error("最后一个消息不是AI消息")
                # 添加完整消息
                chat_widget.add_assistant_message(response)
            # 获取消息气泡的内容文本
            content = last_widget.content
            if hasattr(content, 'toPlainText'):
                content_text = content.toPlainText()
            elif hasattr(content, 'text'):
                content_text = content.text()
            else:
                content_text = str(content)
            
            if not content_text.strip():
                logger.error("最后一个AI消息内容为空")
                # 更新内容
                last_widget.update_content(response)
                last_item.setSizeHint(last_widget.sizeHint())
        else:
            logger.error("消息列表为空")
            chat_widget.add_assistant_message(response)
    
    app_controller.message_complete.connect(on_message_complete)
    
    # 工具调用可视化
    app_controller.tool_call_started.connect(chat_widget.add_tool_call_start)
    app_controller.tool_call_finished.connect(chat_widget.add_tool_call_finish)
    
    # 会话回滚
    chat_widget.rollback_requested.connect(app_controller.on_rollback_requested)
    chat_widget.rollback_requested.connect(chat_widget.apply_rollback)
    
    # ========== 会话相关连接 ==========
    # 新建会话
    main_window.new_session_requested.connect(app_controller.on_create_session)
    session_sidebar.session_created.connect(app_controller.on_create_session)
    
    # 加载会话
    session_sidebar.session_selected.connect(app_controller.on_load_session)
    
    # 保存会话
    main_window.save_session_requested.connect(app_controller.on_save_session)
    
    # 删除会话
    session_sidebar.session_deleted.connect(app_controller.on_delete_session)
    
    # 重命名会话
    session_sidebar.session_renamed.connect(app_controller.on_rename_session)
    
    # 会话列表更新
    app_controller.session_created.connect(lambda: app_controller.load_sessions_list())
    app_controller.session_loaded.connect(chat_widget.load_session_messages)
    app_controller.sessions_list_updated.connect(session_sidebar.load_sessions)
    
    # ========== 文件操作相关连接 ==========
    # 工作目录变更
    file_browser.directory_changed.connect(app_controller.on_directory_changed)
    
    # AI 读取/修改文件
    file_browser.ai_read_requested.connect(app_controller.on_ai_read_file)
    file_browser.ai_modify_requested.connect(app_controller.on_ai_modify_file)
    
    # ========== 模型相关连接 ==========
    # 主窗口模型选择器
    main_window.model_switch_requested.connect(app_controller.on_model_changed)
    
    # 模型切换
    app_controller.model_switched.connect(main_window.update_model_status)
    app_controller.model_switched.connect(lambda name: main_window.update_connection_status(True))
    
    # 模型连接失败
    app_controller.model_connection_failed.connect(
        lambda msg: main_window.update_connection_status(False, "连接失败")
    )
    
    # ========== 错误和状态相关连接 ==========
    # 错误提示
    app_controller.error_occurred.connect(
        lambda msg: main_window.show_error_dialog("错误", msg)
    )
    
    # 状态消息
    app_controller.status_message.connect(main_window.show_status_message)
    
    # ========== 设置对话框连接 ==========
    def show_settings_dialog():
        """显示设置对话框"""
        # 记录对话框打开前的状态
        had_agent_before = app_controller.agent_manager is not None
        
        dialog = SettingsDialog(main_window, app_controller.config_manager)
        
        # 用于跟踪模型是否改变
        model_changed_flag = [False]
        
        def on_model_changed_internal(model_id: str):
            """内部模型改变处理"""
            model_changed_flag[0] = True
            try:
                app_controller.on_model_changed(model_id)
            except Exception as e:
                logger.error(f"模型切换失败: {e}", exc_info=True)
        
        # 连接设置对话框的信号
        dialog.model_changed.connect(on_model_changed_internal)
        dialog.theme_changed.connect(lambda theme: theme_manager.load_theme(theme))
        
        # 显示对话框
        result = dialog.exec()
        
        if result == SettingsDialog.DialogCode.Accepted:
            logger.info("设置已更新")
            
            # 如果之前没有 agent 但现在有模型了，尝试初始化
            if not had_agent_before and app_controller.model_config_manager.has_models():
                if not model_changed_flag[0]:  # 如果还没有初始化过
                    logger.info("检测到首次添加模型，尝试初始化...")
                    if app_controller.initialize():
                        main_window.show_status_message("模型配置成功，可以开始对话了", 3000)
                        logger.info("首次模型初始化成功")
            
            # 更新主窗口的模型列表和状态显示
            models = app_controller.model_config_manager.get_all_models()
            active_model = app_controller.model_config_manager.get_active_model()
            active_model_id = active_model.id if active_model else None
            main_window.update_model_list(models, active_model_id)
            
            active_model_name = app_controller.get_active_model_name()
            main_window.update_model_status(active_model_name)
            if app_controller.agent_manager:
                main_window.update_connection_status(True)
            else:
                main_window.update_connection_status(False, "未初始化")
    
    main_window.settings_requested.connect(show_settings_dialog)
    
    logger.info("应用程序信号槽连接完成")


def main():
    """应用程序主入口"""
    # 创建 QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("AI Chat Agent")
    app.setOrganizationName("ChatAgent")
    
    # 步骤 1: 创建目录结构
    print("检查目录结构...")
    create_directory_structure()
    
    # 步骤 2: 检查并创建配置文件
    print("检查配置文件...")
    config_manager = check_and_create_config()
    
    # 步骤 3: 初始化日志系统
    print("初始化日志系统...")
    logger = initialize_logging(config_manager)
    
    # 步骤 4: 初始化系统上下文
    logger.info("初始化系统上下文...")
    system_context = SystemContextProvider()
    context = system_context.get_context()
    logger.info(f"工作目录: {context.working_directory}")
    logger.info(f"操作系统: {context.os_type} {context.os_version}")
    logger.info(f"Python 版本: {context.python_version}")
    
    # 步骤 5: 应用主题
    settings = config_manager.get_settings()
    logger.info(f"应用主题: {settings.theme}")
    theme_manager = ThemeManager()
    theme_manager.load_theme(settings.theme)
    
    # 步骤 7: 创建主窗口
    logger.info("创建主窗口...")
    main_window = MainWindow()
    main_window.resize(settings.window_width, settings.window_height)
    
    # 步骤 8: 创建应用程序控制器
    logger.info("创建应用程序控制器...")
    app_controller = ApplicationController()
    
    # 步骤 9: 设置信号槽连接
    logger.info("设置信号槽连接...")
    setup_application_connections(app_controller, main_window)
    
    # 步骤 10: 显示主窗口（先显示界面）
    logger.info("显示主窗口...")
    main_window.show()
    
    # 步骤 11: 初始化控制器
    logger.info("初始化应用程序控制器...")
    if not app_controller.initialize():
        logger.warning("应用程序控制器初始化失败，可能是没有模型配置")
        # 检查是否是因为没有模型配置
        model_manager = ModelConfigManager(config_manager)
        if not model_manager.has_models():
            # 显示友好提示，引导用户配置模型
            main_window.show_status_message("请先在设置中添加 AI 模型配置", 0)
            logger.info("等待用户配置模型")
        else:
            # 其他初始化错误
            main_window.show_status_message("初始化失败，请检查配置或查看日志", 0)
            logger.error("应用程序控制器初始化失败（非模型配置问题）")
    
    # 步骤 12: 加载会话列表
    logger.info("加载会话列表...")
    app_controller.load_sessions_list()
    
    # 步骤 13: 更新模型列表和状态显示
    models = app_controller.model_config_manager.get_all_models()
    active_model = app_controller.model_config_manager.get_active_model()
    active_model_id = active_model.id if active_model else None
    main_window.update_model_list(models, active_model_id)
    
    active_model_name = app_controller.get_active_model_name()
    main_window.update_model_status(active_model_name)
    if app_controller.agent_manager:
        main_window.update_connection_status(True)
        # 如果初始化成功且没有会话，显示欢迎提示
        sessions = app_controller.session_manager.list_sessions()
        if not sessions:
            main_window.show_status_message("欢迎使用 AI Chat Agent！点击\"新建会话\"开始对话", 5000)
            logger.info("显示欢迎提示")
    else:
        main_window.update_connection_status(False, "未初始化")
    
    logger.info("应用程序启动完成")
    logger.info("=" * 60)
    
    # 运行应用程序
    exit_code = app.exec()
    
    # 清理资源
    logger.info("应用程序退出，清理资源...")
    app_controller.cleanup()
    logger.info("清理完成")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
