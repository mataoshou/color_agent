"""
LangChain Agent 执行器

管理 Agent 的初始化、工具注册和执行。
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.tools import BaseTool
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from ..tools import ReadFileTool, WriteFileTool, ModifyFileTool, ListFilesTool
from .prompts import AgentPromptTemplate


logger = logging.getLogger(__name__)


class StreamingCallbackHandler(BaseCallbackHandler):
    """流式响应回调处理器"""
    
    def __init__(self, on_llm_new_token: Optional[Callable[[str], None]] = None,
                 on_tool_start: Optional[Callable[[str, str], None]] = None,
                 on_tool_end: Optional[Callable[[str, str], None]] = None):
        """
        初始化回调处理器
        
        Args:
            on_llm_new_token: LLM 生成新 token 时的回调函数
            on_tool_start: 工具开始执行时的回调函数
            on_tool_end: 工具执行完成时的回调函数
        """
        self.on_llm_new_token_callback = on_llm_new_token
        self.on_tool_start_callback = on_tool_start
        self.on_tool_end_callback = on_tool_end
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """LLM 生成新 token 时调用"""
        if self.on_llm_new_token_callback:
            self.on_llm_new_token_callback(token)
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """工具开始执行时调用"""
        if self.on_tool_start_callback:
            tool_name = serialized.get("name", "unknown")
            self.on_tool_start_callback(tool_name, input_str)
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """工具执行完成时调用"""
        if self.on_tool_end_callback:
            self.on_tool_end_callback("tool", output)


class AgentExecutorManager:
    """Agent 执行器管理器"""
    
    def __init__(self, api_base: str, api_key: str, model_name: str,
                 working_directory: str, system_context: Dict[str, Any],
                 temperature: float = 0.7, max_tokens: int = 2048,
                 streaming: bool = True, verbose: bool = False):
        """
        初始化 Agent 执行器管理器
        
        Args:
            api_base: API 端点 URL
            api_key: API 密钥
            model_name: 模型名称
            working_directory: 工作目录
            system_context: 系统上下文信息
            temperature: 温度参数
            max_tokens: 最大 token 数
            streaming: 是否启用流式响应
            verbose: 是否显示详细日志
        """
        self.api_base = api_base
        self.api_key = api_key
        self.model_name = model_name
        self.working_directory = working_directory
        self.system_context = system_context
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming
        self.verbose = verbose
        
        # 初始化组件
        self.llm: Optional[ChatOpenAI] = None
        self.tools: List[BaseTool] = []
        self.chat_history: Optional[InMemoryChatMessageHistory] = None
        self.callback_handler: Optional[StreamingCallbackHandler] = None
        
        logger.info(f"初始化 AgentExecutorManager: model={model_name}, working_dir={working_directory}")
    
    def initialize(self, on_llm_new_token: Optional[Callable[[str], None]] = None,
                   on_tool_start: Optional[Callable[[str, str], None]] = None,
                   on_tool_end: Optional[Callable[[str, str], None]] = None) -> None:
        """
        初始化 Agent 执行器
        
        Args:
            on_llm_new_token: LLM 生成新 token 时的回调函数
            on_tool_start: 工具开始执行时的回调函数
            on_tool_end: 工具执行完成时的回调函数
        """
        try:
            # 创建回调处理器
            self.callback_handler = StreamingCallbackHandler(
                on_llm_new_token=on_llm_new_token,
                on_tool_start=on_tool_start,
                on_tool_end=on_tool_end
            )
            
            # 创建 ChatOpenAI 实例
            self.llm = ChatOpenAI(
                base_url=self.api_base,
                api_key=self.api_key,
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                streaming=self.streaming,
                callbacks=[self.callback_handler] if self.streaming else None
            )
            
            logger.info(f"ChatOpenAI 实例已创建: {self.model_name}")
            
            # 创建工具
            self._create_tools()
            
            # 绑定工具到 LLM
            self.llm = self.llm.bind_tools(self.tools)
            
            # 创建聊天历史
            self.chat_history = InMemoryChatMessageHistory()
            
            logger.info("聊天历史已创建")
            logger.info("Agent 执行器初始化完成")
            
        except Exception as e:
            logger.error(f"初始化 Agent 执行器失败: {e}", exc_info=True)
            raise
    
    def _create_tools(self) -> None:
        """创建并注册工具"""
        try:
            # 创建文件操作工具
            self.tools = [
                ReadFileTool(working_directory=self.working_directory),
                WriteFileTool(working_directory=self.working_directory),
                ModifyFileTool(working_directory=self.working_directory),
                ListFilesTool(working_directory=self.working_directory)
            ]
            
            logger.info(f"已注册 {len(self.tools)} 个工具: {[tool.name for tool in self.tools]}")
            
        except Exception as e:
            logger.error(f"创建工具失败: {e}", exc_info=True)
            raise
    
    def _build_messages(self, user_input: str) -> List[Any]:
        """
        构建消息列表
        
        Args:
            user_input: 用户输入
            
        Returns:
            List: 消息列表
        """
        messages = []
        
        # 添加系统消息
        system_message = AgentPromptTemplate.create_system_message(self.system_context)
        messages.append(system_message)
        
        # 添加历史消息
        if self.chat_history:
            history = self.chat_history.messages
            messages.extend(history)
        
        # 添加用户消息
        messages.append(HumanMessage(content=user_input))
        
        return messages
    
    def run(self, user_input: str) -> Dict[str, Any]:
        """
        执行用户输入
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            Dict: 执行结果，包含 output
        """
        if not self.llm:
            raise RuntimeError("Agent 执行器未初始化，请先调用 initialize()")
        
        try:
            logger.info(f"执行用户输入: {user_input[:100]}...")
            
            # 构建初始消息
            messages = self._build_messages(user_input)
            
            # 保存用户输入到聊天历史
            if self.chat_history:
                self.chat_history.add_user_message(user_input)
            
            # 主循环：持续处理模型响应直到没有工具调用
            final_output = ""
            has_pending_tool_calls = True
            
            while has_pending_tool_calls:
                # 调用 LLM
                logger.info("调用 LLM 获取响应")
                response = self.llm.invoke(messages)
                
                # 记录模型思考过程
                logger.debug(f"LLM 响应结构: {type(response).__name__}")
                logger.debug(f"LLM 响应内容: {response}")
                
                # 将LLM响应添加到消息列表中，这样后续的ToolMessage就有了正确的前驱
                messages.append(response)
                
                # 检查是否有工具调用
                tool_calls = getattr(response, 'tool_calls', [])
                has_pending_tool_calls = len(tool_calls) > 0
                
                if has_pending_tool_calls:
                    logger.info(f"检测到 {len(tool_calls)} 个工具调用")
                    
                    # 处理每个工具调用
                    for tool_call in tool_calls:
                        tool_name = tool_call.get('name', '')
                        tool_args = tool_call.get('args', {})
                        
                        # 查找并执行工具
                        for tool in self.tools:
                            if tool.name == tool_name:
                                logger.info(f"执行工具: {tool_name}")
                                tool_result = tool._run(**tool_args)
                                logger.info(f"工具结果: {tool_result[:100]}...")
                                
                                # 获取工具调用的ID
                                tool_call_id = tool_call.get('id', '')
                                
                                # 将工具结果作为ToolMessage添加到消息列表
                                messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call_id))
                                
                                # 如果启用了聊天历史，添加工具调用和结果
                                if self.chat_history:
                                    self.chat_history.add_ai_message(response.content)
                                    self.chat_history.add_message(ToolMessage(content=tool_result, tool_call_id=tool_call_id))
                                
                                break
                else:
                    # 没有工具调用，保存最终输出
                    final_output = response.content
                    logger.info("没有更多工具调用，完成处理")
            
            # 保存最终回复到聊天历史
            if self.chat_history and final_output:
                self.chat_history.add_ai_message(final_output)
            
            # 记录模型最终输出
            logger.info(f"模型最终输出: {final_output}")
            logger.info("Agent 执行完成")
            
            return {"output": final_output}
            
        except Exception as e:
            logger.error(f"执行 Agent 失败: {e}", exc_info=True)
            raise
    
    async def arun(self, user_input: str) -> Dict[str, Any]:
        """
        异步执行用户输入
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            Dict: 执行结果，包含 output
        """
        if not self.llm:
            raise RuntimeError("Agent 执行器未初始化，请先调用 initialize()")
        
        try:
            logger.info(f"异步执行用户输入: {user_input[:100]}...")
            
            # 构建初始消息
            messages = self._build_messages(user_input)
            
            # 保存用户输入到聊天历史
            if self.chat_history:
                self.chat_history.add_user_message(user_input)
            
            # 主循环：持续处理模型响应直到没有工具调用
            final_output = ""
            has_pending_tool_calls = True
            
            while has_pending_tool_calls:
                # 异步调用 LLM
                logger.info("异步调用 LLM 获取响应")
                response = await self.llm.ainvoke(messages)
                
                # 记录模型思考过程
                logger.debug(f"LLM 异步响应结构: {type(response).__name__}")
                logger.debug(f"LLM 异步响应内容: {response}")
                
                # 将LLM响应添加到消息列表中，这样后续的ToolMessage就有了正确的前驱
                messages.append(response)
                
                # 检查是否有工具调用
                tool_calls = getattr(response, 'tool_calls', [])
                has_pending_tool_calls = len(tool_calls) > 0
                
                if has_pending_tool_calls:
                    logger.info(f"检测到 {len(tool_calls)} 个工具调用")
                    
                    # 处理每个工具调用
                    for tool_call in tool_calls:
                        tool_name = tool_call.get('name', '')
                        tool_args = tool_call.get('args', {})
                        
                        # 查找并执行工具
                        for tool in self.tools:
                            if tool.name == tool_name:
                                logger.info(f"执行工具: {tool_name}")
                                tool_result = tool._run(**tool_args)
                                logger.info(f"工具结果: {tool_result[:100]}...")
                                
                                # 获取工具调用的ID
                                tool_call_id = tool_call.get('id', '')
                                
                                # 将工具结果作为ToolMessage添加到消息列表
                                messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call_id))
                                
                                # 如果启用了聊天历史，添加工具调用和结果
                                if self.chat_history:
                                    self.chat_history.add_ai_message(response.content)
                                    self.chat_history.add_message(ToolMessage(content=tool_result, tool_call_id=tool_call_id))
                                
                                break
                else:
                    # 没有工具调用，保存最终输出
                    final_output = response.content
                    logger.info("没有更多工具调用，完成处理")
            
            # 保存最终回复到聊天历史
            if self.chat_history and final_output:
                self.chat_history.add_ai_message(final_output)
            
            # 记录模型最终输出
            logger.info(f"模型最终输出: {final_output}")
            logger.info("Agent 异步执行完成")
            
            return {"output": final_output}
            
        except Exception as e:
            logger.error(f"异步执行 Agent 失败: {e}", exc_info=True)
            raise
    
    def update_system_context(self, system_context: Dict[str, Any]) -> None:
        """
        更新系统上下文
        
        Args:
            system_context: 新的系统上下文信息
        """
        self.system_context = system_context
        logger.info(f"系统上下文已更新: {system_context}")
        
        # 系统上下文将在下次调用时使用
    
    def update_working_directory(self, working_directory: str) -> None:
        """
        更新工作目录
        
        Args:
            working_directory: 新的工作目录
        """
        self.working_directory = working_directory
        self.system_context['working_directory'] = working_directory
        logger.info(f"工作目录已更新: {working_directory}")
        
        # 重新创建工具
        if self.llm:
            self._create_tools()
            self.llm = self.llm.bind_tools(self.tools)
    
    def clear_memory(self) -> None:
        """清空对话记忆"""
        if self.chat_history:
            self.chat_history.clear()
            logger.info("对话记忆已清空")
    
    def get_memory_messages(self) -> List[Any]:
        """
        获取记忆中的消息
        
        Returns:
            List: 消息列表
        """
        if self.chat_history:
            return self.chat_history.messages
        return []
    
    def load_memory_from_messages(self, messages: List[Dict[str, str]]) -> None:
        """
        从消息列表加载记忆
        
        Args:
            messages: 消息列表，每个消息包含 role 和 content
        """
        if not self.chat_history:
            return
        
        # 清空现有记忆
        self.chat_history.clear()
        
        # 加载消息
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'user':
                self.chat_history.add_user_message(content)
            elif role == 'assistant':
                self.chat_history.add_ai_message(content)
        
        logger.info(f"已加载 {len(messages)} 条消息到记忆")
    
    def shutdown(self) -> None:
        """关闭 Agent 执行器"""
        logger.info("关闭 Agent 执行器")
        self.llm = None
        self.tools = []
        self.chat_history = None
