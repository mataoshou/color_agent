"""
LangChain Agent 模块

包含 Agent 执行器和 Prompt 模板。
"""

from .prompts import AgentPromptTemplate
from .agent_executor import AgentExecutorManager, StreamingCallbackHandler

__all__ = [
    'AgentPromptTemplate',
    'AgentExecutorManager',
    'StreamingCallbackHandler'
]
