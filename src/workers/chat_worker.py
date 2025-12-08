"""
聊天工作线程

使用 QThread 处理 Agent 消息，避免阻塞 UI。
"""

import logging
import time
from typing import Dict, Any, Optional
from PyQt6.QtCore import QThread, pyqtSignal

from ..backend.agent import AgentExecutorManager


logger = logging.getLogger(__name__)


class ChatWorker(QThread):
    """聊天工作线程"""
    
    # 信号定义
    message_chunk = pyqtSignal(str)  # 流式响应的文本块
    message_complete = pyqtSignal(str)  # 消息生成完成
    tool_call_started = pyqtSignal(str, str)  # 工具调用开始 (工具名, 参数)
    tool_call_finished = pyqtSignal(str, str)  # 工具调用完成 (工具名, 结果)
    error_occurred = pyqtSignal(str)  # 错误发生
    
    def __init__(self, agent_manager: AgentExecutorManager, user_input: str,
                 max_retries: int = 2):
        """
        初始化聊天工作线程
        
        Args:
            agent_manager: Agent 执行器管理器
            user_input: 用户输入文本
            max_retries: 最大重试次数
        """
        super().__init__()
        self.agent_manager = agent_manager
        self.user_input = user_input
        self.max_retries = max_retries
        self._is_running = True
        
        logger.info(f"ChatWorker 已创建: user_input={user_input[:50]}...")
    
    def run(self) -> None:
        """执行线程任务"""
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries and self._is_running:
            try:
                logger.info(f"开始处理消息 (尝试 {retry_count + 1}/{self.max_retries + 1})")
                
                # 设置回调函数
                if self.agent_manager.callback_handler:
                    self.agent_manager.callback_handler.on_llm_new_token_callback = self._on_token
                    self.agent_manager.callback_handler.on_tool_start_callback = self._on_tool_start
                    self.agent_manager.callback_handler.on_tool_end_callback = self._on_tool_end
                    logger.debug("已设置回调函数")
                else:
                    logger.warning("callback_handler 不存在")
                
                # 执行 Agent
                result = self.agent_manager.run(self.user_input)
                
                # 获取输出
                output = result.get('output', '')
                logger.info(f"Agent 执行完成，输出长度: {len(output)}")
                
                # 发送完成信号
                if self._is_running:
                    self.message_complete.emit(output)
                    logger.info("已发送 message_complete 信号")
                
                return
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"处理消息失败 (尝试 {retry_count + 1}/{self.max_retries + 1}): {e}", 
                           exc_info=True)
                
                retry_count += 1
                
                # 如果还有重试机会，等待一段时间后重试
                if retry_count <= self.max_retries and self._is_running:
                    wait_time = retry_count * 2  # 递增等待时间
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
        
        # 所有重试都失败，发送错误信号
        if self._is_running:
            error_msg = f"处理消息失败（已重试 {self.max_retries} 次）: {last_error}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
    
    def _on_token(self, token: str) -> None:
        """
        LLM 生成新 token 时的回调
        
        Args:
            token: 新生成的 token
        """
        if self._is_running:
            self.message_chunk.emit(token)
    
    def _on_tool_start(self, tool_name: str, input_str: str) -> None:
        """
        工具开始执行时的回调
        
        Args:
            tool_name: 工具名称
            input_str: 工具输入参数
        """
        if self._is_running:
            logger.info(f"工具调用开始: {tool_name}")
            self.tool_call_started.emit(tool_name, input_str)
    
    def _on_tool_end(self, tool_name: str, output: str) -> None:
        """
        工具执行完成时的回调
        
        Args:
            tool_name: 工具名称
            output: 工具输出结果
        """
        if self._is_running:
            logger.info(f"工具调用完成: {tool_name}")
            self.tool_call_finished.emit(tool_name, output)
    
    def stop(self) -> None:
        """停止线程"""
        logger.info("停止 ChatWorker")
        self._is_running = False
        self.quit()
        self.wait()


class ChatWorkerFactory:
    """聊天工作线程工厂"""
    
    @staticmethod
    def create_worker(agent_manager: AgentExecutorManager, user_input: str,
                     max_retries: int = 2) -> ChatWorker:
        """
        创建聊天工作线程
        
        Args:
            agent_manager: Agent 执行器管理器
            user_input: 用户输入文本
            max_retries: 最大重试次数
        
        Returns:
            ChatWorker: 聊天工作线程实例
        """
        return ChatWorker(agent_manager, user_input, max_retries)
