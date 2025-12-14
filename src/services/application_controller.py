"""
应用程序控制器模块

连接前端 GUI 和后端 LangChain 架构，管理应用程序的核心业务逻辑。
"""

import logging
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

from src.utils.config import ConfigManager
from src.services.model_config_manager import ModelConfigManager
from src.services.session_manager import SessionManager, Session
from src.services.system_context import SystemContextProvider
from src.backend.agent import AgentExecutorManager
from src.workers.chat_worker import ChatWorker

logger = logging.getLogger(__name__)


class ApplicationController(QObject):
    """
    应用程序控制器
    
    负责连接前端 GUI 和后端服务，处理所有业务逻辑。
    
    Signals:
        # 消息相关信号
        message_chunk: 流式响应的文本块
        message_complete: 消息生成完成
        tool_call_started: 工具调用开始（携带工具名和参数）
        tool_call_finished: 工具调用完成（携带工具名和结果）
        
        # 模型相关信号
        model_switched: 模型切换成功（携带模型名称）
        model_connection_failed: 模型连接失败（携带错误信息）
        
        # 会话相关信号
        session_created: 会话创建（携带会话 ID）
        session_loaded: 会话加载（携带会话数据）
        session_saved: 会话保存（携带会话 ID）
        session_deleted: 会话删除（携带会话 ID）
        session_renamed: 会话重命名（携带会话 ID 和新名称）
        sessions_list_updated: 会话列表更新（携带会话列表）
        
        # 系统上下文相关信号
        working_directory_changed: 工作目录变更（携带新路径）
        
        # 错误相关信号
        error_occurred: 错误发生（携带错误信息）
        
        # 状态相关信号
        status_message: 状态消息（携带消息文本和超时时间）
    """
    
    # 消息相关信号
    message_chunk = pyqtSignal(str)
    message_complete = pyqtSignal(str)
    tool_call_started = pyqtSignal(str, str)  # tool_name, input_str
    tool_call_finished = pyqtSignal(str, str)  # tool_name, output_str
    
    # 模型相关信号
    model_switched = pyqtSignal(str)  # model_name
    model_connection_failed = pyqtSignal(str)  # error_message
    
    # 会话相关信号
    session_created = pyqtSignal(str)  # session_id
    session_loaded = pyqtSignal(dict)  # session_data
    session_saved = pyqtSignal(str)  # session_id
    session_deleted = pyqtSignal(str)  # session_id
    session_renamed = pyqtSignal(str, str)  # session_id, new_name
    sessions_list_updated = pyqtSignal(list)  # sessions_list
    
    # 系统上下文相关信号
    working_directory_changed = pyqtSignal(str)  # directory_path
    
    # 错误相关信号
    error_occurred = pyqtSignal(str)  # error_message
    
    # 状态相关信号
    status_message = pyqtSignal(str, int)  # message, timeout
    
    def __init__(self, parent: Optional[QObject] = None):
        """
        初始化应用程序控制器
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        
        # 初始化服务组件
        self.config_manager = ConfigManager()
        self.model_config_manager = ModelConfigManager(self.config_manager)
        self.session_manager = SessionManager()
        self.system_context_provider = SystemContextProvider()
        
        # Agent 管理器（延迟初始化）
        self.agent_manager: Optional[AgentExecutorManager] = None
        
        # 当前工作线程
        self.current_worker: Optional[ChatWorker] = None
        
        logger.info("ApplicationController 初始化完成")
    
    def initialize(self) -> bool:
        """
        初始化控制器
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 检查是否有可用的模型
            if not self.model_config_manager.has_models():
                logger.warning("没有可用的模型配置")
                return False
            
            # 获取激活的模型
            active_model = self.model_config_manager.get_active_model()
            if not active_model:
                logger.warning("没有激活的模型")
                return False
            
            # 初始化 Agent 管理器
            self._initialize_agent_manager()
            
            # 加载工作目录
            settings = self.config_manager.get_settings()
            if settings.working_directory:
                self.system_context_provider.set_working_directory(settings.working_directory)
            
            logger.info("ApplicationController 初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"ApplicationController 初始化失败: {e}", exc_info=True)
            self.error_occurred.emit(f"初始化失败: {e}")
            return False
    
    def _initialize_agent_manager(self) -> None:
        """初始化 Agent 管理器"""
        try:
            # 获取激活的模型配置
            active_model = self.model_config_manager.get_active_model()
            if not active_model:
                raise ValueError("没有激活的模型")
            
            # 获取系统上下文
            system_context = self.system_context_provider.get_context()
            
            # 获取配置参数
            settings = self.config_manager.get_settings()
            
            # 创建 Agent 管理器
            self.agent_manager = AgentExecutorManager(
                api_base=active_model.api_base,
                api_key=active_model.api_key,
                model_name=active_model.model_name,
                working_directory=system_context.working_directory,
                system_context=system_context.to_dict(),
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            
            # 初始化 Agent 管理器（创建 callback_handler、LLM、tools 等）
            # 注意：callback 函数将在 ChatWorker 中动态设置
            self.agent_manager.initialize()
            
            logger.info(f"Agent 管理器初始化成功: {active_model.name}")
            
        except Exception as e:
            logger.error(f"Agent 管理器初始化失败: {e}", exc_info=True)
            raise
    
    def on_send_message(self, message: str) -> None:
        """
        处理发送消息
        
        Args:
            message: 用户消息
        """
        try:
            # 检查 Agent 是否已初始化
            if not self.agent_manager:
                self.error_occurred.emit("Agent 未初始化，请先配置模型")
                return
            
            # 检查是否有当前会话
            if not self.session_manager.get_current_session():
                # 自动创建新会话
                self.on_create_session()
            
            # 添加用户消息到会话
            self.session_manager.add_message('user', message)
            
            # 停止之前的工作线程（如果有）
            if self.current_worker and self.current_worker.isRunning():
                self.current_worker.stop()
            
            # 创建新的工作线程
            self.current_worker = ChatWorker(self.agent_manager, message)
            
            # 连接信号
            self.current_worker.message_chunk.connect(self.message_chunk.emit)
            self.current_worker.message_complete.connect(self._on_message_complete)
            self.current_worker.tool_call_started.connect(self.tool_call_started.emit)
            self.current_worker.tool_call_finished.connect(self.tool_call_finished.emit)
            self.current_worker.error_occurred.connect(self._on_worker_error)
            
            # 启动工作线程
            self.current_worker.start()
            
            logger.info(f"开始处理消息: {message[:50]}...")
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}", exc_info=True)
            self.error_occurred.emit(f"发送消息失败: {e}")
    
    def _on_message_complete(self, response: str) -> None:
        """
        消息完成处理
        
        Args:
            response: AI 响应
        """
        try:
            # 添加 AI 响应到会话
            self.session_manager.add_message('assistant', response)
            
            # 发出完成信号
            self.message_complete.emit(response)
            
            # 更新会话列表
            self._refresh_sessions_list()
            
            logger.info("消息处理完成")
            
        except Exception as e:
            logger.error(f"消息完成处理失败: {e}", exc_info=True)
    
    def _on_worker_error(self, error_message: str) -> None:
        """
        工作线程错误处理
        
        Args:
            error_message: 错误消息
        """
        self.error_occurred.emit(error_message)
        self.model_connection_failed.emit(error_message)
    
    def on_model_changed(self, model_id: str) -> None:
        """
        处理模型切换
        
        Args:
            model_id: 模型 ID
        """
        try:
            # 获取模型配置
            model_config = self.model_config_manager.get_model_config(model_id)
            if not model_config:
                self.error_occurred.emit(f"模型不存在: {model_id}")
                return
            
            # 设置为激活模型
            if not self.model_config_manager.set_active_model(model_id):
                self.error_occurred.emit("切换模型失败")
                return
            
            # 重新初始化 Agent 管理器
            self._initialize_agent_manager()
            
            # 发出模型切换信号
            self.model_switched.emit(model_config.name)
            self.status_message.emit(f"已切换到模型: {model_config.name}", 3000)
            
            logger.info(f"模型切换成功: {model_config.name}")
            
        except Exception as e:
            logger.error(f"模型切换失败: {e}", exc_info=True)
            self.error_occurred.emit(f"模型切换失败: {e}")
            self.model_connection_failed.emit(str(e))
    
    def on_create_session(self, name: Optional[str] = None) -> None:
        """
        处理创建会话
        
        Args:
            name: 会话名称
        """
        try:
            # 创建新会话
            session = self.session_manager.create_session(name)
            
            # 清空 LangChain Memory（新会话没有历史）
            if self.agent_manager:
                self.agent_manager.clear_memory()
                logger.info("已清空 LangChain Memory（新会话）")
            
            # 发出会话创建信号
            self.session_created.emit(session.session_id)
            self.status_message.emit(f"已创建会话: {session.name}", 3000)
            
            # 刷新会话列表前，检查会话数量
            logger.info(f"刷新会话列表前，会话数量: {len(self.session_manager.list_sessions())}")
            
            # 刷新会话列表
            self._refresh_sessions_list()
            
            # 刷新会话列表后，检查会话数量
            logger.info(f"刷新会话列表后，会话数量: {len(self.session_manager.list_sessions())}")
            
            # 获取所有会话，检查新会话是否在列表中
            all_sessions = self.session_manager.list_sessions()
            session_ids = [s.get('session_id') for s in all_sessions]
            logger.info(f"所有会话ID列表: {session_ids}")
            if session.session_id in session_ids:
                logger.info(f"新会话 {session.session_id} 已在会话列表中，位置: {session_ids.index(session.session_id) + 1}")
            else:
                logger.error(f"新会话 {session.session_id} 不在会话列表中")
            
            logger.info(f"会话创建成功: {session.session_id}")
            
        except Exception as e:
            logger.error(f"创建会话失败: {e}", exc_info=True)
            self.error_occurred.emit(f"创建会话失败: {e}")
    
    def on_load_session(self, session_id: str) -> None:
        """
        处理加载会话
        
        Args:
            session_id: 会话 ID
        """
        try:
            # 保存当前会话（如果有）
            current_session = self.session_manager.get_current_session()
            if current_session:
                self.session_manager.save_session(current_session)
            
            # 加载会话
            session = self.session_manager.load_session(session_id)
            
            # 将历史消息加载到 LangChain Memory
            if self.agent_manager:
                messages = [{'role': msg.role, 'content': msg.content} for msg in session.messages]
                self.agent_manager.load_memory_from_messages(messages)
                logger.info(f"已将 {len(messages)} 条消息加载到 LangChain Memory")
            
            # 获取回滚点
            rollback_point = self.session_manager.get_rollback_point()
            
            # 准备会话数据
            session_data = {
                'session_id': session.session_id,
                'name': session.name,
                'messages': [msg.to_dict() for msg in session.messages],
                'created_at': session.created_at,
                'updated_at': session.updated_at,
                'rollback_point': rollback_point
            }
            
            # 发出会话加载信号
            self.session_loaded.emit(session_data)
            self.status_message.emit(f"已加载会话: {session.name}", 3000)
            
            logger.info(f"会话加载成功: {session_id}")
            
        except FileNotFoundError:
            self.error_occurred.emit(f"会话不存在: {session_id}")
        except ValueError as e:
            self.error_occurred.emit(f"会话文件损坏: {session_id}")
        except Exception as e:
            logger.error(f"加载会话失败: {e}", exc_info=True)
            self.error_occurred.emit(f"加载会话失败: {e}")
    
    def on_save_session(self) -> None:
        """处理保存会话"""
        try:
            current_session = self.session_manager.get_current_session()
            if not current_session:
                self.status_message.emit("没有需要保存的会话", 3000)
                return
            
            # 保存会话
            self.session_manager.save_session(current_session)
            
            # 发出会话保存信号
            self.session_saved.emit(current_session.session_id)
            self.status_message.emit(f"会话已保存: {current_session.name}", 3000)
            
            logger.info(f"会话保存成功: {current_session.session_id}")
            
        except Exception as e:
            logger.error(f"保存会话失败: {e}", exc_info=True)
            self.error_occurred.emit(f"保存会话失败: {e}")
    
    def on_delete_session(self, session_id: str) -> None:
        """
        处理删除会话
        
        Args:
            session_id: 会话 ID
        """
        try:
            # 删除会话
            self.session_manager.delete_session(session_id)
            
            # 发出会话删除信号
            self.session_deleted.emit(session_id)
            self.status_message.emit("会话已删除", 3000)
            
            # 刷新会话列表
            self._refresh_sessions_list()
            
            logger.info(f"会话删除成功: {session_id}")
            
        except FileNotFoundError:
            self.error_occurred.emit(f"会话不存在: {session_id}")
        except Exception as e:
            logger.error(f"删除会话失败: {e}", exc_info=True)
            self.error_occurred.emit(f"删除会话失败: {e}")
    
    def on_rename_session(self, session_id: str, new_name: str) -> None:
        """
        处理重命名会话
        
        Args:
            session_id: 会话 ID
            new_name: 新名称
        """
        try:
            # 重命名会话
            self.session_manager.rename_session(session_id, new_name)
            
            # 发出会话重命名信号
            self.session_renamed.emit(session_id, new_name)
            self.status_message.emit(f"会话已重命名: {new_name}", 3000)
            
            # 刷新会话列表
            self._refresh_sessions_list()
            
            logger.info(f"会话重命名成功: {session_id} -> {new_name}")
            
        except FileNotFoundError:
            self.error_occurred.emit(f"会话不存在: {session_id}")
        except Exception as e:
            logger.error(f"重命名会话失败: {e}", exc_info=True)
            self.error_occurred.emit(f"重命名会话失败: {e}")
    
    def on_directory_changed(self, directory: str) -> None:
        """
        处理工作目录变更
        
        Args:
            directory: 新的工作目录路径
        """
        try:
            # 更新系统上下文
            if not self.system_context_provider.set_working_directory(directory):
                self.error_occurred.emit(f"无效的目录路径: {directory}")
                return
            
            # 更新配置
            self.config_manager.update_settings(working_directory=directory)
            
            # 重新初始化 Agent（更新系统上下文）
            if self.agent_manager:
                self._initialize_agent_manager()
            
            # 发出目录变更信号
            self.working_directory_changed.emit(directory)
            self.status_message.emit(f"工作目录已更新: {directory}", 3000)
            
            logger.info(f"工作目录变更成功: {directory}")
            
        except Exception as e:
            logger.error(f"工作目录变更失败: {e}", exc_info=True)
            self.error_occurred.emit(f"工作目录变更失败: {e}")
    
    def on_rollback_requested(self, message_index: int) -> None:
        """
        处理会话回滚请求
        
        Args:
            message_index: 消息索引（在列表中的位置）
        """
        try:
            # 获取当前会话
            current_session = self.session_manager.get_current_session()
            if not current_session:
                self.error_occurred.emit("没有当前会话，无法回滚")
                return
            
            # 执行回滚
            if self.session_manager.rollback_to_message(message_index):
                self.status_message.emit(f"已回滚到第 {message_index + 1} 条消息", 3000)
                logger.info(f"会话回滚成功: 消息索引 {message_index}")
            else:
                self.error_occurred.emit("回滚失败")
            
        except Exception as e:
            logger.error(f"会话回滚失败: {e}", exc_info=True)
            self.error_occurred.emit(f"会话回滚失败: {e}")
    
    def on_ai_read_file(self, file_path: str) -> None:
        """
        处理 AI 阅读文件请求
        
        Args:
            file_path: 文件路径
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 构建消息
            message = f"请阅读以下文件内容：\n\n文件路径: {file_path}\n\n内容:\n{content}"
            
            # 发送消息
            self.on_send_message(message)
            
            logger.info(f"AI 阅读文件: {file_path}")
            
        except Exception as e:
            logger.error(f"AI 阅读文件失败: {e}", exc_info=True)
            self.error_occurred.emit(f"读取文件失败: {e}")
    
    def on_ai_modify_file(self, file_path: str) -> None:
        """
        处理 AI 修改文件请求
        
        Args:
            file_path: 文件路径
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 构建消息
            message = f"请帮我修改以下文件：\n\n文件路径: {file_path}\n\n当前内容:\n{content}\n\n请告诉我你想如何修改这个文件。"
            
            # 发送消息
            self.on_send_message(message)
            
            logger.info(f"AI 修改文件: {file_path}")
            
        except Exception as e:
            logger.error(f"AI 修改文件失败: {e}", exc_info=True)
            self.error_occurred.emit(f"读取文件失败: {e}")
    
    def load_sessions_list(self) -> None:
        """加载会话列表"""
        self._refresh_sessions_list()
    
    def _refresh_sessions_list(self) -> None:
        """刷新会话列表"""
        try:
            sessions = self.session_manager.list_sessions()
            self.sessions_list_updated.emit(sessions)
            logger.debug(f"会话列表已刷新: {len(sessions)} 个会话")
        except Exception as e:
            logger.error(f"刷新会话列表失败: {e}", exc_info=True)
    
    def get_active_model_name(self) -> str:
        """
        获取当前激活的模型名称
        
        Returns:
            str: 模型名称
        """
        active_model = self.model_config_manager.get_active_model()
        if active_model:
            return active_model.name
        return "未配置"
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止工作线程
            if self.current_worker and self.current_worker.isRunning():
                self.current_worker.stop()
            
            # 保存当前会话
            current_session = self.session_manager.get_current_session()
            if current_session:
                self.session_manager.save_session(current_session)
            
            logger.info("ApplicationController 清理完成")
            
        except Exception as e:
            logger.error(f"清理资源失败: {e}", exc_info=True)
