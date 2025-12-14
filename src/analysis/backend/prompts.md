# backend/agent/prompts.py 分析文档

## 1. 文件概述
- 文件路径：d:\core\color\color_agent\src\backend\agent\prompts.py
- 所属模块：Backend.Agent
- 主要功能：提供 Agent 提示词模板管理和消息生成功能

## 2. 核心实现

### 2.1 AgentPromptTemplate 类
- **功能**：管理 Agent 的系统消息模板和各种消息生成方法
- **核心属性**：
  - `SYSTEM_MESSAGE_TEMPLATE`：系统消息模板字符串，定义了 Agent 的角色、系统上下文和可用工具
- **关键方法**：
  - `create_system_message()`：根据系统上下文创建系统消息对象
  - `create_system_message_template()`：创建系统消息模板对象
  - `get_tool_descriptions()`：获取工具描述文本
  - `create_user_message_with_context()`：创建包含额外上下文的用户消息
  - `create_file_context_message()`：创建文件上下文消息
  - `create_error_message()`：创建错误消息

## 3. 与其他模块的关系
- **依赖模块**：
  - `langchain_core.prompts`：提供 SystemMessagePromptTemplate 和 ChatPromptTemplate 类
  - `langchain_core.messages`：提供 SystemMessage 类
- **被依赖情况**：被 `agent_executor.py` 依赖，用于生成系统消息
- **交互方式**：
  - 通过静态方法提供各种消息生成功能
  - 与 AgentExecutorManager 交互，提供系统上下文和工具描述

## 4. 代码结构
```python
"""
LangChain Prompt 模板

提供系统消息模板和工具使用说明。
"""

from langchain_core.prompts import SystemMessagePromptTemplate, ChatPromptTemplate
from langchain_core.messages import SystemMessage
from typing import Dict, Any

class AgentPromptTemplate:
    """Agent Prompt 模板管理器"""
    
    # 系统消息模板
    SYSTEM_MESSAGE_TEMPLATE = """你是一个智能助手，可以帮助用户完成各种任务。

系统上下文信息：
- 当前工作目录: {working_directory}
- 操作系统: {os_type} {os_version}
- Python 版本: {python_version}

你可以使用以下工具来帮助用户：

1. read_file - 读取文件内容
   - 用途：读取指定文件的完整内容
   - 输入：文件路径（相对或绝对路径）
   - 示例：read_file("README.md")

2. write_file - 创建或覆盖文件
   - 用途：创建新文件或覆盖现有文件
   - 输入：文件路径和要写入的内容
   - 示例：write_file(file_path="output.txt", content="Hello World")

3. modify_file - 修改文件内容
   - 用途：替换文件中的特定内容
   - 输入：文件路径、要替换的旧内容、替换后的新内容
   - 示例：modify_file(file_path="config.py", old_content="DEBUG = False", new_content="DEBUG = True")

4. list_files - 列出目录文件
   - 用途：列出指定目录下的所有文件和子目录
   - 输入：目录路径（默认为当前工作目录）
   - 示例：list_files(".") 或 list_files("src")

工具使用规则：
- 所有文件路径都相对于当前工作目录
- 只能访问工作目录内的文件
- 支持的文件格式：.txt, .md, .py, .js, .json, .yaml, .yml, .html, .css, .xml, .csv, .log, .sh, .bat
- 单个文件大小限制：10MB
- 在执行文件操作前，建议先使用 list_files 查看目录结构
- 在修改文件前，建议先使用 read_file 读取文件内容

请根据用户的需求，合理使用这些工具来完成任务。如果需要操作文件，请主动调用相应的工具。"""
    
    @staticmethod
    def create_system_message(system_context: Dict[str, Any]) -> SystemMessage:
        # 方法实现...
        
    @staticmethod
    def create_system_message_template() -> SystemMessagePromptTemplate:
        # 方法实现...
        
    @staticmethod
    def get_tool_descriptions() -> str:
        # 方法实现...
        
    @staticmethod
    def create_user_message_with_context(user_message: str, 
                                        additional_context: str = "") -> str:
        # 方法实现...
        
    @staticmethod
    def create_file_context_message(file_path: str, content: str) -> str:
        # 方法实现...
        
    @staticmethod
    def create_error_message(error: str) -> str:
        # 方法实现...
```

## 5. 潜在问题或改进点
- **模板灵活性**：当前系统消息模板是固定的，可以考虑支持更灵活的模板配置
- **多语言支持**：可以考虑添加多语言模板支持
- **模板版本控制**：可以考虑添加模板版本控制机制，便于管理和更新
- **工具描述维护**：当前工具描述存在重复（SYSTEM_MESSAGE_TEMPLATE 和 get_tool_descriptions()），可以考虑统一维护

## 6. 总结
该文件是 Color Agent 项目的提示词模板管理器，定义了 AgentPromptTemplate 类用于管理系统消息模板和各种消息生成功能。它提供了系统消息模板、工具使用说明以及多种消息生成方法，是 Agent 能够理解自身角色和可用工具的关键组件。该模块与 Agent 执行器紧密配合，确保 Agent 能够正确理解和响应用户请求。