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
        """
        创建系统消息
        
        Args:
            system_context: 系统上下文信息字典，包含：
                - working_directory: 工作目录
                - os_type: 操作系统类型
                - os_version: 操作系统版本
                - python_version: Python 版本
        
        Returns:
            SystemMessage: 系统消息对象
        """
        # 格式化系统消息
        content = AgentPromptTemplate.SYSTEM_MESSAGE_TEMPLATE.format(
            working_directory=system_context.get('working_directory', '.'),
            os_type=system_context.get('os_type', 'Unknown'),
            os_version=system_context.get('os_version', 'Unknown'),
            python_version=system_context.get('python_version', 'Unknown')
        )
        
        return SystemMessage(content=content)
    
    @staticmethod
    def create_system_message_template() -> SystemMessagePromptTemplate:
        """
        创建系统消息模板
        
        Returns:
            SystemMessagePromptTemplate: 系统消息模板对象
        """
        return SystemMessagePromptTemplate.from_template(
            AgentPromptTemplate.SYSTEM_MESSAGE_TEMPLATE
        )
    
    @staticmethod
    def get_tool_descriptions() -> str:
        """
        获取工具描述文本
        
        Returns:
            str: 工具描述文本
        """
        return """可用工具：

1. read_file - 读取文件内容
   读取指定文件的完整内容。适用于查看文件内容、分析代码等场景。

2. write_file - 创建或覆盖文件
   创建新文件或完全覆盖现有文件。适用于生成新文件、重写配置等场景。

3. modify_file - 修改文件内容
   替换文件中的特定内容。适用于更新配置、修改代码片段等场景。

4. list_files - 列出目录文件
   列出指定目录下的所有文件和子目录。适用于浏览项目结构、查找文件等场景。"""
    
    @staticmethod
    def create_user_message_with_context(user_message: str, 
                                        additional_context: str = "") -> str:
        """
        创建包含额外上下文的用户消息
        
        Args:
            user_message: 用户原始消息
            additional_context: 额外的上下文信息
        
        Returns:
            str: 格式化后的用户消息
        """
        if additional_context:
            return f"{additional_context}\n\n用户消息：{user_message}"
        return user_message
    
    @staticmethod
    def create_file_context_message(file_path: str, content: str) -> str:
        """
        创建文件上下文消息
        
        Args:
            file_path: 文件路径
            content: 文件内容
        
        Returns:
            str: 格式化的文件上下文消息
        """
        return f"""文件 '{file_path}' 的内容：

```
{content}
```

请根据上述文件内容回答用户的问题或执行用户的请求。"""
    
    @staticmethod
    def create_error_message(error: str) -> str:
        """
        创建错误消息
        
        Args:
            error: 错误信息
        
        Returns:
            str: 格式化的错误消息
        """
        return f"抱歉，执行过程中遇到了错误：{error}\n\n请检查输入并重试，或者换一种方式描述您的需求。"
